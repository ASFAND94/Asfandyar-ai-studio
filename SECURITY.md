# Security and Owner Control

## Security model
- Single-owner administration. There is no public registration endpoint.
- First-run setup is protected by the one-time `ADMIN_SETUP_KEY` environment secret.
- Admin passwords are stored as PBKDF2-HMAC-SHA256 hashes with random salts (310,000 iterations), never as plaintext.
- Login sessions use cryptographically random opaque tokens; only token hashes are stored in SQLite.
- Session cookie is HttpOnly, SameSite=Strict, eight-hour lifetime, and Secure by default.
- State-changing requests require the CSRF token returned at login in the `X-CSRF-Token` header.
- Five failed password attempts trigger a 15-minute lockout per client IP.
- Optional authenticator-app TOTP MFA encrypts its seed using Fernet and rate-limits failed codes (five failures per client key trigger a 15-minute lockout).
- Password changes revoke every active session.
- Admin routes are protected; health, first-run setup, and login are the only public routes.
- Security response headers are enabled. API docs are disabled by default.

## First-time setup
1. Deploy only behind HTTPS. Keep `COOKIE_SECURE=true`.
2. Create a private `.env` file on the server (never in GitHub).
3. Set a long random `ADMIN_SETUP_KEY` (at least 20 characters).
4. Start the app and send one POST to `/auth/setup` with JSON fields `setup_key`, `username`, and a unique password of at least 12 characters.
5. Immediately remove `ADMIN_SETUP_KEY` from the server environment and restart the app.
6. Log in using POST `/auth/login`. The response includes a CSRF token. Keep it private and send it in `X-CSRF-Token` for POST/PUT/PATCH/DELETE requests.
7. Keep the SQLite database and `.env` file outside public web access. Back up the database securely.

## Important operational requirements
- HTTPS is mandatory for any internet-facing deployment. Do not set `COOKIE_SECURE=false` on a public server.
- Restrict server, hosting, GitHub, and deployment credentials with MFA.
- Keep repository secrets out of commits and rotate any secret accidentally exposed.
- An encrypted generic secret vault is available through the owner-only dashboard/API. It requires APP_ENCRYPTION_KEY and never returns saved secret values from list endpoints. Provider adapters must explicitly read only the needed vault entry; generic vault storage alone does not complete provider OAuth.
- Generate APP_ENCRYPTION_KEY with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Back it up separately from the database. Losing it makes encrypted vault and MFA seeds unrecoverable.
- Enable authenticator MFA from the Security tab after setting APP_ENCRYPTION_KEY. There are no built-in recovery codes in this release; keep the authenticator device and encryption-key backup safe.
- Use a persistent private volume for `asfandyar.db`; ephemeral hosting storage will lose accounts and sessions.
- This is an initial security foundation, not a completed third-party security audit. Test deployment, backups, dependency updates, and hosting configuration before putting real accounts or money at risk.
