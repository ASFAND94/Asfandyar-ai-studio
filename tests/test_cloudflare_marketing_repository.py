import sqlite3
import unittest

from cloudflare_marketing_repository import (
    D1AnalyticsRepository,
    D1CampaignRepository,
    D1ContentRepository,
)


class SQLiteTestStore:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE content_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                platform TEXT NOT NULL DEFAULT 'blogger',
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                website_url TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE monetization_link_settings (
                provider TEXT PRIMARY KEY,
                direct_link_url TEXT NOT NULL DEFAULT '',
                placement TEXT NOT NULL DEFAULT 'end_article',
                enabled INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE analytics_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_date TEXT NOT NULL,
                platform TEXT NOT NULL,
                visitors INTEGER NOT NULL DEFAULT 0,
                pageviews INTEGER NOT NULL DEFAULT 0,
                impressions INTEGER NOT NULL DEFAULT 0,
                clicks INTEGER NOT NULL DEFAULT 0,
                earnings REAL NOT NULL DEFAULT 0
            );
        """)

    async def one(self, sql, *params):
        row = self.db.execute(sql, params).fetchone()
        return dict(row) if row is not None else None

    async def all(self, sql, *params):
        return [dict(row) for row in self.db.execute(sql, params).fetchall()]

    async def execute(self, sql, *params):
        cursor = self.db.execute(sql, params)
        self.db.commit()
        return {"changes": cursor.rowcount, "last_row_id": cursor.lastrowid}


class D1MarketingRepositoryTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.store = SQLiteTestStore()
        self.content = D1ContentRepository(self.store)
        self.campaigns = D1CampaignRepository(self.store)
        self.analytics = D1AnalyticsRepository(self.store)

    async def test_content_drafts_persist_and_mark_ready(self):
        draft = await self.content.create_content("Test title", "Long enough body", "blogger")
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(len(await self.content.get_all_content()), 1)
        ready = await self.content.mark_ready(draft["id"])
        self.assertEqual(ready["status"], "ready_to_publish")
        self.assertTrue(await self.content.delete_content(draft["id"]))
        self.assertEqual(await self.content.get_all_content(), [])

    async def test_empty_content_is_rejected(self):
        self.assertIsNone(await self.content.create_content("", "body"))

    async def test_enabled_monetization_links_are_inserted_only_in_blogger_drafts(self):
        await self.store.execute(
            """INSERT INTO monetization_link_settings
               (provider, direct_link_url, placement, enabled)
               VALUES (?, ?, ?, ?)""",
            "adsterra", "https://example.com/ad", "after_intro", 1,
        )
        blogger = await self.content.create_content(
            "Blogger article", "Intro paragraph\\n\\nSecond paragraph", "blogger"
        )
        self.assertIn('rel="sponsored nofollow noopener noreferrer"', blogger["body"])
        self.assertIn("https://example.com/ad", blogger["body"])
        social = await self.content.create_content(
            "Social post", "A social post body", "facebook"
        )
        self.assertNotIn("example.com/ad", social["body"])

    async def test_campaigns_persist(self):
        campaign = await self.campaigns.create_campaign(
            "Blogger traffic", "facebook", "https://example.com"
        )
        self.assertEqual(campaign["website"], "https://example.com")
        self.assertEqual(len(await self.campaigns.get_campaigns()), 1)

    async def test_analytics_metrics_and_total(self):
        record = await self.analytics.add_daily_record(
            "blogger", visitors=50, pageviews=100, impressions=500,
            clicks=10, earnings=2.5, record_date="2026-11-21",
        )
        self.assertEqual(record["ctr_percent"], 2.0)
        self.assertEqual(record["cpm"], 5.0)
        self.assertEqual(record["rpm"], 25.0)
        self.assertEqual(await self.analytics.total_earnings(), 2.5)
        self.assertEqual(len(await self.analytics.get_report()), 1)


if __name__ == "__main__":
    unittest.main()
