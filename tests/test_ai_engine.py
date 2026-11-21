import unittest
from unittest.mock import Mock, patch

from ai_engine import AIEngine


class LocalAIEngineTests(unittest.TestCase):
    @patch("ai_engine.requests.post")
    def test_generates_draft_using_local_ollama(self, post):
        response = Mock()
        response.json.return_value = {"response": "A helpful draft"}
        post.return_value = response
        result = AIEngine().generate_content("SEO basics", "blogger")
        self.assertTrue(result["success"])
        self.assertEqual(result["content"], "A helpful draft")
        self.assertTrue(post.call_args.args[0].startswith("http://127.0.0.1:11434/"))

    @patch("ai_engine.requests.post", side_effect=OSError("offline"))
    def test_reports_local_model_unavailable_without_paid_fallback(self, post):
        result = AIEngine().generate_content("SEO basics")
        self.assertFalse(result["success"])
        self.assertEqual(result["status"], "local_model_unavailable")
        self.assertIn("No paid API", result["message"])


if __name__ == "__main__":
    unittest.main()
