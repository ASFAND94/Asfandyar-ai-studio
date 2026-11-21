# Deployment and device setup

## What is ready
This repository contains a FastAPI application, responsive installable PWA, SQLite-backed drafts/campaigns/analytics/social account registry, owner authentication, mandatory approval controls, security event log, tests, Windows launcher and Docker packaging.

**This is not a public SaaS and has not had an independent security audit.** Real third-party integrations require provider approval, OAuth credentials and testing. Never paste credentials into chat or commit them to Git.

## Before any public deployment
1. Use a host that supports a persistent disk/volume. SQLite data must survive restarts. Ephemeral filesystems are not supported for production data.
2. Configure HTTPS at the hosting platform/reverse proxy. Keep `COOKIE_SECURE=true`.
3. Create private environment variables from `env.example`. Set a long random `ADMIN_SETUP_KEY` (at least 32 random bytes) and generate `APP_ENCRYPTION_KEY` with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`. Store the encryption key in a separate secure backup location. Losing it makes vault and MFA secrets unrecoverable. Do not upload `.env`.
4. Set `APP_DB_PATH`, `AUTH_DB_PATH`, and `SOCIAL_DB_PATH` to the same private persistent database path (Docker Compose defaults to `/data/asfandyar.db`).
5. Deploy the container using the included Dockerfile, or use the platform's Python runtime with `pip install -r requirements.txt` and start command `uvicorn main:app --host 0.0.0.0 --port $PORT --proxy-headers`.
6. Open `/auth/status`. Complete the one-time setup with the secret setup key, unique username and a long unique password. Remove `ADMIN_SETUP_KEY` from the hosting environment after setup and restart.
7. Sign in. In the Security tab, enable authenticator-app MFA and confirm it with a current six-digit code. Store the encryption key separately and protect your authenticator device. There are no automatic MFA recovery codes in this release; losing the device may require restoring the encrypted database/key or a documented operator recovery.
8. Verify the security log, create a test draft and campaign, restart the service, and confirm data persists.
8. Configure backups of the persistent volume. Encrypt backups before copying off-site and periodically test restoration.
9. Install the PWA from the HTTPS site using Chrome on Android (browser menu → Install app/Add to Home screen). On desktop use the browser install icon/menu.

## Local Windows use
Install Python 3.11+, download the GitHub ZIP, extract it and run `run_windows.bat`. Keep the terminal open. The app binds to localhost and is intended for local testing. Do not expose this HTTP development server to the internet.

## Docker Compose
- Create a private `.env` beside `docker-compose.yml`.
- Set `ADMIN_SETUP_KEY` to a random one-time value and `COOKIE_SECURE=true`.
- Run `docker compose up --build -d`.
- Inspect logs with `docker compose logs -f`.
- Stop with `docker compose down`. The named volume is retained; `docker compose down -v` deletes it and must not be used unless you intend to erase the database.

## Free-tier warning
A free hosting tier may sleep, have limits, or lack persistent storage. Do not deploy this SQLite configuration to an ephemeral free host and assume records are safe. Always verify the host's current persistent-volume policy and pricing. No paid plan is enabled by this project.

## Known integration boundaries
- Blogger publishing uses the official API only and needs a valid server-side access token and blog ID. OAuth token refresh and secure token vault are not yet included.
- Social account slots are local records, not authenticated provider connections. No social platform credentials are accepted in the UI.
- AI text generation currently prepares prompts/drafts; no paid AI API is called.
- Adsterra/Monetag earnings are manual records; live earnings APIs are not connected.
- TOTP authenticator MFA and a generic Fernet-encrypted secret vault are implemented. Provider-specific OAuth token refresh, rotation and adapter integration remain future work. MFA recovery codes are not implemented; keep your authenticator device and encryption key safe. Password/session/CSRF/approval controls are implemented, but the app is not independently security-audited.
