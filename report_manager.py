
import json
from pathlib import Path
from datetime import date, timedelta


class ReportManager:

    def __init__(self, analytics_manager=None):
        self.analytics_manager = analytics_manager

    def get_records(self):
        if self.analytics_manager:
            return self.analytics_manager.get_report()
        return []

    def generate_daily_report(self):
        today = date.today().isoformat()

        records = [
            record for record in self.get_records()
            if record["date"] == today
        ]

        return self.summarize(records, "Daily Report")

    def generate_weekly_report(self):
        today = date.today()
        start = today - timedelta(days=6)

        records = [
            record for record in self.get_records()
            if start.isoformat() <= record["date"] <= today.isoformat()
        ]

        return self.summarize(records, "Weekly Report")

    def generate_monthly_report(self):
        today = date.today()

        records = [
            record for record in self.get_records()
            if record["date"][:7] == today.strftime("%Y-%m")
        ]

        return self.summarize(records, "Monthly Report")

    def summarize(self, records, report_type):
        return {
            "report_type": report_type,
            "total_records": len(records),
            "total_visitors": sum(r["visitors"] for r in records),
            "total_pageviews": sum(r["pageviews"] for r in records),
            "total_impressions": sum(r["impressions"] for r in records),
            "total_clicks": sum(r["clicks"] for r in records),
            "total_earnings": round(
                sum(r["earnings"] for r in records), 2
            ),
            "average_ctr": self.average(records, "ctr_percent"),
            "average_cpm": self.average(records, "cpm"),
            "average_rpm": self.average(records, "rpm")
        }

    def average(self, records, key):
        if not records:
            return 0

        return round(
            sum(r.get(key, 0) for r in records) / len(records),
            2
        )

    def export_report(self, report, filename="report.json"):
        output_dir = Path("data/reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / filename

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(report, file, indent=4, ensure_ascii=False)

        return str(filepath)


if __name__ == "__main__":
    manager = ReportManager()

    print("Asfandyar AI Studio - Report Manager")
    print(json.dumps(
        manager.generate_daily_report(),
        indent=4
    ))
