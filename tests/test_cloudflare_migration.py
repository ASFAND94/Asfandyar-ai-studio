import sqlite3
import unittest
from pathlib import Path


class CloudflareMigrationTests(unittest.TestCase):
    def test_initial_migration_executes_and_keeps_publishing_safe(self):
        migration = (
            Path(__file__).resolve().parents[1]
            / "migrations"
            / "0001_initial.sql"
        )
        database = sqlite3.connect(":memory:")
        try:
            database.executescript(migration.read_text(encoding="utf-8"))
            tables = {
                row[0]
                for row in database.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            expected = {
                "admin_user", "admin_sessions", "login_attempts",
                "social_accounts", "social_account_preferences",
                "owner_control_settings", "content_drafts", "campaigns",
                "analytics_records",
            }
            self.assertTrue(expected.issubset(tables))
            controls = dict(database.execute(
                "SELECT setting_key, setting_value FROM owner_control_settings"
            ))
            self.assertEqual(controls["global_publishing_enabled"], "false")
            self.assertEqual(controls["require_approval"], "true")
        finally:
            database.close()


if __name__ == "__main__":
    unittest.main()
