"""Restore an encrypted SQLite backup. Stop the app before running.

Usage: python scripts/restore_database.py path/to/backup.enc
The current database is copied to <database>.pre-restore before replacement.
"""
import os
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

if len(sys.argv) != 2:
    raise SystemExit("Usage: python scripts/restore_database.py path/to/backup.enc")

key = os.getenv("APP_ENCRYPTION_KEY", "")
if not key:
    raise SystemExit("APP_ENCRYPTION_KEY is required.")
try:
    cipher = Fernet(key.encode("ascii"))
except (ValueError, UnicodeEncodeError):
    raise SystemExit("APP_ENCRYPTION_KEY is not a valid Fernet key.")

backup = Path(sys.argv[1]).resolve()
if not backup.is_file():
    raise SystemExit(f"Backup file not found: {backup}")
try:
    plain = cipher.decrypt(backup.read_bytes())
except InvalidToken:
    raise SystemExit("Backup could not be decrypted. Check the key and file integrity.")

database = Path(os.getenv("APP_DB_PATH", "asfandyar.db")).resolve()
database.parent.mkdir(parents=True, exist_ok=True)
with tempfile.NamedTemporaryFile(prefix="asfandyar-restore-", suffix=".sqlite3",
                                 dir=database.parent, delete=False) as tmp:
    staged = Path(tmp.name)
try:
    staged.write_bytes(plain)
    with sqlite3.connect(staged) as check:
        result = check.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise SystemExit(f"Restored database failed integrity check: {result}")
    if database.exists():
        shutil.copy2(database, database.with_suffix(database.suffix + ".pre-restore"))
    os.replace(staged, database)
    print(f"Restored database: {database}")
    print("Restart the application and verify owner login and stored records.")
finally:
    staged.unlink(missing_ok=True)
