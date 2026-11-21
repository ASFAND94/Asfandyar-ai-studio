# Cloudflare deployment preparation

Status: **Cloudflare Worker shell and D1 social repository added; full dashboard is not yet ready to deploy.**

All changes are on the `cloudflare-deployment-prep` branch. The default `main` branch remains unchanged.

## Verified repository facts

- The existing application is a FastAPI service with a dashboard in `static/`.
- `auth_manager.py` and `social_account_manager.py` use local Python `sqlite3` files.
- Content drafts, campaigns, and analytics currently use process memory.
- The existing `main.py` creates the SQLite managers at import time, so it must not be imported by the Worker until those managers have been migrated.
- The local Windows/Uvicorn workflow should remain supported.

## Added in this branch

- `migrations/0001_initial.sql`: initial D1 schema for owner authentication, sessions, login attempts, social account slots/preferences, owner controls, content drafts, campaigns, and analytics.
- `cloudflare_d1.py`: async D1 adapter using prepared statements and bound parameters. It obtains the D1 binding from FastAPI's documented ASGI request scope (`request.scope["env"]`).
- `cloudflare_social_repository.py`: async D1-backed social-account repository, kept separate from the local SQLite manager.
- `cloudflare_marketing_repository.py`: async D1 repositories for content drafts, traffic campaign plans, and manual analytics.
- `cloudflare_app.py`: isolated FastAPI worker shell with basic health endpoints; it does not import the current SQLite-backed `main.py`.
- `cloudflare_worker.py`: Python Worker entrypoint using Cloudflare's documented `asgi.fetch(app, request, self.env)` pattern.
- `pyproject.toml`: minimal Python Workers dependency manifest, separate from the local Windows `requirements.txt`.
- Tests for the D1 adapter, social repository behavior, marketing repositories, and Worker shell.
- The initial D1 SQL migration was executed against a local SQLite engine for syntax/schema validation; this does not replace a real Cloudflare D1 migration test.

## Important scope boundary

The new D1 social repository is not wired into the existing dashboard routes yet. Authentication, content, campaign, and analytics still need their own durable D1 repositories and route wiring. The Cloudflare shell currently exposes health checks only; it is not the full dashboard.

The existing SQLite database is not automatically copied to D1. Before switching, create a backup and implement/verify an explicit data migration.

## Next implementation steps

1. Run the GitHub Actions tests and resolve any failures.
2. Test the D1 adapter and Worker entrypoint with Cloudflare's local runtime (PyWrangler), not only fake bindings.
3. Add D1-backed authentication while preserving the current PBKDF2 password hashing, hashed session tokens, lockout, and CSRF protections.
4. Wire the D1 social repository into API routes and test account limits and owner controls.
5. Wire the content, campaign, and analytics repositories into API routes; verify insert IDs and persistence across Worker restarts.
6. Migrate authentication carefully. Benchmark the current PBKDF2-HMAC-SHA256 310,000-iteration verification under the free Worker CPU limits before choosing the runtime implementation; do not weaken password hashing just to make it fit.
7. Configure Workers Static Assets so the current dashboard paths work correctly.
8. Create the actual D1 database in the owner's Cloudflare account, then place its real database ID into the Wrangler configuration. Do not invent or commit a placeholder ID.
9. Only after local Worker smoke tests pass, prepare a deployment. No deployment has been performed.

## Runtime and security notes

Cloudflare's FastAPI guide demonstrates a WorkerEntrypoint calling `await asgi.fetch(app, request, self.env)`; the ASGI scope exposes the environment as `request.scope["env"]`. The D1 Python guide documents `await self.env.DB.prepare(...).bind(...).run()`. The code follows these documented patterns, but a real PyWrangler/D1 smoke test is still required.

- Publishing remains OFF by default; owner approval remains required.
- Never commit `.env`, setup keys, passwords, session tokens, OAuth tokens, or provider credentials.
- The D1 migration does not add live OAuth, social posting, Blogger publishing, AI generation, or Adsterra/Monetag earnings APIs.
- Cloudflare has free usage allowances, but quotas and possible overages must be checked in the account before deployment. Do not enable paid billing or paid services without explicit owner approval.

## Official references

- FastAPI on Python Workers: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
- Query D1 from Python Workers: https://developers.cloudflare.com/d1/examples/query-d1-from-python-workers/
- D1 binding API: https://developers.cloudflare.com/d1/worker-api/d1-database/
- Python Workers: https://developers.cloudflare.com/workers/languages/python/
