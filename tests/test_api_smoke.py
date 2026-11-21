"""End-to-end smoke test for the private dashboard and protected API."""
import os
import tempfile
import unittest
from pathlib import Path

TEST_HOME = tempfile.TemporaryDirectory(prefix="asfandyar-test-")
os.environ["AUTH_DB_PATH"] = str(Path(TEST_HOME.name) / "auth.sqlite3")
os.environ["SOCIAL_DB_PATH"] = str(Path(TEST_HOME.name) / "social.sqlite3")
os.environ["ADMIN_SETUP_KEY"] = "api-test-only-setup-key-with-more-than-20-chars"
os.environ["COOKIE_SECURE"] = "false"

from fastapi.testclient import TestClient
from main import app


class DashboardAPISmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_setup_login_dashboard_and_owner_account_controls(self):
        page = self.client.get("/app/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Asfandyar AI Studio", page.text)

        status = self.client.get("/auth/status")
        self.assertEqual(status.status_code, 200)
        self.assertTrue(status.json()["setup_required"])

        setup = self.client.post("/auth/setup", json={
            "setup_key": os.environ["ADMIN_SETUP_KEY"],
            "username": "owner_test",
            "password": "Strong-test-password-123",
        })
        self.assertEqual(setup.status_code, 201, setup.text)

        login = self.client.post("/auth/login", json={
            "username": "owner_test",
            "password": "Strong-test-password-123",
        })
        self.assertEqual(login.status_code, 200, login.text)
        csrf = login.json()["csrf_token"]
        headers = {"X-CSRF-Token": csrf}

        me = self.client.get("/auth/me")
        self.assertEqual(me.status_code, 200)
        self.assertTrue(me.json()["authenticated"])

        account = self.client.post("/social/accounts", headers=headers, json={
            "platform": "instagram",
            "account_name": "Test page",
            "account_handle": "@test_page",
        })
        self.assertEqual(account.status_code, 201, account.text)
        account_id = account.json()["account"]["id"]

        preferences = self.client.put(
            f"/social/accounts/{account_id}/preferences",
            headers=headers,
            json={
                "niche": "AI education",
                "content_formats": ["reel", "post"],
                "publishing_enabled": False,
                "require_approval": True,
            },
        )
        self.assertEqual(preferences.status_code, 200, preferences.text)
        self.assertEqual(preferences.json()["preferences"]["niche"], "AI education")

        # Facebook profiles and Pages have independent 10-slot limits.
        profile = self.client.post("/social/accounts", headers=headers, json={
            "platform": "facebook_profile", "account_name": "Personal profile", "account_handle": "profile_one",
        })
        page = self.client.post("/social/accounts", headers=headers, json={
            "platform": "facebook_page", "account_name": "Business Page", "account_handle": "page_one",
        })
        self.assertEqual(profile.status_code, 201, profile.text)
        self.assertEqual(page.status_code, 201, page.text)
        platform_info = self.client.get("/social/platforms").json()
        self.assertEqual(platform_info["max_accounts_per_platform"], 10)
        self.assertEqual(platform_info["limits"]["facebook_profile"]["used"], 1)
        self.assertEqual(platform_info["limits"]["facebook_page"]["used"], 1)

        settings = self.client.get("/control/settings")
        self.assertEqual(settings.status_code, 200)
        self.assertFalse(settings.json()["global_publishing_enabled"])\n        self.assertTrue(settings.json()["require_approval"])\n\n        cannot_disable = self.client.put("/control/settings", headers=headers, json={"require_approval": False})\n        self.assertEqual(cannot_disable.status_code, 422)

        blocked = self.client.post("/social/accounts", json={
            "platform": "facebook",
            "account_name": "No CSRF",
            "account_handle": "no_csrf",
        })
        self.assertEqual(blocked.status_code, 403)

        logout = self.client.post("/auth/logout", headers=headers, json={})
        self.assertEqual(logout.status_code, 200)
        protected = self.client.get("/social/accounts")
        self.assertEqual(protected.status_code, 401)


if __name__ == "__main__":
    unittest.main()
