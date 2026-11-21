"""D1-backed repositories for drafts, traffic plans, and manual analytics."""
from datetime import date


class D1ContentRepository:
    def __init__(self, store):
        self.store = store

    async def create_content(self, title, body, platform="blogger"):
        if not title or not body:
            return None
        await self.store.execute(
            """INSERT INTO content_drafts (title, body, platform, status)
               VALUES (?, ?, ?, 'draft')""",
            title, body, platform,
        )
        return await self.store.one(
            """SELECT id, title, body, platform, status, created_at, updated_at
               FROM content_drafts WHERE title = ? AND platform = ?
               ORDER BY id DESC LIMIT 1""",
            title, platform,
        )

    async def get_all_content(self):
        return await self.store.all(
            """SELECT id, title, body, platform, status, created_at, updated_at
               FROM content_drafts ORDER BY id DESC"""
        )

    async def mark_ready(self, content_id):
        await self.store.execute(
            """UPDATE content_drafts
               SET status = 'ready_to_publish', updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND status = 'draft'""",
            content_id,
        )
        row = await self.store.one(
            """SELECT id, title, body, platform, status, created_at, updated_at
               FROM content_drafts WHERE id = ?""",
            content_id,
        )
        return row

    async def delete_content(self, content_id):
        result = await self.store.execute(
            "DELETE FROM content_drafts WHERE id = ?", content_id
        )
        return int(result.get("changes", 0)) > 0


class D1CampaignRepository:
    def __init__(self, store):
        self.store = store

    async def create_campaign(self, name, platform, website_url):
        await self.store.execute(
            """INSERT INTO campaigns (name, platform, website_url)
               VALUES (?, ?, ?)""",
            name, platform, website_url,
        )
        return await self.store.one(
            """SELECT id, name, platform, website_url AS website, created_at
               FROM campaigns WHERE name = ? AND platform = ?
               ORDER BY id DESC LIMIT 1""",
            name, platform,
        )

    async def get_campaigns(self):
        return await self.store.all(
            """SELECT id, name, platform, website_url AS website, created_at
               FROM campaigns ORDER BY id DESC"""
        )


class D1AnalyticsRepository:
    def __init__(self, store):
        self.store = store

    @staticmethod
    def calculate_metrics(record):
        impressions = int(record["impressions"])
        clicks = int(record["clicks"])
        earnings = float(record["earnings"])
        pageviews = int(record["pageviews"])
        return {
            **record,
            "ctr_percent": round(clicks / impressions * 100, 2) if impressions else 0,
            "cpm": round(earnings / impressions * 1000, 2) if impressions else 0,
            "rpm": round(earnings / pageviews * 1000, 2) if pageviews else 0,
        }

    async def add_daily_record(
        self, platform, visitors=0, pageviews=0, impressions=0,
        clicks=0, earnings=0.0, record_date=None,
    ):
        record_date = record_date or date.today().isoformat()
        values = (
            record_date, platform, max(0, int(visitors)),
            max(0, int(pageviews)), max(0, int(impressions)),
            max(0, int(clicks)), max(0.0, float(earnings)),
        )
        await self.store.execute(
            """INSERT INTO analytics_records
               (record_date, platform, visitors, pageviews, impressions, clicks, earnings)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            *values,
        )
        row = await self.store.one(
            """SELECT record_date AS date, platform, visitors, pageviews,
                      impressions, clicks, earnings
               FROM analytics_records
               WHERE record_date = ? AND platform = ?
               ORDER BY id DESC LIMIT 1""",
            record_date, platform,
        )
        return self.calculate_metrics(row)

    async def get_report(self):
        rows = await self.store.all(
            """SELECT record_date AS date, platform, visitors, pageviews,
                      impressions, clicks, earnings
               FROM analytics_records ORDER BY record_date DESC, id DESC"""
        )
        return [self.calculate_metrics(row) for row in rows]

    async def total_earnings(self):
        row = await self.store.one(
            "SELECT COALESCE(SUM(earnings), 0) AS total FROM analytics_records"
        )
        return round(float(row["total"]), 2)
