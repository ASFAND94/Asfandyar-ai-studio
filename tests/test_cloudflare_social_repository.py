import json
import sqlite3
import unittest

from cloudflare_social_repository import D1SocialAccountRepository


class SQLiteTestStore:
    """SQLite-backed stand-in to exercise repository SQL and behavior locally."""

    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys = ON")
        self.db.executescript("""
            CREATE TABLE social_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                account_name TEXT NOT NULL,
                account_handle TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'not_connected',
                provider_account_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, account_handle)
            );
            CREATE TABLE social_account_preferences (
                account_id INTEGER PRIMARY KEY,
                niche TEXT NOT NULL DEFAULT '',
                content_formats TEXT NOT NULL DEFAULT '["post"]',
                publishing_enabled INTEGER NOT NULL DEFAULT 0,
                require_approval INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(account_id) REFERENCES social_accounts(id) ON DELETE CASCADE
            );
            CREATE TABLE owner_control_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL
            );
            INSERT INTO owner_control_settings VALUES
                ('global_publishing_enabled', 'false'),
                ('require_approval', 'true');
        """)

    async def one(self, sql, *params):
        row = self.db.execute(sql, params).fetchone()
        return dict(row) if row is not None else None

    async def all(self, sql, *params):
        return [dict(row) for row in self.db.execute(sql, params).fetchall()]

    async def execute(self, sql, *params):
        cursor = self.db.execute(sql, params)
        self.db.commit()
        return {"changes": cursor.rowcount if cursor.rowcount >= 0 else 0}

    async def batch(self, statements):
        results = []
        with self.db:
            for sql, params in statements:
                cursor = self.db.execute(sql, tuple(params))
                results.append({"changes": cursor.rowcount})
        return results


class D1SocialRepositoryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.store = SQLiteTestStore()
        self.repo = D1SocialAccountRepository(self.store)

    async def test_add_and_list_account(self):
        account = await self.repo.add_account("facebook", "My Page", "@mypage")
        self.assertEqual(account["platform"], "facebook_profile")
        rows = await self.repo.list_accounts("facebook_profile")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["account_handle"], "@mypage")

    async def test_duplicate_handle_rejected(self):
        await self.repo.add_account("x", "First", "@same")
        with self.assertRaises(ValueError):
            await self.repo.add_account("x", "Second", "@same")

    async def test_ten_slot_limit_enforced(self):
        for index in range(10):
            await self.repo.add_account("instagram", f"Account {index}", f"@user{index}")
        with self.assertRaises(OverflowError):
            await self.repo.add_account("instagram", "Eleventh", "@user10")

    async def test_preferences_keep_publishing_safe_by_default(self):
        account = await self.repo.add_account("youtube", "Channel", "@channel")
        prefs = await self.repo.get_preferences(account["id"])
        self.assertFalse(prefs["publishing_enabled"])
        self.assertTrue(prefs["require_approval"])
        updated = await self.repo.update_preferences(
            account["id"],
            {"niche": "technology", "content_formats": ["video", "short"]},
        )
        self.assertEqual(updated["niche"], "technology")
        self.assertEqual(updated["content_formats"], ["video", "short"])
        self.assertFalse(updated["publishing_enabled"])

    async def test_invalid_format_rejected(self):
        account = await self.repo.add_account("x", "Account", "@account")
        with self.assertRaises(ValueError):
            await self.repo.update_preferences(
                account["id"], {"content_formats": ["unknown"]}
            )

    async def test_owner_controls_default_off_and_can_update(self):
        controls = await self.repo.get_owner_controls()
        self.assertFalse(controls["global_publishing_enabled"])
        self.assertTrue(controls["require_approval"])
        updated = await self.repo.update_owner_controls(
            global_publishing_enabled=True, require_approval=True
        )
        self.assertTrue(updated["global_publishing_enabled"])
        self.assertTrue(updated["require_approval"])

    async def test_delete_removes_account_and_preferences(self):
        account = await self.repo.add_account("linkedin", "Profile", "@profile")
        self.assertTrue(await self.repo.remove_account(account["id"]))
        self.assertIsNone(await self.repo.get_preferences(account["id"]))
        self.assertFalse(await self.repo.remove_account(account["id"]))


if __name__ == "__main__":
    unittest.main()
