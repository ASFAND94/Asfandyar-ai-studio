import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from auth_manager import AuthManager


class AuthManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = AuthManager(Path(self.temp_dir.name) / "auth-test.db")
        self.env = patch.dict(os.environ, {"ADMIN_SETUP_KEY": "test-setup-key-long-enough-123"})
        self.env.start()
        self.addCleanup(self.env.stop)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_setup_login_and_csrf_validation(self):
        self.manager.setup("test-setup-key-long-enough-123", "owner_admin", "a-very-long-test-password")
        result = self.manager.login("owner_admin", "a-very-long-test-password", "127.0.0.1")
        self.assertIsNotNone(result)
        session = self.manager.validate_session(result["session"])
        self.assertIsNotNone(session)
        self.assertTrue(self.manager.validate_csrf(session, result["csrf"]))
        self.assertFalse(self.manager.validate_csrf(session, "wrong-token"))

    def test_setup_is_one_time(self):
        self.manager.setup("test-setup-key-long-enough-123", "owner_admin", "a-very-long-test-password")
        with self.assertRaises(FileExistsError):
            self.manager.setup("test-setup-key-long-enough-123", "other_admin", "another-long-password")

    def test_five_bad_logins_lock_client(self):
        self.manager.setup("test-setup-key-long-enough-123", "owner_admin", "a-very-long-test-password")
        for _ in range(5):
            self.assertIsNone(self.manager.login("owner_admin", "wrong-password", "127.0.0.2"))
        with self.assertRaises(TimeoutError):
            self.manager.login("owner_admin", "a-very-long-test-password", "127.0.0.2")

    def test_password_change_revokes_sessions(self):
        self.manager.setup("test-setup-key-long-enough-123", "owner_admin", "a-very-long-test-password")
        result = self.manager.login("owner_admin", "a-very-long-test-password", "127.0.0.3")
        self.manager.change_password(result["session"], "a-very-long-test-password", "a-new-very-long-password")
        self.assertIsNone(self.manager.validate_session(result["session"]))
        self.assertIsNotNone(self.manager.login("owner_admin", "a-new-very-long-password", "127.0.0.3"))


if __name__ == "__main__":
    unittest.main()
