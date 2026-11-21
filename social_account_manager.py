import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent / "asfandyar.db"

SUPPORTED_PLATFORMS = {
    "facebook", "instagram", "x", "youtube",
    "linkedin", "tiktok", "pinterest"
}
MAX_ACCOUNTS_PER_PLATFORM = 5
DEFAULT_FORMATS = ["post"]


class SocialAccountManager:
    """SQLite registry and owner-controlled preferences for social accounts.

    Account slots are not authenticated provider connections. OAuth tokens
    must be obtained via official provider flows and encrypted at rest.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path, timeout=15)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA busy_timeout = 15000")
            connection.execute("PRAGMA foreign_keys = ON")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self):
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS social_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    account_name TEXT NOT NULL,
                    account_handle TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'not_connected',
                    provider_account_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, account_handle)
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS social_account_preferences (
                    account_id INTEGER PRIMARY KEY,
                    niche TEXT NOT NULL DEFAULT '',
                    content_formats TEXT NOT NULL DEFAULT '["post"]',
                    publishing_enabled INTEGER NOT NULL DEFAULT 0,
                    require_approval INTEGER NOT NULL DEFAULT 1,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(account_id) REFERENCES social_accounts(id)
                        ON DELETE CASCADE
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS owner_control_settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT NOT NULL
                )
            """)
            connection.execute("""
                INSERT OR IGNORE INTO owner_control_settings
                (setting_key, setting_value) VALUES
                ('global_publishing_enabled', 'false'),
                ('require_approval', 'true')
            """)

    def add_account(self, platform, account_name, account_handle):
        platform = platform.strip().lower()
        account_name = account_name.strip()
        account_handle = account_handle.strip()
        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError("Unsupported platform.")
        if not account_name or not account_handle:
            raise ValueError("Account name and handle are required.")

        with self.connect() as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM social_accounts WHERE platform = ?",
                (platform,)
            ).fetchone()[0]
            if count >= MAX_ACCOUNTS_PER_PLATFORM:
                raise OverflowError(
                    f"{platform} already has the maximum of "
                    f"{MAX_ACCOUNTS_PER_PLATFORM} account slots."
                )
            try:
                cursor = connection.execute("""
                    INSERT INTO social_accounts
                    (platform, account_name, account_handle, status)
                    VALUES (?, ?, ?, 'not_connected')
                """, (platform, account_name, account_handle))
            except sqlite3.IntegrityError:
                raise ValueError("This account handle is already registered.")
            account_id = cursor.lastrowid
            connection.execute(
                "INSERT OR IGNORE INTO social_account_preferences (account_id) VALUES (?)",
                (account_id,)
            )
            row = connection.execute(
                "SELECT * FROM social_accounts WHERE id = ?", (account_id,)
            ).fetchone()
            return dict(row)

    def list_accounts(self, platform=None):
        with self.connect() as connection:
            if platform:
                platform = platform.strip().lower()
                if platform not in SUPPORTED_PLATFORMS:
                    raise ValueError("Unsupported platform.")
                rows = connection.execute(
                    "SELECT * FROM social_accounts WHERE platform = ? ORDER BY id",
                    (platform,)
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM social_accounts ORDER BY platform, id"
                ).fetchall()
            return [dict(row) for row in rows]

    def account_limits(self):
        accounts = self.list_accounts()
        return {
            platform: {
                "used": sum(1 for item in accounts if item["platform"] == platform),
                "limit": MAX_ACCOUNTS_PER_PLATFORM,
                "available": MAX_ACCOUNTS_PER_PLATFORM - sum(
                    1 for item in accounts if item["platform"] == platform
                ),
            }
            for platform in sorted(SUPPORTED_PLATFORMS)
        }

    def get_preferences(self, account_id):
        with self.connect() as connection:
            account = connection.execute(
                "SELECT id, platform, account_name, account_handle, status "
                "FROM social_accounts WHERE id = ?", (account_id,)
            ).fetchone()
            if not account:
                return None
            connection.execute(
                "INSERT OR IGNORE INTO social_account_preferences (account_id) VALUES (?)",
                (account_id,)
            )
            prefs = connection.execute(
                "SELECT * FROM social_account_preferences WHERE account_id = ?",
                (account_id,)
            ).fetchone()
            result = dict(account)
            result.update(dict(prefs))
            result["content_formats"] = json.loads(result["content_formats"])
            result["publishing_enabled"] = bool(result["publishing_enabled"])
            result["require_approval"] = bool(result["require_approval"])
            return result

    def update_preferences(self, account_id, changes):
        allowed_formats = {"post", "video", "reel", "story", "short", "article"}
        with self.connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM social_accounts WHERE id = ?", (account_id,)
            ).fetchone()
            if not exists:
                return None
            connection.execute(
                "INSERT OR IGNORE INTO social_account_preferences (account_id) VALUES (?)",
                (account_id,)
            )
            current = connection.execute(
                "SELECT * FROM social_account_preferences WHERE account_id = ?",
                (account_id,)
            ).fetchone()
            niche = changes.get("niche", current["niche"])
            formats = changes.get(
                "content_formats", json.loads(current["content_formats"])
            )
            enabled = changes.get(
                "publishing_enabled", bool(current["publishing_enabled"])
            )
            approval = changes.get(
                "require_approval", bool(current["require_approval"])
            )
            if niche is not None and len(niche) > 160:
                raise ValueError("Niche must be 160 characters or fewer.")
            if not isinstance(formats, list) or not formats:
                raise ValueError("Select at least one content format.")
            if any(item not in allowed_formats for item in formats):
                raise ValueError("Unsupported content format.")
            connection.execute("""
                UPDATE social_account_preferences
                SET niche = ?, content_formats = ?, publishing_enabled = ?,
                    require_approval = ?, updated_at = CURRENT_TIMESTAMP
                WHERE account_id = ?
            """, (niche or "", json.dumps(formats), int(enabled), int(approval), account_id))
        return self.get_preferences(account_id)

    def get_owner_controls(self):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT setting_key, setting_value FROM owner_control_settings"
            ).fetchall()
            values = {row["setting_key"]: row["setting_value"] for row in rows}
            return {
                "global_publishing_enabled": values.get(
                    "global_publishing_enabled", "false"
                ).lower() == "true",
                "require_approval": values.get("require_approval", "true").lower() == "true",
                "owner_has_final_control": True,
            }

    def update_owner_controls(self, global_publishing_enabled=None, require_approval=None):
        with self.connect() as connection:
            if global_publishing_enabled is not None:
                connection.execute("""
                    INSERT INTO owner_control_settings (setting_key, setting_value)
                    VALUES ('global_publishing_enabled', ?)
                    ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value
                """, (str(bool(global_publishing_enabled)).lower(),))
            if require_approval is not None:
                connection.execute("""
                    INSERT INTO owner_control_settings (setting_key, setting_value)
                    VALUES ('require_approval', ?)
                    ON CONFLICT(setting_key) DO UPDATE SET setting_value=excluded.setting_value
                """, (str(bool(require_approval)).lower(),))
        return self.get_owner_controls()

    def remove_account(self, account_id):
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM social_accounts WHERE id = ?", (account_id,)
            )
            return cursor.rowcount > 0
