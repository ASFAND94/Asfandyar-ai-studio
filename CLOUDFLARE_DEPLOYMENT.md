# Cloudflare deployment preparation

Status: **Cloudflare backend and dashboard integration are implemented in this branch, but a live deployment is NOT verified or ready to enable until the owner's D1 database ID, setup secret, and free-tier authentication benchmark are resolved.**

All changes are on `cloudflare-deployment-prep`. The default `main` branch remains unchanged. Draft PR #4 remains open and unmerged.

## Implemented in this branch

- `cloudflare_worker.py`: Cloudflare Python Worker entrypoint using the official `workers.asgi.entrypoint(app)` adapter.
- `cloudflare_app.py`: separate Cloudflare FastAPI application. It does not import the local SQLite-backed `main.py`.
- `cloudflare_d1.py`: async D1 adapter using prepared statements and bound parameters, reading the documented ASGI `request.scope["env"]` binding.
- `migrations/0001_initial.sql`: owner authentication/session tables, login attempts, social accounts/preferences, owner controls, content drafts, campaigns, analytics.
- `migrations/0002_integrations_and_limits.sql`: database-enforced 10-slot-per-platform limit, Blogger URL settings, and separate Adsterra/Monetag link settings (both disabled by default).
- `cloudflare_social_repository.py`: persistent social account registry, account limits, preferences and owner controls.
- `cloudflare_marketing_repository.py`: persistent content drafts, campaign plans, manual analytics, Blogger settings, and separate Monetag/Adsterra URL settings.
- `cloudflare_app.py` API routes: owner setup/login/logout/password change, session and CSRF checks, account management, content drafts, SEO/keyword analysis, campaign plans, analytics and integration settings.
- Blogger drafts receive enabled HTTPS Adsterra/Monetag links at the owner's selected position. This only changes the saved draft HTML; it does not publish the post to Blogger.
- `static/manifest.webmanifest` and `static/sw.js`: installable PWA metadata and offline caching for the dashboard shell. API calls still require a network connection.
- `wrangler.jsonc.example`: Cloudflare Worker + Static Assets + D1 configuration template.
- Tests cover the D1 repositories with SQLite stand-ins and validate the SQL migrations locally. These are not a substitute for running PyWrangler and real D1.

## What is not connected yet

- Official OAuth connections and actual publishing to Facebook, Instagram, TikTok, YouTube, LinkedIn, X or Pinterest.
- Blogger API authentication and actual post creation/updates.
- Live Adsterra or Monetag earnings/analytics APIs. The dashboard only stores the owner's Direct Link URLs and manual analytics.
- AI content generation using an external model API.
- A persistent content calendar, background scheduler, retries, and automatic multi-account posting.
- Import of the existing local SQLite database into D1.

Do not describe an account slot as a connected account, a saved campaign as a running campaign, or a draft as a published post.

## Important zero-cost deployment blocker

Cloudflare Workers Free currently lists a **10 ms CPU limit per request**. This app preserves the local app's PBKDF2-HMAC-SHA256 password hash at 310,000 iterations. That password verification may exceed 10 ms; it has not been benchmarked in PyWrangler. Do not lower the password hashing work factor just to force it onto the free plan. Before public deployment, benchmark setup/login on the actual free Worker runtime. If it exceeds the free CPU limit, keep the app local or adopt a properly reviewed free authentication alternative; do not enable a paid plan without explicit owner approval.

Cloudflare's published Workers Free request allowance is 100,000 requests/day. D1 has separate quotas/limits. Check the current account dashboard before deployment and do not enable paid billing. See official limits and pricing references below.

## Required owner-side setup before deployment

1. In Cloudflare, create a D1 database named `asfandyar-ai-studio-db`.
2. Copy the real database ID into a local copy of `wrangler.jsonc.example`, save it as `wrangler.jsonc`, and never commit any secrets.
3. Set `ADMIN_SETUP_KEY` as a Worker secret using Wrangler/Cloudflare dashboard. Never put it in source control.
4. Install `uv` and Node.js on the Windows laptop, then run `uv sync` and `uv run pywrangler dev`.
5. Apply migrations to the local D1 emulator first, verify `/health/storage`, test owner setup/login and the full dashboard, then benchmark password hashing.
6. Only if every check passes and the free-tier CPU constraint is met, apply migrations remotely and deploy. No deployment or remote database creation has been performed by this repository change.

Example commands (after creating the real D1 database and local `wrangler.jsonc`):
```powershell
uv sync
uv run pywrangler dev
npx wrangler d1 migrations apply asfandyar-ai-studio-db --local
# Remote migration and deploy are intentionally deferred until tests pass:
# npx wrangler d1 migrations apply asfandyar-ai-studio-db --remote
# uv run pywrangler deploy
```

## Security and safety

- One owner; no public registration.
- PBKDF2-HMAC-SHA256 password hashing, random sessions stored as SHA-256 digests, login lockout, HttpOnly/Secure/SameSite cookies and CSRF validation.
- Publishing is OFF globally and per account by default; owner approval is ON.
- OAuth credentials and API keys are not stored in the new settings tables.
- Never commit `.env`, setup keys, passwords, session tokens, OAuth tokens or provider credentials.
- Do not enable automatic publishing until official provider OAuth, permissions, idempotency and a tested approval workflow exist.

## Official references

- FastAPI on Python Workers: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
- Python Workers: https://developers.cloudflare.com/workers/languages/python/
- Query D1 from Python Workers: https://developers.cloudflare.com/d1/examples/query-d1-from-python-workers/
- D1 migrations: https://developers.cloudflare.com/d1/reference/migrations/
- D1 foreign keys: https://developers.cloudflare.com/d1/sql-api/foreign-keys/
- Workers Free limits: https://developers.cloudflare.com/workers/platform/limits/
