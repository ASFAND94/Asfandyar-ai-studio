"""Shared SQLite storage for Asfandyar AI Studio.

Set APP_DB_PATH to a persistent private path in deployment. Never expose this
file through the static web directory or commit it to source control.
"""
import os
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(os.getenv(
    "APP_DB_PATH",
    str(Path(__file__).resolve().parent / "asfandyar.db")
))


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH, timeout=20)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 20000")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                website TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                platform TEXT NOT NULL DEFAULT 'blogger',
                status TEXT NOT NULL DEFAULT 'draft',
                external_post_id TEXT,
                external_url TEXT,
                created_at TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                platform TEXT NOT NULL,
                visitors INTEGER NOT NULL DEFAULT 0,
                pageviews INTEGER NOT NULL DEFAULT 0,
                impressions INTEGER NOT NULL DEFAULT 0,
                clicks INTEGER NOT NULL DEFAULT 0,
                earnings REAL NOT NULL DEFAULT 0
            )
        """)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_content_created ON content(created_at DESC)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date DESC)")


if __name__ == "__main__":
    initialize_database()
    print(f"Asfandyar AI Studio database initialized at {DATABASE_PATH}.")
