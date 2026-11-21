from datetime import datetime


class ContentManager:

    def __init__(self):
        self.contents = []

    def create_content(self, title, body, platform="blogger"):
        if not title or not body:
            return None

        content = {
            "id": len(self.contents) + 1,
            "title": title,
            "body": body,
            "platform": platform,
            "status": "draft",
            "created_at": datetime.now().isoformat()
        }

        self.contents.append(content)
        return content

    def get_all_content(self):
        return self.contents

    def publish_content(self, content_id):
        for content in self.contents:
            if content["id"] == content_id:
                content["status"] = "ready_to_publish"
                return content

        return None

    def mark_published(self, content_id, post=None):
        for content in self.contents:
            if content["id"] == content_id:
                content["status"] = "published"
                if post:
                    content["external_post_id"] = post.get("id")
                    content["external_url"] = post.get("url")
                return content
        return None

    def delete_content(self, content_id):
        self.contents = [
            content for content in self.contents
            if content["id"] != content_id
        ]

        return True
