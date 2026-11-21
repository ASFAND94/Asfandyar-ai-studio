import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parent / "asfandyar.db"

SUPPORTED_PLATFORMS = {
    "facebook", "instagram", "x", "youtube",
    "linkedin", "tiktok", "pinterest", "threads"
}
MAX_ACCOUNTS_PER_PLATFORM = 5


class SocialAccountManager:
    """Keeps a separate maximum of five account slots for each platform.

    This registry stores account labels and connection status only.
    OAuth tokens/secrets must be added later through each provider's
    official OAuth flow and stored encrypted; never accept passwords here.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.initialize()

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        with self.connect() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS social_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    account_name TEXT NOT NULL,
                    account_handle TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'not_connected',
                    provider_account_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(platform, account_handle)
                )
            """)

    def add_account(self, platform, account_name, account_handle):
        platform = platform.strip().lower()
        account_name = account_name.strip()
        account_handle = account_handle.strip()

        if platform not in SUPPORTED_PLATFORMS:
            raise ValueError("Unsupported platform.")
        if not account_name or not account_handle:
            raise ValueError("Account name and handle are required.")

        with self.connect() as connection:
            count = connection.execute(
                "SELECT COUNT(*) FROM social_accounts WHERE platform = ?",
                (platform,)
            ).fetchone()[0]

            if count >= MAX_ACCOUNTS_PER_PLATFORM:
                raise OverflowError(
                    f"{platform} already has the maximum of "
                    f"{MAX_ACCOUNTS_PER_PLATFORM} account slots."
                )

            try:
                cursor = connection.execute("""
                    INSERT INTO social_accounts
                    (platform, account_name, account_handle, status)
                    VALUES (?, ?, ?, 'not_connected')
                """, (platform, account_name, account_handle))
            except sqlite3.IntegrityError:
                raise ValueError("This account handle is already registered.")

            row = connection.execute(
                "SELECT * FROM social_accounts WHERE id = ?",
                (cursor.lastrowid,)
            ).fetchone()
            return dict(row)

    def list_accounts(self, platform=None):
        with self.connect() as connection:
            if platform:
                platform = platform.strip().lower()
                if platform not in SUPPORTED_PLATFORMS:
                    raise ValueError("Unsupported platform.")
                rows = connection.execute(
                    "SELECT * FROM social_accounts WHERE platform = ? ORDER BY id",
                    (platform,)
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM social_accounts ORDER BY platform, id"
                ).fetchall()
            return [dict(row) for row in rows]

    def account_limits(self):
        accounts = self.list_accounts()
        result = {}
        for platform in sorted(SUPPORTED_PLATFORMS):
            used = sum(1 for item in accounts if item["platform"] == platform)
            result[platform] = {
                "used": used,
                "limit": MAX_ACCOUNTS_PER_PLATFORM,
                "available": MAX_ACCOUNTS_PER_PLATFORM - used,
            }
        return result

    def remove_account(self, account_id):
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM social_accounts WHERE id = ?",
                (account_id,)
            )
            return cursor.rowcount > 0
