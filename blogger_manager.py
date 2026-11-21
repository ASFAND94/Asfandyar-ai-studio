import os
import requests


class BloggerManager:

    def __init__(self):
        self.api_url = "https://www.googleapis.com/blogger/v3"
        self.access_token = os.getenv("BLOGGER_ACCESS_TOKEN")
        self.blog_id = os.getenv("BLOGGER_BLOG_ID")

    def create_post(self, title, content, labels=None):
        if not self.access_token or not self.blog_id:
            return {
                "success": False,
                "message": "Blogger API credentials are missing."
            }

        url = f"{self.api_url}/blogs/{self.blog_id}/posts/"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
            "labels": labels or []
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )

            response.raise_for_status()

            return {
                "success": True,
                "post": response.json()
            }

        except requests.RequestException as error:
            return {
                "success": False,
                "message": str(error)
            }
