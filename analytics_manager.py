
from datetime import date


class AnalyticsManager:
    def __init__(self):
        self.records = []

    def add_daily_record(
        self,
        platform,
        visitors=0,
        pageviews=0,
        impressions=0,
        clicks=0,
        earnings=0.0
    ):
        record = {
            "date": date.today().isoformat(),
            "platform": platform,
            "visitors": max(0, int(visitors)),
            "pageviews": max(0, int(pageviews)),
            "impressions": max(0, int(impressions)),
            "clicks": max(0, int(clicks)),
            "earnings": max(0.0, float(earnings))
        }

        self.records.append(record)
        return record

    def calculate_metrics(self, record):
        impressions = record["impressions"]
        clicks = record["clicks"]
        earnings = record["earnings"]
        pageviews = record["pageviews"]

        return {
            **record,
            "ctr_percent": round(
                clicks / impressions * 100, 2
            ) if impressions else 0,
            "cpm": round(
                earnings / impressions * 1000, 2
            ) if impressions else 0,
            "rpm": round(
                earnings / pageviews * 1000, 2
            ) if pageviews else 0
        }

    def get_report(self):
        return [
            self.calculate_metrics(record)
            for record in self.records
        ]

    def total_earnings(self):
        return round(
            sum(record["earnings"] for record in self.records),
            2
        )
