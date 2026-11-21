"""Create an encrypted, consistent SQLite backup.

Usage: python scripts/backup_database.py [destination.enc]
APP_DB_PATH and APP_ENCRYPTION_KEY must be set in the private environment.
"""
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

from cryptography.fernet import Fernet

source = Path(os.getenv("APP_DB_PATH", "asfandyar.db")).resolve()
key = os.getenv("APP_ENCRYPTION_KEY", "")
if not key:
    raise SystemExit("APP_ENCRYPTION_KEY is required.")
if not source.exists():
    raise SystemExit(f"Database not found: {source}")

try:
    cipher = Fernet(key.encode("ascii"))
except (ValueError, UnicodeEncodeError):
    raise SystemExit("APP_ENCRYPTION_KEY is not a valid Fernet key.")

destination = Path(sys.argv[1] if len(sys.argv) > 1 else f"{source.name}.backup.enc").resolve()
destination.parent.mkdir(parents=True, exist_ok=True)

with tempfile.NamedTemporaryFile(prefix="asfandyar-backup-", suffix=".sqlite3", delete=False) as tmp:
    temp_path = Path(tmp.name)

try:
    with sqlite3.connect(source) as live, sqlite3.connect(temp_path) as snapshot:
        live.backup(snapshot)
        result = snapshot.execute("PRAGMA integrity_check").fetchone()[0]
        if result != "ok":
            raise SystemExit(f"SQLite integrity check failed: {result}")
    encrypted = cipher.encrypt(temp_path.read_bytes())
    destination.write_bytes(encrypted)
    try:
        destination.chmod(0o600)
    except OSError:
        pass
    print(f"Encrypted backup written: {destination}")
    print("Store this file separately from APP_ENCRYPTION_KEY. Test restores regularly.")
finally:
    temp_path.unlink(missing_ok=True)
