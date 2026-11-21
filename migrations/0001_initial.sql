-- Asfandyar AI Studio: initial durable schema for Cloudflare D1.
-- Apply with: npx wrangler d1 migrations apply asfandyar-ai-studio-db --remote
-- No passwords, API keys, OAuth tokens, or personal data belong in this file.

CREATE TABLE IF NOT EXISTS admin_user (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admin_sessions (
    token_hash TEXT PRIMARY KEY,
    csrf_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_admin_sessions_expires
    ON admin_sessions(expires_at);

CREATE TABLE IF NOT EXISTS login_attempts (
    client_key TEXT PRIMARY KEY,
    failures INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT
);

CREATE TABLE IF NOT EXISTS social_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    account_name TEXT NOT NULL,
    account_handle TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'not_connected',
    provider_account_id TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, account_handle)
);

CREATE INDEX IF NOT EXISTS idx_social_accounts_platform
    ON social_accounts(platform, id);

CREATE TABLE IF NOT EXISTS social_account_preferences (
    account_id INTEGER PRIMARY KEY,
    niche TEXT NOT NULL DEFAULT '',
    content_formats TEXT NOT NULL DEFAULT '["post"]',
    publishing_enabled INTEGER NOT NULL DEFAULT 0 CHECK (publishing_enabled IN (0, 1)),
    require_approval INTEGER NOT NULL DEFAULT 1 CHECK (require_approval IN (0, 1)),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(account_id) REFERENCES social_accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS owner_control_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL
);

INSERT OR IGNORE INTO owner_control_settings(setting_key, setting_value)
VALUES ('global_publishing_enabled', 'false'),
       ('require_approval', 'true');

CREATE TABLE IF NOT EXISTS content_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'blogger',
    status TEXT NOT NULL DEFAULT 'draft',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_content_drafts_created
    ON content_drafts(created_at DESC);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    platform TEXT NOT NULL,
    website_url TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_date TEXT NOT NULL,
    platform TEXT NOT NULL,
    visitors INTEGER NOT NULL DEFAULT 0 CHECK (visitors >= 0),
    pageviews INTEGER NOT NULL DEFAULT 0 CHECK (pageviews >= 0),
    impressions INTEGER NOT NULL DEFAULT 0 CHECK (impressions >= 0),
    clicks INTEGER NOT NULL DEFAULT 0 CHECK (clicks >= 0),
    earnings REAL NOT NULL DEFAULT 0 CHECK (earnings >= 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_analytics_date_platform
    ON analytics_records(record_date, platform);
