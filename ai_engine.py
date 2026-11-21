import os


class AIEngine:

    def __init__(self):
        self.provider = "free"
        self.model = None

    def generate_content(self, topic, platform="blogger"):
        if not topic:
            return "Please provide a content topic."

        prompt = f"""
        Create original and engaging content.

        Topic: {topic}
        Platform: {platform}

        Requirements:
        - Write useful and informative content.
        - Use an attractive headline.
        - Include relevant keywords.
        - Avoid misleading claims.
        """

        return prompt

    def create_post(self, topic, platform):
        content = self.generate_content(topic, platform)

        return {
            "platform": platform,
            "content": content,
            "status": "draft"
        }


if __name__ == "__main__":
    ai = AIEngine()
    result = ai.create_post(
        "Digital Marketing",
        "blogger"
    )
    print(result)
