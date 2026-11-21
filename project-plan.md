# Asfandyar AI Studio — project status and roadmap

## Goal
A zero-cost-first, owner-controlled digital marketing workspace. Prefer free tiers and open-source tools. Never enable paid services or external actions without explicit owner approval.

## Implemented project foundation
- FastAPI application and responsive installable Android-style PWA.
- Single-owner first-run setup, login, logout and password change.
- PBKDF2-HMAC-SHA256 password hashing, opaque hashed sessions, HttpOnly/SameSite cookies, CSRF validation, login lockout and security headers.
- Owner-only security activity log and mandatory approval that cannot be disabled.
- Global publishing OFF by default.
- SQLite persistence for content drafts, traffic campaigns, analytics records and social account registry.
- Separate Facebook Profile and Facebook Page registries; ten account slots per supported platform.
- Content draft management, SEO/keyword utilities, traffic campaign planning and manual analytics calculations.
- Blogger publishing endpoint guarded by global publishing switch and owner-approved draft state; requires valid official API access token and blog ID.
- PWA shell, Windows launcher, Dockerfile, Docker Compose persistent volume, deployment notes and backup/restore guide.
- GitHub Actions compilation and automated test workflow.

## Not included / future development
- TOTP authenticator 2FA and encrypted OAuth credential vault.
- Official OAuth connections and platform-specific publishing adapters for Facebook, X, Instagram, YouTube, LinkedIn, TikTok and Pinterest.
- Blogger OAuth authorization-code flow and automatic token refresh.
- AI model provider integration; current AI helper creates prompt/draft content and does not invoke a model API.
- Automated scheduling and background task queue.
- Live Adsterra/Monetag earnings and analytics APIs.
- Automated encrypted off-site backup, monitoring, penetration testing and independent security audit.
- Production hosting account configuration and deployment.

A social account slot is a local record, not an authenticated provider connection. Never collect provider passwords. Never promise that a third-party API is free or available without checking its current policies and limits.

## Next stages
1. Run the full GitHub Actions test suite and fix all failures.
2. Complete MFA and secure secret-vault design with recovery and rotation procedures.
3. Implement official OAuth one provider at a time, beginning with Blogger, only after owner approval.
4. Add AI assistance through an optional free/local model provider, with human review and no automatic external publishing.
5. Add a durable scheduler/queue with idempotency and per-action approval.
6. Add tested backup/restore automation and monitoring.
7. Deploy only to HTTPS hosting with persistent storage and validate recovery before production use.

## Safety
- No bought traffic, fake engagement, spam or policy-violating automation.
- Publishing stays OFF until explicitly enabled by the owner; each sensitive action needs approval.
- Never commit .env, credentials, passwords, setup keys, tokens or database backups.
- Prefer free/open-source options; do not incur charges without explicit owner permission.
