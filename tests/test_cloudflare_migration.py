import sqlite3
import unittest
from pathlib import Path


class CloudflareMigrationTests(unittest.TestCase):
    def test_all_migrations_execute_and_keep_safe_defaults(self):
        root = Path(__file__).resolve().parents[1]
        database = sqlite3.connect(":memory:")
        try:
            for migration in sorted((root / "migrations").glob("*.sql")):
                database.executescript(migration.read_text(encoding="utf-8"))
            tables = {
                row[0] for row in database.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            expected = {
                "admin_user", "admin_sessions", "login_attempts",
                "social_accounts", "social_account_preferences",
                "owner_control_settings", "content_drafts", "campaigns",
                "analytics_records", "monetization_link_settings",
                "blogger_settings",
            }
            self.assertTrue(expected.issubset(tables))
            controls = dict(database.execute(
                "SELECT setting_key, setting_value FROM owner_control_settings"
            ))
            self.assertEqual(controls["global_publishing_enabled"], "false")
            self.assertEqual(controls["require_approval"], "true")
            monetization = list(database.execute(
                "SELECT provider, enabled FROM monetization_link_settings"
            ))
            self.assertEqual({row[0] for row in monetization}, {"adsterra", "monetag"})
            self.assertTrue(all(row[1] == 0 for row in monetization))

            for index in range(10):
                database.execute(
                    "INSERT INTO social_accounts(platform, account_name, account_handle) VALUES (?, ?, ?)",
                    ("instagram", f"Account {index}", f"@user{index}"),
                )
            with self.assertRaises(sqlite3.IntegrityError):
                database.execute(
                    "INSERT INTO social_accounts(platform, account_name, account_handle) VALUES (?, ?, ?)",
                    ("instagram", "Eleventh", "@user10"),
                )
        finally:
            database.close()


if __name__ == "__main__":
    unittest.main()
