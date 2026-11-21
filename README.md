# Asfandyar AI Studio

Private, owner-controlled digital marketing workspace. Built to prefer free/open-source tools. Publishing stays OFF by default and nothing is sent to external platforms by this MVP.

## Run on Windows

1. Install Python 3.11+ from https://www.python.org/downloads/ and enable **Add Python to PATH**.
2. Download this repository with GitHub **Code → Download ZIP**, then extract it.
3. Double-click `run_windows.bat`. It creates a virtual environment, installs dependencies, creates a local `.env` and starts the server.
4. Copy the one-time setup key printed in the terminal. Keep it private.
5. Open http://127.0.0.1:8000/app/ in your browser.
6. Create the owner account using the setup key, a username and a password of at least 12 characters.
7. After successful setup, stop the server with Ctrl+C. Open `.env`, remove the `ADMIN_SETUP_KEY=...` line, save, then run `run_windows.bat` again.
8. Sign in with your owner username and password.

Keep the terminal open while using the dashboard. The local server is only accessible from your computer.

## Install as an Android-style app (PWA)

The dashboard now includes a Progressive Web App shell. When served from **HTTPS** (or localhost for local testing), supported browsers can install it from the browser's install prompt or menu.

1. Open the dashboard at `/app/` in Chrome on Android.
2. Sign in to your private owner workspace.
3. If the **Install app** button appears, tap it. Otherwise open Chrome's ⋮ menu and choose **Install app** or **Add to Home screen**.
4. Launch Asfandyar AI Studio from the new home-screen icon.

On iPhone/iPad, open the site in Safari, tap Share, then **Add to Home Screen**. Browser support and wording can vary.

The service worker caches only the static app shell (HTML, CSS, JavaScript, manifest and icon). It does **not** cache API responses, login sessions, drafts, account records, analytics or other private data. Offline mode therefore provides the app shell only; signing in and using live features still requires the server and a network connection. This is an installable web app, not a Play Store APK.

## Dashboard modules

- Private owner login, logout and password change.
- Separate Facebook Profile and Facebook Page registries.
- Ten independent account slots per supported platform: Facebook Profile, Facebook Page, Instagram, X, YouTube, LinkedIn, TikTok and Pinterest.
- Per-account niche, content formats and approval preferences.
- Global publishing safety switch (OFF by default).
- Save and review content drafts.
- Basic SEO and keyword analysis.
- Traffic campaign planning.
- Manual analytics record entry and summary.

## Important limitations

This is a local MVP and test dashboard, not a complete automation service. Registering an account slot does **not** connect or authenticate a social account. Official OAuth, encrypted token storage, provider permissions and platform-specific publishing adapters are not implemented. The dashboard does not yet generate AI content, publish to Blogger/social platforms, schedule posts, or fetch live Adsterra/Monetag earnings. SEO/keyword and analytics functions are starter utilities/manual records, not live third-party data.

Do not enter social passwords or API tokens into this app. Do not use it for public production hosting. Real publishing requires official API access and platform policy compliance. Never buy traffic, generate fake engagement, or spam. No paid service should be enabled without the owner's explicit permission.

## Tests

```bat
.venv\Scripts\python.exe -m unittest discover -v
```

GitHub Actions runs dependency installation, compilation, unit tests and API smoke tests on pushes.

## Security

- One owner account; no public registration.
- Passwords are salted and hashed with PBKDF2-HMAC-SHA256 (310,000 iterations).
- Random session tokens are stored only as SHA-256 digests; session cookies are HttpOnly and SameSite=Strict.
- Login is temporarily locked after five failed attempts for the client key.
- State-changing API calls require CSRF validation.
- Security headers include CSP, frame denial, no-sniff, no-referrer, restrictive Permissions Policy, no-store and HSTS on HTTPS.
- Owner-only audit log records successful/failed logins, logout, password changes, CSRF failures and mutating API requests; client identifiers are one-way fingerprints and logs are capped.
- Password changes revoke all active sessions.
- Mandatory owner approval cannot be disabled; global publishing starts OFF.
- Keep `.env`, passwords, setup keys and OAuth secrets out of GitHub.
- **Not yet implemented:** TOTP authenticator 2FA, encrypted OAuth token vault, external security monitoring and automated encrypted off-site backups. Do not treat this MVP as audited or production-hardened.
- The Windows quick-start binds to `127.0.0.1` over HTTP. It is for local testing only, not public deployment.
