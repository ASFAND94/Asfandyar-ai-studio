import os
import tempfile
import unittest
from pathlib import Path

from auth_manager import AuthManager
from social_account_manager import SocialAccountManager


class SocialAccountManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.manager = SocialAccountManager(Path(self.temp.name) / "social.db")

    def tearDown(self):
        self.temp.cleanup()

    def test_each_platform_has_independent_ten_account_limit(self):
        for index in range(10):
            self.manager.add_account("facebook_profile", f"FB Profile {index}", f"profile_{index}")
            self.manager.add_account("facebook_page", f"FB Page {index}", f"page_{index}")
        self.manager.add_account("instagram", "IG 1", "ig_1")
        with self.assertRaises(OverflowError):
            self.manager.add_account("facebook_profile", "FB Profile 11", "profile_11")
        with self.assertRaises(OverflowError):
            self.manager.add_account("facebook_page", "FB Page 11", "page_11")
        self.assertEqual(self.manager.account_limits()["facebook_profile"]["used"], 10)
        self.assertEqual(self.manager.account_limits()["facebook_page"]["used"], 10)
        self.assertEqual(self.manager.account_limits()["instagram"]["used"], 1)

    def test_owner_controls_niche_and_default_approval(self):
        account = self.manager.add_account("instagram", "My page", "@my_page")
        prefs = self.manager.get_preferences(account["id"])
        self.assertEqual(prefs["niche"], "")
        self.assertFalse(prefs["publishing_enabled"])
        self.assertTrue(prefs["require_approval"])\n        with self.assertRaises(ValueError):\n            self.manager.update_preferences(account["id"], {"require_approval": False})
        updated = self.manager.update_preferences(account["id"], {
            "niche": "AI education", "content_formats": ["reel", "post"],
            "publishing_enabled": True,
        })
        self.assertEqual(updated["niche"], "AI education")
        self.assertEqual(updated["content_formats"], ["reel", "post"])
        self.assertTrue(updated["publishing_enabled"])
        self.assertTrue(updated["require_approval"])

    def test_global_publishing_is_off_by_default(self):
        controls = self.manager.get_owner_controls()
        self.assertFalse(controls["global_publishing_enabled"])
        self.assertTrue(controls["require_approval"])\n        with self.assertRaises(ValueError):\n            self.manager.update_owner_controls(require_approval=False)


class AuthManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.manager = AuthManager(Path(self.temp.name) / "auth.db")
        os.environ["ADMIN_SETUP_KEY"] = "test-one-time-setup-secret-value"

    def tearDown(self):
        os.environ.pop("ADMIN_SETUP_KEY", None)
        self.temp.cleanup()

    def test_setup_login_csrf_and_password_change(self):
        self.manager.setup("test-one-time-setup-secret-value", "owner", "A-very-strong-test-password")
        result = self.manager.login("owner", "A-very-strong-test-password", "127.0.0.1")
        self.assertIsNotNone(result)
        session = self.manager.validate_session(result["session"])
        self.assertIsNotNone(session)
        self.assertTrue(self.manager.validate_csrf(session, result["csrf"]))
        self.manager.change_password(result["session"], "A-very-strong-test-password", "Another-strong-test-password")
        self.assertIsNone(self.manager.validate_session(result["session"]))
        self.assertIsNotNone(self.manager.login("owner", "Another-strong-test-password", "127.0.0.1"))


if __name__ == "__main__":
    unittest.main()
