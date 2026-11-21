"""Official Blogger v3 publishing adapter.

Credentials are read from private environment variables first, then from the
encrypted owner vault. OAuth consent and refresh-token management are not
implemented here: supply a valid short-lived access token privately.
"""
import os
import requests

import security_manager


class BloggerManager:
    def __init__(self):
        self.api_url = "https://www.googleapis.com/blogger/v3"
        self.access_token = None
        self.blog_id = None
        self.refresh_credentials()

    def refresh_credentials(self):
        self.access_token = os.getenv("BLOGGER_ACCESS_TOKEN")
        self.blog_id = os.getenv("BLOGGER_BLOG_ID")
        if not self.access_token or not self.blog_id:
            try:
                self.access_token = self.access_token or security_manager.get_secret("blogger_access_token")
                self.blog_id = self.blog_id or security_manager.get_secret("blogger_blog_id")
            except (RuntimeError, OSError):
                pass
        return bool(self.access_token and self.blog_id)

    def create_post(self, title, content, labels=None):
        self.refresh_credentials()
        if not self.access_token or not self.blog_id:
            return {
                "success": False,
                "message": "Blogger API credentials are missing. Store blogger_access_token and blogger_blog_id in the encrypted vault or configure private environment variables."
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
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            return {"success": True, "post": response.json()}
        except requests.RequestException as error:
            # Do not echo request headers or token material into application logs.
            return {
                "success": False,
                "message": f"Blogger API request failed ({getattr(error.response, 'status_code', 'network error')}). Check token validity and Blogger permissions."
            }
