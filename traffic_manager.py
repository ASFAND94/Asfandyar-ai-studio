class TrafficManager:

    def __init__(self):
        self.campaigns = []

    def create_campaign(self, name, platform, website_url):
        campaign = {
            "name": name,
            "platform": platform,
            "website": website_url,
            "status": "draft"
        }

        self.campaigns.append(campaign)
        return campaign

    def seo_checklist(self):
        return [
            "Create original and useful content",
            "Use relevant keywords",
            "Write SEO-friendly titles",
            "Add descriptive meta descriptions",
            "Optimize images",
            "Use internal links",
            "Improve mobile experience",
            "Submit sitemap to Google"
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
                "Review traffic performance"
            ],
            "status": "draft"
        }

    def get_campaigns(self):
        return self.campaigns
