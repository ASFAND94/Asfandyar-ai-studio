# Asfandyar AI Studio

Private, owner-controlled digital marketing manager. The project is designed to prefer free/open-source services and to require the owner's approval before external publishing.

## Security and first-time setup

1. Deploy only behind HTTPS. Do not expose the application directly to the public internet without a TLS reverse proxy and firewall.
2. Copy `env.example` to `.env` on the server. Never upload `.env` to GitHub.
3. Generate a unique one-time setup secret and set it as `ADMIN_SETUP_KEY`:
   `python -c "import secrets; print(secrets.token_urlsafe(48))"`
4. Keep `COOKIE_SECURE=true` in production. Set it to `false` only for local HTTP testing on your own computer.
5. Install requirements and run:
   `pip install -r requirements.txt`
   `uvicorn main:app --host 127.0.0.1 --port 8000`
6. Open `/auth/status` to check whether initial setup is required. Call `POST /auth/setup` once with the setup secret, your chosen username, and a unique password of at least 12 characters.
7. Remove `ADMIN_SETUP_KEY` from the server environment after creating the admin. Then sign in through `POST /auth/login`.
8. The login response includes a CSRF token. Send it in the `X-CSRF-Token` header for every state-changing request. The session cookie is HttpOnly, SameSite=Strict, Secure in production, and expires after eight hours.
9. Change your password through `POST /auth/change-password`. This revokes all active sessions.

## Security controls currently implemented

- One owner/admin account; no public registration.
- Passwords are salted and hashed with PBKDF2-HMAC-SHA256 (310,000 iterations).
- Random session tokens are stored only as SHA-256 digests in SQLite.
- Login lockout after repeated failed attempts.
- CSRF checks on state-changing authenticated requests.
- Security response headers; HTTPS HSTS when served over HTTPS.
- API documentation/OpenAPI routes disabled by default.
- `.env`, local database, caches and secrets excluded from Git.
- Global publishing switch defaults OFF and approval defaults ON.

## Owner controls and social account settings

- Seven social platforms are supported in the account registry: Facebook, Instagram, X, YouTube, LinkedIn, TikTok and Pinterest.
- Each platform has a separate limit of five account slots.
- Each account can have its own owner-selected niche, allowed content formats and publishing preference.
- Publishing is not implemented merely by registering an account. Official OAuth/API access, provider permissions and a secure encrypted token store are required before any real publishing can be enabled.
- Do not paste passwords, access tokens, app secrets or recovery codes into GitHub, chat, or ordinary account fields.

## Important current limitations

This repository is still an MVP/API backend, not a finished hosted dashboard. Some existing content and analytics managers use in-memory storage. OAuth integrations, encrypted provider-token storage, video generation, scheduling, real multi-platform publishing, backups, monitoring and a complete browser login dashboard remain future work and must be tested before production use.

Never use fake traffic, spam, or unauthorized automation. Never spend money without the owner's explicit permission.
