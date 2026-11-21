"""Persistence regression tests for the shared SQLite-backed managers."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class PersistenceTests(unittest.TestCase):
    def test_content_campaigns_and_analytics_survive_manager_restart(self):
        with tempfile.TemporaryDirectory() as folder:
            db_path = str(Path(folder) / "studio.sqlite3")
            with patch.dict(os.environ, {"APP_DB_PATH": db_path}):
                # Import after selecting an isolated test database.
                import database
                import content_manager
                import analytics_manager
                import traffic_manager

                database.DATABASE_PATH = Path(db_path)
                content_manager.initialize_database = database.initialize_database
                analytics_manager.initialize_database = database.initialize_database
                traffic_manager.initialize_database = database.initialize_database

                draft = content_manager.ContentManager().create_content(
                    "Persistence test", "A durable content draft for testing.", "blogger"
                )
                campaign = traffic_manager.TrafficManager().create_campaign(
                    "Test campaign", "facebook", "https://example.com"
                )
                analytics_manager.AnalyticsManager().add_daily_record(
                    "manual", visitors=12, pageviews=20, impressions=100,
                    clicks=4, earnings=1.25
                )

                # New manager instances must read the same durable database.
                self.assertEqual(
                    content_manager.ContentManager().get_content(draft["id"])["title"],
                    "Persistence test",
                )
                self.assertEqual(
                    traffic_manager.TrafficManager().get_campaigns()[0]["name"],
                    campaign["name"],
                )
                analytics = analytics_manager.AnalyticsManager()
                self.assertEqual(len(analytics.get_report()), 1)
                self.assertEqual(analytics.total_earnings(), 1.25)


if __name__ == "__main__":
    unittest.main()
