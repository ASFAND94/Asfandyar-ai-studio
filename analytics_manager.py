from datetime import date

from database import get_connection, initialize_database


class AnalyticsManager:
    def __init__(self):
        initialize_database()

    def add_daily_record(self, platform, visitors=0, pageviews=0,
                         impressions=0, clicks=0, earnings=0.0):
        record = {
            "date": date.today().isoformat(),
            "platform": platform,
            "visitors": max(0, int(visitors)),
            "pageviews": max(0, int(pageviews)),
            "impressions": max(0, int(impressions)),
            "clicks": max(0, int(clicks)),
            "earnings": max(0.0, float(earnings)),
        }
        with get_connection() as connection:
            cursor = connection.execute(
                """INSERT INTO analytics
                   (date, platform, visitors, pageviews, impressions, clicks, earnings)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                tuple(record.values()),
            )
            record["id"] = cursor.lastrowid
        return record

    def calculate_metrics(self, record):
        impressions = record["impressions"]
        clicks = record["clicks"]
        earnings = record["earnings"]
        pageviews = record["pageviews"]
        return {
            **record,
            "ctr_percent": round(clicks / impressions * 100, 2) if impressions else 0,
            "cpm": round(earnings / impressions * 1000, 2) if impressions else 0,
            "rpm": round(earnings / pageviews * 1000, 2) if pageviews else 0,
        }

    def get_report(self):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM analytics ORDER BY date DESC, id DESC"
            ).fetchall()
        return [self.calculate_metrics(dict(row)) for row in rows]

    def total_earnings(self):
        with get_connection() as connection:
            row = connection.execute(
                "SELECT COALESCE(SUM(earnings), 0) AS total FROM analytics"
            ).fetchone()
        return round(float(row["total"]), 2)
