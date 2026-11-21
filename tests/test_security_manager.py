import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.fernet import Fernet

import security_manager


class SecurityManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "security.sqlite3"
        self.env = patch.dict(os.environ, {"APP_ENCRYPTION_KEY": Fernet.generate_key().decode()})
        self.env.start()
        self.old_path = security_manager.DB_PATH
        security_manager.DB_PATH = self.db_path
        security_manager.initialize()

    def tearDown(self):
        security_manager.DB_PATH = self.old_path
        self.env.stop()
        self.temp.cleanup()

    def test_totp_enrollment_and_verification(self):
        secret = security_manager.new_totp_enrollment()
        self.assertFalse(security_manager.mfa_enabled())
        code = security_manager.totp_code(secret)
        self.assertTrue(security_manager.verify_totp(code, secret=secret))
        self.assertTrue(security_manager.confirm_totp_enrollment(code))
        self.assertTrue(security_manager.mfa_enabled())
        self.assertTrue(security_manager.verify_owner_totp(code))
        self.assertFalse(security_manager.verify_owner_totp("000000"))
        security_manager.disable_totp()
        self.assertFalse(security_manager.mfa_enabled())

    def test_vault_encrypts_and_never_lists_secret_value(self):
        saved = security_manager.put_secret("blogger_access_token", "test-private-token")
        self.assertEqual(saved["name"], "blogger_access_token")
        self.assertEqual(security_manager.get_secret("blogger_access_token"), "test-private-token")
        metadata = security_manager.list_secret_metadata()
        self.assertEqual(metadata[0]["name"], "blogger_access_token")
        self.assertNotIn("test-private-token", str(metadata))
        with security_manager._connect() as db:
            ciphertext = db.execute("SELECT ciphertext FROM secret_vault").fetchone()[0]
        self.assertNotIn("test-private-token", ciphertext)
        self.assertTrue(security_manager.delete_secret("blogger_access_token"))
        self.assertIsNone(security_manager.get_secret("blogger_access_token"))


if __name__ == "__main__":
    unittest.main()
