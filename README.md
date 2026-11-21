# Asfandyar AI Studio

Private, owner-controlled digital marketing workspace with a responsive installable Android-style PWA. The project prioritizes free/open-source tools and does not activate paid services. External publishing is disabled by default and requires an authenticated owner action plus an approved draft.

## Included features

- Private single-owner setup, login, logout and password change.
- PBKDF2-HMAC-SHA256 password hashing, random opaque sessions, HttpOnly/SameSite cookies, CSRF checks and login lockout.
- Security response headers, owner-only security activity log and mandatory approval controls.
- SQLite-persisted content drafts, campaign records, analytics and social-account registry.
- Separate Facebook Profile and Facebook Page account types; up to ten account slots per supported platform.
- Content draft management, SEO checks, keyword suggestions, traffic campaign planning and manual analytics with CTR/CPM/RPM.
- Blogger API publishing route, gated by the global OFF switch and explicit draft approval; requires valid private server-side credentials.
- Installable PWA shell with conservative static-asset caching; private API responses are not cached.
- Windows local launcher, Dockerfile, Docker Compose with persistent database volume, deployment and backup instructions.

## Run on Windows

1. Install Python 3.11+ from https://www.python.org/downloads/ and enable **Add Python to PATH**.
2. Download the repository using GitHub **Code → Download ZIP**, then extract it.
3. Double-click `run_windows.bat`. It creates a virtual environment, installs requirements, creates a private local `.env` and starts the server.
4. Keep the one-time setup key printed in the terminal private.
5. Open http://127.0.0.1:8000/app/ and create your owner account with the setup key, a unique username and a strong password of at least 12 characters.
6. Stop the server with Ctrl+C, remove `ADMIN_SETUP_KEY` from the local `.env`, save, then restart with `run_windows.bat`.
7. Keep the terminal open while using the local application.

This launcher binds to localhost and is for local testing. It is not a public internet server.

## Install on Android

The PWA must be served from HTTPS for installation on a real hosted domain (localhost is permitted for local development). Open `/app/` in Chrome on Android, then choose **Install app** or **Add to Home screen** from the browser menu. On iOS, use Safari → Share → Add to Home Screen.

The service worker caches only the static app shell. It does not cache API responses, login sessions, drafts, accounts or analytics. Offline mode does not provide live application functionality. This is an installable web app, not an APK or Play Store release.

## Docker deployment

See [DEPLOYMENT.md](DEPLOYMENT.md). A persistent disk/volume and HTTPS are required for a public deployment. Docker Compose retains data in a named SQLite volume. Do not deploy to an ephemeral filesystem and assume records will survive restarts.

## Tests

Run locally:

```bash
python -m compileall -q .
python -m unittest discover -v
```

GitHub Actions runs compilation, dependency installation and the automated test suite on pushes and pull requests.

## Important integration boundaries

- Social account slots are local registry records, not authenticated social accounts. Social OAuth and provider-specific publishing adapters are not implemented.
- Blogger publishing uses the official API and needs a valid access token and blog ID supplied only through private server environment variables. OAuth refresh flow and an encrypted token vault are not included yet.
- AI content generation currently provides prompt/draft assistance; no paid AI provider is called automatically.
- Adsterra and Monetag earnings are manual analytics records. Live reporting APIs are not connected.
- No automated traffic buying, fake engagement, spam or policy-violating automation is included.
- Hosting free tiers may sleep or lack persistent storage. Verify current host limits/pricing before deployment; no paid service is enabled by this repository.

## Security status

Implemented security controls are an initial foundation, not a third-party audit or a guarantee of security. TOTP authenticator 2FA, encrypted OAuth token vault, automated encrypted off-site backups, external monitoring and penetration testing remain future hardening tasks. Do not enter social passwords into this app. Keep `.env`, database files, setup keys and provider credentials out of GitHub. Rotate any secret that is accidentally exposed.

See [SECURITY.md](SECURITY.md), [DEPLOYMENT.md](DEPLOYMENT.md) and [BACKUP.md](BACKUP.md).
