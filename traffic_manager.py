from database import get_connection, initialize_database


class TrafficManager:
    def __init__(self):
        initialize_database()

    def create_campaign(self, name, platform, website_url):
        with get_connection() as connection:
            cursor = connection.execute(
                """INSERT INTO campaigns (name, platform, website, status)
                   VALUES (?, ?, ?, 'draft')""",
                (name, platform, website_url),
            )
            row = connection.execute(
                "SELECT * FROM campaigns WHERE id = ?", (cursor.lastrowid,)
            ).fetchone()
            return dict(row)

    def seo_checklist(self):
        return [
            "Create original and useful content",
            "Use relevant keywords",
            "Write SEO-friendly titles",
            "Add descriptive meta descriptions",
            "Optimize images",
            "Use internal links",
            "Improve mobile experience",
            "Submit sitemap to Google",
        ]

    def generate_promotion_plan(self, website_url):
        return {
            "website": website_url,
            "tasks": [
                "Create useful blog content",
                "Share articles on Facebook",
                "Share posts on X",
                "Create relevant social media posts",
                "Monitor Google Analytics",
                "Review traffic performance",
            ],
            "status": "draft",
        }

    def get_campaigns(self):
        with get_connection() as connection:
            rows = connection.execute(
                "SELECT * FROM campaigns ORDER BY id DESC"
            ).fetchall()
            return [dict(row) for row in rows]
