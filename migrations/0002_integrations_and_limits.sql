-- Enforce the advertised account slot limit at the database boundary.
CREATE TRIGGER IF NOT EXISTS enforce_social_account_slot_limit
BEFORE INSERT ON social_accounts
WHEN (SELECT COUNT(*) FROM social_accounts WHERE platform = NEW.platform) >= 10
BEGIN
    SELECT RAISE(ABORT, 'maximum of 10 account slots per platform reached');
END;

-- Per-provider monetization link settings. Disabled until owner enables them.
CREATE TABLE IF NOT EXISTS monetization_link_settings (
    provider TEXT PRIMARY KEY CHECK (provider IN ('adsterra', 'monetag')),
    direct_link_url TEXT NOT NULL DEFAULT '',
    placement TEXT NOT NULL DEFAULT 'end_article'
        CHECK (placement IN ('after_intro', 'mid_article', 'end_article')),
    enabled INTEGER NOT NULL DEFAULT 0 CHECK (enabled IN (0, 1)),
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO monetization_link_settings(provider, direct_link_url, placement, enabled)
VALUES ('adsterra', '', 'end_article', 0),
       ('monetag', '', 'end_article', 0);

CREATE TABLE IF NOT EXISTS blogger_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    blog_url TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO blogger_settings(id, blog_url) VALUES (1, '');
