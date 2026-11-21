import os
import runpy
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.fernet import Fernet


class BackupRestoreTests(unittest.TestCase):
    def test_encrypted_backup_and_verified_restore(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            database = root / "app.sqlite3"
            backup = root / "backup.enc"
            with sqlite3.connect(database) as db:
                db.execute("CREATE TABLE sample (value TEXT)")
                db.execute("INSERT INTO sample VALUES ('persisted-value')")

            env = {
                "APP_DB_PATH": str(database),
                "APP_ENCRYPTION_KEY": Fernet.generate_key().decode(),
            }
            with patch.dict(os.environ, env):
                with patch.object(sys, "argv", ["backup_database.py", str(backup)]):
                    runpy.run_path(str(Path(__file__).parents[1] / "scripts" / "backup_database.py"))
                self.assertTrue(backup.exists())
                self.assertNotIn(b"persisted-value", backup.read_bytes())

                with sqlite3.connect(database) as db:
                    db.execute("UPDATE sample SET value='changed-value'")

                with patch.object(sys, "argv", ["restore_database.py", str(backup)]):
                    runpy.run_path(str(Path(__file__).parents[1] / "scripts" / "restore_database.py"))

            with sqlite3.connect(database) as db:
                self.assertEqual(db.execute("SELECT value FROM sample").fetchone()[0], "persisted-value")
            self.assertTrue(database.with_suffix(".sqlite3.pre-restore").exists())


if __name__ == "__main__":
    unittest.main()
