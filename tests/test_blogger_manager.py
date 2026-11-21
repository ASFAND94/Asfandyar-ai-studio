import unittest
from unittest.mock import patch

from blogger_manager import BloggerManager


class BloggerManagerTests(unittest.TestCase):
    def test_reads_credentials_from_encrypted_vault_fallback(self):
        with patch.dict("os.environ", {"BLOGGER_ACCESS_TOKEN": "", "BLOGGER_BLOG_ID": ""}):
            with patch("blogger_manager.security_manager.get_secret") as get_secret:
                get_secret.side_effect = lambda name: {
                    "blogger_access_token": "private-token",
                    "blogger_blog_id": "blog-123",
                }.get(name)
                manager = BloggerManager()
        self.assertEqual(manager.access_token, "private-token")
        self.assertEqual(manager.blog_id, "blog-123")
        self.assertTrue(manager.refresh_credentials())


if __name__ == "__main__":
    unittest.main()
