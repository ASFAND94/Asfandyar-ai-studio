# Asfandyar AI Studio

Private, owner-controlled digital marketing workspace with an installable Android-style PWA. The project prioritizes free/open-source tools and does not activate paid services. External publishing is OFF by default and every publish action requires owner approval.

## Implemented

- FastAPI backend and responsive installable PWA.
- Single-owner setup/login/logout/password change.
- PBKDF2-HMAC-SHA256 password hashes, opaque sessions, HttpOnly/SameSite cookies, CSRF validation and login lockouts.
- Optional authenticator-app TOTP MFA with failed-code throttling.
- Fernet-encrypted credential vault; vault lists expose metadata only.
- Owner-only security activity log and mandatory publishing approval.
- SQLite persistence for drafts, campaigns, analytics and social-account registry.
- Facebook Profile and Facebook Page separate account slots, with up to ten slots per platform.
- Content drafts, SEO/keyword checks, campaign planning and manual CTR/CPM/RPM analytics.
- Official Blogger API publishing adapter using private environment credentials or encrypted vault entries. Google OAuth consent and refresh-token lifecycle are not yet included.
- Optional local AI generation through Ollama. No paid AI API is called.
- Encrypted SQLite backup and integrity-checked restore scripts.
- PWA shell, Windows launcher, Dockerfile and Docker Compose persistent volume.
- Optional Docker Compose Ollama profile for self-hosted local AI.
- GitHub Actions compilation and automated tests.

## Windows local setup

1. Install Python 3.11+ from https://www.python.org/downloads/ and enable **Add Python to PATH**.
2. Download this branch with GitHub **Code → Download ZIP**, then extract it.
3. Run `run_windows.bat`. It installs dependencies and creates a private local `.env`.
4. Keep the one-time setup key and encryption key printed by setup_local.py private. Store a separate backup of the encryption key; without it, saved vault/MFA secrets cannot be decrypted.
5. Open http://127.0.0.1:8000/app/ and create the owner account using the one-time setup key, a unique username and a strong password of at least 12 characters.
6. Stop the app, remove `ADMIN_SETUP_KEY` from `.env`, save, then restart. Keep `APP_ENCRYPTION_KEY`.
7. In the Security tab, enroll your authenticator app and confirm with its current six-digit code.

The Windows launcher binds to localhost for local testing only. It is not a public internet server.

## Install on Android

For a hosted install, use an HTTPS domain. Open `/app/` in Chrome on Android and choose **Install app** or **Add to Home screen**. The service worker caches only static shell assets, not private API data. Offline mode does not provide live app functionality. This is a PWA, not an APK or Play Store release.

## Optional local AI (free/open source)

Install Ollama and pull a model, for example `ollama pull llama3.2:3b`. Keep Ollama running and set `OLLAMA_BASE_URL` and `OLLAMA_MODEL` in the private environment. With Docker Compose, start the optional AI profile using `docker compose --profile ai up --build -d`, then run `docker compose exec ollama ollama pull llama3.2:3b`. CPU inference can be slow and needs RAM/disk. If Ollama is unavailable, the app reports that no local model is available; it never falls back to a paid provider.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md). Public deployment requires HTTPS, private environment variables and a persistent disk/volume. Do not use an ephemeral free host for SQLite data unless its persistence guarantees are confirmed.

Before public launch:
- Generate and securely back up `APP_ENCRYPTION_KEY`.
- Set a long random `ADMIN_SETUP_KEY`; remove it after first owner setup.
- Use a unique strong owner password and enable TOTP MFA.
- Configure persistent storage for `APP_DB_PATH`, `AUTH_DB_PATH` and `SOCIAL_DB_PATH`.
- Test `/health`, `/ready`, backup and restore.
- Keep publishing OFF until provider integrations and permissions are validated.

## Encrypted backup and restore

Create a backup with `python scripts/backup_database.py /secure-location/asfandyar.backup.enc`. Restore with the app stopped using `python scripts/restore_database.py /secure-location/asfandyar.backup.enc`. See [BACKUP.md](BACKUP.md). Store backup files separately from the encryption key.

## Tests

```bash
python -m compileall -q .
python -m unittest discover -v
```

GitHub Actions runs the same compilation and automated test suite.

## Not yet implemented / external dependencies

- Social account records are not authenticated platform connections. Facebook, Instagram, X, YouTube, LinkedIn, TikTok and Pinterest require their official OAuth apps, permissions, review/approval and platform-specific publishing adapters.
- Blogger uses the official API, but Google OAuth authorization-code consent and automatic refresh-token lifecycle still need completion. A valid private access token and blog ID are required.
- Adsterra and Monetag live earnings APIs are not connected; earnings are manual analytics entries.
- Background scheduler/queue and unattended campaign automation are not implemented.
- Built-in MFA recovery codes are not included. Keep your authenticator device and encryption-key backup safe.
- Independent security audit, penetration test and external monitoring are not included.

No fake engagement, bought traffic, spam or policy-violating automation is included. Never commit `.env`, database files, backups, setup keys, encryption keys or provider credentials. This is a deployment candidate, not an independently audited production service.

See [SECURITY.md](SECURITY.md), [FINAL_DEPLOYMENT_CHECKLIST.md](FINAL_DEPLOYMENT_CHECKLIST.md), [DEPLOYMENT.md](DEPLOYMENT.md) and [BACKUP.md](BACKUP.md).
