import os
import requests


class SocialMediaManager:

    def __init__(self):
        self.facebook_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.facebook_page_id = os.getenv("FACEBOOK_PAGE_ID")

        self.x_api_key = os.getenv("X_API_KEY")
        self.x_api_secret = os.getenv("X_API_SECRET")

    def create_facebook_post(self, message, link=None):
        if not self.facebook_token or not self.facebook_page_id:
            return {
                "success": False,
                "message": "Facebook credentials are missing."
            }

        url = f"https://graph.facebook.com/v21.0/{self.facebook_page_id}/feed"

        data = {
            "message": message,
            "access_token": self.facebook_token
        }

        if link:
            data["link"] = link

        try:
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()

            return {
                "success": True,
                "result": response.json()
            }

        except requests.RequestException as error:
            return {
                "success": False,
                "message": str(error)
            }

    def create_x_post(self, message):
        return {
            "success": False,
            "message": (
                "X API authentication and publishing "
                "integration must be configured."
            ),
            "draft": message
        }

    def create_post_draft(self, platform, message):
        return {
            "platform": platform,
            "message": message,
            "status": "draft"
        }
