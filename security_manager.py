"""Encrypted secret vault and RFC 6238 TOTP MFA helpers.

Requires APP_ENCRYPTION_KEY containing a Fernet key generated with:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
Keep that key outside GitHub and back it up separately. Losing it makes stored secrets unrecoverable.
"""
import base64
import hashlib
import hmac
import os
import secrets
import sqlite3
import struct
import time
from datetime import datetime, timezone
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

DB_PATH = Path(os.getenv("APP_DB_PATH", str(Path(__file__).resolve().parent / "asfandyar.db")))


def _fernet():
    key = os.getenv("APP_ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError("APP_ENCRYPTION_KEY is not configured. Generate a Fernet key and set it in the private server environment.")
    try:
        return Fernet(key.encode("ascii"))
    except (ValueError, UnicodeEncodeError):
        raise RuntimeError("APP_ENCRYPTION_KEY is invalid. Generate a valid Fernet key.")


def _connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=20)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout=20000")
    db.execute("PRAGMA foreign_keys=ON")
    return db


def initialize():
    with _connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS owner_mfa (
            id INTEGER PRIMARY KEY CHECK(id=1),
            secret_ciphertext TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS mfa_login_attempts (
            client_key TEXT PRIMARY KEY,
            failures INTEGER NOT NULL DEFAULT 0,
            locked_until REAL
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS secret_vault (
            name TEXT PRIMARY KEY,
            ciphertext TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )""")


def _now():
    return datetime.now(timezone.utc).isoformat()


def new_totp_enrollment():
    initialize()
    f = _fernet()
    secret = base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")
    encrypted = f.encrypt(secret.encode()).decode()
    with _connect() as db:
        db.execute(
            "INSERT INTO owner_mfa(id, secret_ciphertext, enabled, updated_at) VALUES(1, ?, 0, ?) "
            "ON CONFLICT(id) DO UPDATE SET secret_ciphertext=excluded.secret_ciphertext, enabled=0, updated_at=excluded.updated_at",
            (encrypted, _now()),
        )
    return secret


def _get_totp_secret():
    initialize()
    with _connect() as db:
        row = db.execute("SELECT secret_ciphertext FROM owner_mfa WHERE id=1").fetchone()
    if not row:
        return None
    try:
        return _fernet().decrypt(row["secret_ciphertext"].encode()).decode()
    except InvalidToken:
        raise RuntimeError("MFA secret cannot be decrypted. Check APP_ENCRYPTION_KEY.")


def totp_code(secret, timestamp=None):
    timestamp = time.time() if timestamp is None else timestamp
    key = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
    counter = int(timestamp // 30)
    digest = hmac.new(key, struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    number = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return f"{number % 1000000:06d}"


def verify_totp(code, secret=None, timestamp=None, window=1):
    if not isinstance(code, str) or len(code) != 6 or not code.isdigit():
        return False
    secret = secret or _get_totp_secret()
    if not secret:
        return False
    now = time.time() if timestamp is None else timestamp
    return any(hmac.compare_digest(totp_code(secret, now + offset * 30), code)
               for offset in range(-window, window + 1))


def confirm_totp_enrollment(code):
    secret = _get_totp_secret()
    if not secret or not verify_totp(code, secret=secret):
        return False
    with _connect() as db:
        db.execute("UPDATE owner_mfa SET enabled=1, updated_at=? WHERE id=1", (_now(),))
    return True


def mfa_enabled():
    initialize()
    with _connect() as db:
        row = db.execute("SELECT enabled FROM owner_mfa WHERE id=1").fetchone()
    return bool(row and row["enabled"])


def verify_owner_totp(code, client_key="owner-action"):
    if not mfa_enabled():
        return False
    now = time.time()
    with _connect() as db:
        row = db.execute(
            "SELECT failures, locked_until FROM mfa_login_attempts WHERE client_key=?",
            (str(client_key),),
        ).fetchone()
        if row and row["locked_until"] and row["locked_until"] > now:
            return False
        if verify_totp(code):
            db.execute("DELETE FROM mfa_login_attempts WHERE client_key=?", (str(client_key),))
            return True
        failures = (row["failures"] if row else 0) + 1
        locked_until = now + 900 if failures >= 5 else None
        db.execute(
            "INSERT INTO mfa_login_attempts(client_key,failures,locked_until) VALUES(?,?,?) "
            "ON CONFLICT(client_key) DO UPDATE SET failures=excluded.failures,locked_until=excluded.locked_until",
            (str(client_key), failures, locked_until),
        )
        return False


def disable_totp():
    with _connect() as db:
        db.execute("DELETE FROM owner_mfa WHERE id=1")


def put_secret(name, value):
    if not isinstance(name, str) or not name.strip() or len(name) > 80:
        raise ValueError("Secret name must be 1-80 characters.")
    if not isinstance(value, str) or not value or len(value) > 10000:
        raise ValueError("Secret value must be 1-10000 characters.")
    ciphertext = _fernet().encrypt(value.encode()).decode()
    with _connect() as db:
        db.execute(
            "INSERT INTO secret_vault(name,ciphertext,updated_at) VALUES(?,?,?) "
            "ON CONFLICT(name) DO UPDATE SET ciphertext=excluded.ciphertext,updated_at=excluded.updated_at",
            (name.strip(), ciphertext, _now()),
        )
    return {"name": name.strip(), "updated_at": _now()}


def get_secret(name):
    with _connect() as db:
        row = db.execute("SELECT ciphertext FROM secret_vault WHERE name=?", (name,)).fetchone()
    if not row:
        return None
    try:
        return _fernet().decrypt(row["ciphertext"].encode()).decode()
    except InvalidToken:
        raise RuntimeError("Vault entry cannot be decrypted. Check APP_ENCRYPTION_KEY.")


def list_secret_metadata():
    initialize()
    with _connect() as db:
        rows = db.execute("SELECT name,updated_at FROM secret_vault ORDER BY name").fetchall()
    return [{"name": row["name"], "updated_at": row["updated_at"]} for row in rows]


def delete_secret(name):
    with _connect() as db:
        cursor = db.execute("DELETE FROM secret_vault WHERE name=?", (name,))
    return cursor.rowcount > 0
