"""D1-backed social account repository.

This is the Cloudflare counterpart to SocialAccountManager. It intentionally
uses async methods and a D1 binding; the existing SQLite manager remains the
local Windows implementation until the application wiring is migrated.
"""
import json

from social_account_manager import (
    DEFAULT_FORMATS,
    MAX_ACCOUNTS_PER_PLATFORM,
    SUPPORTED_PLATFORMS,
)


class D1SocialAccountRepository:
    def __init__(self, store):
        self.store = store

    @staticmethod
    def normalize_platform(platform):
        value = platform.strip().lower()
        return "facebook_profile" if value == "facebook" else value

    async def add_account(self, platform, account_name, account_handle):
        platform = self.normalize_platform(platform)
        account_name = account_name.strip()
        account_handle = account_handle.strip()
        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError("Unsupported platform.")
        if not account_name or not account_handle:
            raise ValueError("Account name and handle are required.")

        count_row = await self.store.one(
            "SELECT COUNT(*) AS account_count FROM social_accounts WHERE platform = ?",
            platform,
        )
        if int(count_row["account_count"]) >= MAX_ACCOUNTS_PER_PLATFORM:
            raise OverflowError(
                f"{platform} already has the maximum of "
                f"{MAX_ACCOUNTS_PER_PLATFORM} account slots."
            )

        try:
            await self.store.execute(
                """INSERT INTO social_accounts
                   (platform, account_name, account_handle, status)
                   VALUES (?, ?, ?, 'not_connected')""",
                platform, account_name, account_handle,
            )
        except Exception as error:
            # D1 raises a runtime exception for the UNIQUE(platform, handle)
            # constraint. Do not hide unrelated storage failures.
            message = str(error).lower()
            if "unique" in message or "constraint" in message:
                raise ValueError("This account handle is already registered.") from error
            raise

        account = await self.store.one(
            "SELECT * FROM social_accounts WHERE platform = ? AND account_handle = ?",
            platform, account_handle,
        )
        await self.store.execute(
            "INSERT OR IGNORE INTO social_account_preferences (account_id) VALUES (?)",
            account["id"],
        )
        return account

    async def list_accounts(self, platform=None):
        if platform:
            platform = self.normalize_platform(platform)
            if platform not in SUPPORTED_PLATFORMS:
                raise ValueError("Unsupported platform.")
            return await self.store.all(
                "SELECT * FROM social_accounts WHERE platform = ? ORDER BY id",
                platform,
            )
        return await self.store.all(
            "SELECT * FROM social_accounts ORDER BY platform, id"
        )

    async def account_limits(self):
        rows = await self.store.all(
            "SELECT platform, COUNT(*) AS used FROM social_accounts GROUP BY platform"
        )
        counts = {row["platform"]: int(row["used"]) for row in rows}
        return {
            platform: {
                "used": counts.get(platform, 0),
                "limit": MAX_ACCOUNTS_PER_PLATFORM,
                "available": MAX_ACCOUNTS_PER_PLATFORM - counts.get(platform, 0),
            }
            for platform in sorted(SUPPORTED_PLATFORMS)
        }

    async def get_preferences(self, account_id):
        row = await self.store.one(
            """SELECT a.id, a.platform, a.account_name, a.account_handle, a.status,
                      p.niche, p.content_formats, p.publishing_enabled,
                      p.require_approval, p.updated_at
               FROM social_accounts a
               LEFT JOIN social_account_preferences p ON p.account_id = a.id
               WHERE a.id = ?""",
            account_id,
        )
        if row is None:
            return None
        row["content_formats"] = json.loads(
            row.get("content_formats") or json.dumps(DEFAULT_FORMATS)
        )
        row["publishing_enabled"] = bool(row.get("publishing_enabled", 0))
        row["require_approval"] = bool(row.get("require_approval", 1))
        row["niche"] = row.get("niche") or ""
        return row

    async def update_preferences(self, account_id, changes):
        current = await self.get_preferences(account_id)
        if current is None:
            return None

        allowed_formats = {"post", "video", "reel", "story", "short", "article"}
        niche = changes.get("niche", current["niche"])
        formats = changes.get("content_formats", current["content_formats"])
        enabled = changes.get("publishing_enabled", current["publishing_enabled"])
        approval = changes.get("require_approval", current["require_approval"])
        if niche is not None and len(niche) > 160:
            raise ValueError("Niche must be 160 characters or fewer.")
        if not isinstance(formats, list) or not formats:
            raise ValueError("Select at least one content format.")
        if any(item not in allowed_formats for item in formats):
            raise ValueError("Unsupported content format.")

        await self.store.execute(
            """INSERT OR IGNORE INTO social_account_preferences (account_id)
               VALUES (?)""",
            account_id,
        )
        await self.store.execute(
            """UPDATE social_account_preferences
               SET niche = ?, content_formats = ?, publishing_enabled = ?,
                   require_approval = ?, updated_at = CURRENT_TIMESTAMP
               WHERE account_id = ?""",
            niche or "", json.dumps(formats), int(bool(enabled)),
            int(bool(approval)), account_id,
        )
        return await self.get_preferences(account_id)

    async def get_owner_controls(self):
        rows = await self.store.all(
            "SELECT setting_key, setting_value FROM owner_control_settings"
        )
        values = {row["setting_key"]: row["setting_value"] for row in rows}
        return {
            "global_publishing_enabled": values.get(
                "global_publishing_enabled", "false"
            ).lower() == "true",
            "require_approval": values.get("require_approval", "true").lower() == "true",
            "owner_has_final_control": True,
        }

    async def update_owner_controls(
        self, global_publishing_enabled=None, require_approval=None
    ):
        updates = []
        if global_publishing_enabled is not None:
            updates.append((
                """INSERT INTO owner_control_settings (setting_key, setting_value)
                   VALUES ('global_publishing_enabled', ?)
                   ON CONFLICT(setting_key) DO UPDATE
                   SET setting_value=excluded.setting_value""",
                (str(bool(global_publishing_enabled)).lower(),),
            ))
        if require_approval is not None:
            updates.append((
                """INSERT INTO owner_control_settings (setting_key, setting_value)
                   VALUES ('require_approval', ?)
                   ON CONFLICT(setting_key) DO UPDATE
                   SET setting_value=excluded.setting_value""",
                (str(bool(require_approval)).lower(),),
            ))
        if updates:
            await self.store.batch(updates)
        return await self.get_owner_controls()

    async def remove_account(self, account_id):
        result = await self.store.execute(
            "DELETE FROM social_accounts WHERE id = ?", account_id
        )
        return int(result.get("changes", 0)) > 0
