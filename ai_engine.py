"""Optional local AI generation through Ollama. No paid API is called."""
import os
import requests


class AIEngine:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    def build_prompt(self, topic, platform="blogger"):
        return (
            "Write original, useful, accurate content suitable for the selected platform. "
            "Do not invent statistics, sources, product claims or personal experiences. "
            "Use a clear headline, helpful structure and a natural call to action. "
            "Return only the finished draft.\n\n"
            f"Platform: {platform}\nTopic: {topic}"
        )

    def generate_content(self, topic, platform="blogger"):
        if not topic or not topic.strip():
            return {"success": False, "status": "invalid", "message": "Please provide a topic."}
        prompt = self.build_prompt(topic.strip(), platform)
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=(5, 180),
            )
            response.raise_for_status()
            text = response.json().get("response", "").strip()
            if not text:
                return {"success": False, "status": "empty", "message": "The local model returned an empty response."}
            return {"success": True, "status": "generated", "model": self.model, "platform": platform, "content": text}
        except (requests.RequestException, OSError):
            return {
                "success": False,
                "status": "local_model_unavailable",
                "message": "Local Ollama is not reachable. Install Ollama, download a model, and configure OLLAMA_BASE_URL and OLLAMA_MODEL. No paid API is used.",
                "prompt": prompt,
            }

    def create_post(self, topic, platform="blogger"):
        return self.generate_content(topic, platform)


if __name__ == "__main__":
    import json
    print(json.dumps(AIEngine().generate_content("A beginner's guide to digital marketing"), indent=2))
