# Cloudflare deployment readiness — Asfandyar AI Studio

Status: **NOT DEPLOYABLE YET**. This document records the verified blockers before any public deployment.

## Safe repository state

- Original `main` branch has not been modified.
- Snapshot branch: `backup-main-2026-11-21`.
- Work branch: `cloudflare-deploy`.
- Do not merge this branch into `main` until the deployment tests pass.

## What the current application uses

- FastAPI app in `main.py`, with dashboard assets served from `static/`.
- SQLite databases created by `database.py` and `auth_manager.py`.
- Authentication uses PBKDF2-HMAC-SHA256 with 310,000 iterations.
- Several managers keep data in process memory.
- The requirements include packages for Google APIs, Tweepy, Pillow, BeautifulSoup, feedparser, APScheduler, and more.

## Cloudflare compatibility work required

1. Add a Cloudflare Python Worker ASGI entry point and validate all imported packages against the Python Workers runtime.
2. Replace local SQLite file access with a supported persistent service (for example, Cloudflare D1) and redesign database access for the Worker runtime.
3. Move all application state currently held only in process memory into persistent storage.
4. Review password verification against the Free plan's 10 ms CPU budget. The current 310,000-iteration PBKDF2 implementation may exceed it; do not weaken password security just to make deployment pass.
5. Replace or remove unsupported background scheduling and filesystem assumptions. A Worker is not a continuously running Uvicorn server.
6. Add automated tests for setup, login, CSRF, sessions, dashboard assets, and persistent data before public release.
7. Keep all publisher codes, OAuth tokens, passwords, setup keys, and other secrets out of this public GitHub repository. Configure secrets only in the hosting dashboard/CLI.

## Free-plan constraints

Cloudflare Workers Free currently documents 100,000 requests/day and 10 ms CPU time per HTTP request. A successful deployment does not guarantee that every operation will fit within these limits. Do not enable billing or a paid plan without the owner's explicit approval.

## Functional status (do not overstate)

This repository is currently a local MVP. Social account slots are not live OAuth connections; automatic social publishing, scheduled publishing, AI article generation, and live Adsterra/Monetag earnings are not implemented. Blogger publishing and monetization-code management still need separate, tested integrations.

## Next implementation milestone

Build and test the persistence/authentication adapter first, then add the Worker entry point and deployment configuration. Deploy only after local Worker tests pass. Publishing must remain disabled by default and every external publishing action must require owner approval.
