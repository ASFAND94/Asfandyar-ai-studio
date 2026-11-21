# Cloudflare deployment preparation

Status: **prepared, not yet deployable**.

This repository is currently a Windows/local FastAPI application. Do not deploy the existing `main.py` directly to Cloudflare Pages or Workers yet.

## Verified repository facts

- The app is FastAPI and mounts the dashboard from `static/`.
- `auth_manager.py` and `social_account_manager.py` persist data using Python `sqlite3` files.
- `content_manager.py`, `analytics_manager.py`, `keyword_manager.py`, `seo_manager.py`, and `traffic_manager.py` currently keep several records in process memory.
- `main.py` imports `python-dotenv` and the local managers.
- `requirements.txt` includes packages beyond the minimal Cloudflare FastAPI example.
- The current Windows launcher starts Uvicorn on `127.0.0.1`; it is not a Cloudflare Worker entrypoint.

## Why a Wrangler config is intentionally not added yet

Cloudflare supports FastAPI on Python Workers through its ASGI adapter. However, adding a `wrangler.jsonc` file alone would not make this app production-ready:

1. The existing SQLite file-based persistence is not a suitable durable database design for Workers.
2. In-memory content and analytics records would be lost when an isolate is recycled or traffic moves between isolates.
3. The current authentication and social-account storage must be moved to a supported persistent service, with correct transaction and concurrency behavior.
4. The Worker entrypoint must adapt the FastAPI app using `workers.asgi.entrypoint(app)`.
5. Static asset serving must be configured through Workers Static Assets and tested for the current `/app/` routes.
6. All runtime dependencies must be checked against Python Workers compatibility.

Deploying before these changes could expose a broken app or cause user data loss. No secrets, API keys, OAuth credentials, or paid services should be added to Git.

## Recommended zero-cost migration sequence

### Phase 1 — Worker-compatible application shell

- Keep the current Windows/local launcher working.
- Add a separate Cloudflare Worker entrypoint; do not replace the local Uvicorn entrypoint.
- Use Cloudflare's Python Workers ASGI integration for FastAPI.
- Serve `static/` through a Workers Static Assets binding.
- Pin and verify compatible Python dependencies using `pyproject.toml`.

### Phase 2 — Durable storage

- Create a Cloudflare D1 schema for owner credentials, hashed sessions, social-account slots, preferences, content drafts, campaigns, and analytics records.
- Replace direct SQLite file access with a storage interface and a D1 implementation.
- Ensure session and credential handling remains secure; never store raw passwords or provider tokens.
- Keep local SQLite support for Windows development and tests.

### Phase 3 — Validation

- Add automated tests for the D1 repository layer and Worker routes.
- Test setup, login, logout, CSRF, account-slot limits, drafts, campaign records, and analytics.
- Verify that publishing remains disabled by default and owner approval remains required.
- Only then add the production `wrangler.jsonc` and deployment instructions.

## Current product limitations (not solved by deployment)

Cloudflare hosting does not itself add AI content generation, OAuth connections, automatic posting, Blogger publishing, or Adsterra/Monetag earnings APIs. Those require separate implementation and, where applicable, provider approval and credentials. Any paid API or service must remain disabled unless the owner explicitly approves it.

## Official Cloudflare references

- FastAPI on Python Workers: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
- Python Workers: https://developers.cloudflare.com/workers/languages/python/
- Python Workers framework support announcement: https://developers.cloudflare.com/changelog/post/2026-09-02-python-workers-web-framework-support/
