# Cloudflare deployment preparation

Status: **D1 foundation added; full Worker deployment is not yet ready.**

The work is being developed on the `cloudflare-deployment-prep` branch. The default `main` branch has not been changed.

## Repository findings

- The application is a FastAPI service with a dashboard in `static/`.
- `auth_manager.py` and `social_account_manager.py` currently use local Python `sqlite3` files.
- Content drafts, campaigns, and analytics are currently held in process memory.
- The current `main.py` constructs those managers at import time. It must not be imported in a Worker until those constructors use a supported durable storage implementation.
- The local Windows/Uvicorn workflow should remain supported.

## Added in this branch

- `migrations/0001_initial.sql`: initial D1 tables for owner authentication, sessions, login attempts, social account slots/preferences, owner controls, content drafts, campaigns, and analytics.
- `cloudflare_d1.py`: a small asynchronous D1 binding adapter using prepared statements and bound parameters.
- `tests/test_cloudflare_d1_helpers.py`: isolated unit tests using a fake D1 binding.

These files are groundwork only. The existing managers do not use this adapter yet, and existing SQLite data is not automatically migrated.

## Next implementation steps

1. Run the unit tests and validate the adapter against the actual Python Workers runtime.
2. Define storage interfaces and implement D1-backed authentication and social-account repositories. Preserve the local SQLite implementation for Windows.
3. Move content, campaign, and analytics records from process memory to durable repositories.
4. Refactor application construction so importing the Worker entrypoint does not create local database files.
5. Add a separate FastAPI Worker entrypoint using `workers.asgi.entrypoint(app)`.
6. Configure Workers Static Assets for the existing `/app/` dashboard paths and configure the D1 binding only after the Cloudflare database is created.
7. Add a real local Worker smoke test and CI checks before deployment.

## Important runtime notes

Cloudflare's Python Workers documentation shows D1 access through the Worker environment binding, for example `self.env.DB.prepare(...)`. FastAPI applications can access the Worker environment through the ASGI request scope. The adapter follows the request-scope pattern but still requires a real-runtime smoke test before it is considered production-verified.

The official FastAPI guide requires a Python Workers entrypoint and a `pyproject.toml`; it also documents static assets through the `ASSETS` binding. Do not add a fake database ID or deploy configuration with placeholders.

## Security and product limits

- Publishing stays disabled by default; owner approval remains required.
- Never commit `.env`, setup keys, passwords, session tokens, OAuth tokens, or provider credentials.
- A D1 migration does not add live OAuth, social posting, Blogger publishing, AI generation, or Adsterra/Monetag earnings APIs.
- Cloudflare hosting and D1 have free usage allowances, but limits and overages must be checked in the account before deployment. Do not enable paid billing or paid services without explicit owner approval.

## Official references

- FastAPI on Python Workers: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
- Query D1 from Python Workers: https://developers.cloudflare.com/d1/examples/query-d1-from-python-workers/
- Python Workers: https://developers.cloudflare.com/workers/languages/python/
