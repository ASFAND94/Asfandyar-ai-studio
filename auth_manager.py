"""Single-owner authentication and session security for Asfandyar AI Studio.

Secrets are supplied only through environment variables. Never commit .env,
passwords, setup keys, session tokens, or provider access tokens to GitHub.
"""
import hashlib
import hmac
import os
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "asfandyar.db"
SESSION_COOKIE = "asfandyar_admin_session"
SESSION_HOURS = 8
PBKDF2_ITERATIONS = 310_000
MAX_LOGIN_FAILURES = 5
LOCKOUT_MINUTES = 15


def utc_now():
    return datetime.now(timezone.utc)


def utc_text(value):
    return value.isoformat()


def password_hash(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return salt.hex() + "$" + derived.hex()


def verify_password(password, stored_hash):
    try:
        salt_hex, expected_hex = stored_hash.split("$", 1)
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex),
            PBKDF2_ITERATIONS
        ).hex()
        return hmac.compare_digest(actual, expected_hex)
    except (ValueError, TypeError):
        return False


def token_digest(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class AuthManager:
    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.initialize()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.db_path, timeout=15)
        connection.row_factory = sqlite3.Row
        try:
            connection.execute("PRAGMA busy_timeout = 15000")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self):
        with self.connect() as db:
            db.execute("""
                CREATE TABLE IF NOT EXISTS admin_user (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS admin_sessions (
                    token_hash TEXT PRIMARY KEY,
                    csrf_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """)
            db.execute("""
                CREATE TABLE IF NOT EXISTS login_attempts (
                    client_key TEXT PRIMARY KEY,
                    failures INTEGER NOT NULL DEFAULT 0,
                    locked_until TEXT
                )
            """)

    def is_configured(self):
        with self.connect() as db:
            return db.execute("SELECT 1 FROM admin_user WHERE id = 1").fetchone() is not None

    def setup(self, setup_key, username, password):
        expected = os.getenv("ADMIN_SETUP_KEY", "")
        if not expected or not hmac.compare_digest(setup_key, expected):
            raise PermissionError("Invalid one-time setup key.")
        if len(username.strip()) < 3 or len(username) > 80:
            raise ValueError("Username must be 3 to 80 characters.")
        if len(password) < 12 or len(password) > 256:
            raise ValueError("Password must be 12 to 256 characters.")
        now = utc_text(utc_now())
        with self.connect() as db:
            if db.execute("SELECT 1 FROM admin_user WHERE id = 1").fetchone():
                raise FileExistsError("Admin account is already configured.")
            db.execute(
                "INSERT INTO admin_user (id, username, password_hash, created_at, updated_at) VALUES (1, ?, ?, ?, ?)",
                (username.strip(), password_hash(password), now, now)
            )

    def login(self, username, password, client_key):
        now = utc_now()
        with self.connect() as db:
            attempt = db.execute(
                "SELECT failures, locked_until FROM login_attempts WHERE client_key = ?",
                (client_key,)
            ).fetchone()
            if attempt and attempt["locked_until"]:
                if datetime.fromisoformat(attempt["locked_until"]) > now:
                    raise TimeoutError("Too many failed attempts. Try again later.")

            user = db.execute(
                "SELECT username, password_hash FROM admin_user WHERE id = 1"
            ).fetchone()
            valid = bool(user and hmac.compare_digest(user["username"], username)
                         and verify_password(password, user["password_hash"]))
            if not valid:
                failures = (attempt["failures"] if attempt else 0) + 1
                locked_until = (
                    utc_text(now + timedelta(minutes=LOCKOUT_MINUTES))
                    if failures >= MAX_LOGIN_FAILURES else None
                )
                db.execute("""
                    INSERT INTO login_attempts (client_key, failures, locked_until)
                    VALUES (?, ?, ?)
                    ON CONFLICT(client_key) DO UPDATE SET
                        failures=excluded.failures, locked_until=excluded.locked_until
                """, (client_key, failures, locked_until))
                return None

            db.execute("DELETE FROM login_attempts WHERE client_key = ?", (client_key,))
            raw_session = secrets.token_urlsafe(48)
            raw_csrf = secrets.token_urlsafe(32)
            db.execute("""
                INSERT INTO admin_sessions (token_hash, csrf_hash, created_at, expires_at)
                VALUES (?, ?, ?, ?)
            """, (
                token_digest(raw_session), token_digest(raw_csrf),
                utc_text(now), utc_text(now + timedelta(hours=SESSION_HOURS))
            ))
            return {"session": raw_session, "csrf": raw_csrf, "username": user["username"]}

    def validate_session(self, raw_session):
        if not raw_session:
            return None
        with self.connect() as db:
            row = db.execute("""
                SELECT token_hash, csrf_hash, expires_at FROM admin_sessions
                WHERE token_hash = ?
            """, (token_digest(raw_session),)).fetchone()
            if not row:
                return None
            if datetime.fromisoformat(row["expires_at"]) <= utc_now():
                db.execute("DELETE FROM admin_sessions WHERE token_hash = ?",
                           (row["token_hash"],))
                return None
            return {"token_hash": row["token_hash"], "csrf_hash": row["csrf_hash"]}

    def validate_csrf(self, session, csrf_token):
        return bool(
            session and csrf_token and
            hmac.compare_digest(session["csrf_hash"], token_digest(csrf_token))
        )

    def logout(self, raw_session):
        if raw_session:
            with self.connect() as db:
                db.execute("DELETE FROM admin_sessions WHERE token_hash = ?",
                           (token_digest(raw_session),))

    def change_password(self, raw_session, current_password, new_password):
        if len(new_password) < 12 or len(new_password) > 256:
            raise ValueError("New password must be 12 to 256 characters.")
        session = self.validate_session(raw_session)
        if not session:
            raise PermissionError("Session expired.")
        now = utc_text(utc_now())
        with self.connect() as db:
            user = db.execute(
                "SELECT password_hash FROM admin_user WHERE id = 1"
            ).fetchone()
            if not user or not verify_password(current_password, user["password_hash"]):
                raise PermissionError("Current password is incorrect.")
            db.execute(
                "UPDATE admin_user SET password_hash = ?, updated_at = ? WHERE id = 1",
                (password_hash(new_password), now)
            )
            db.execute("DELETE FROM admin_sessions")
        return True
