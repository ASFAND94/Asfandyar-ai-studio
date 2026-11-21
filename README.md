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
- Passwords are salted and hashed with PBKDF2-HMAC-SHA256.
- Session tokens are random; only SHA-256 digests are stored.
- Login attempts are rate-limited; state-changing API calls require CSRF protection.
- Keep `.env`, passwords, setup keys and OAuth secrets out of GitHub.
- The Windows quick-start binds to `127.0.0.1` over HTTP. It is for local testing only, not public deployment.


## Cloudflare version (in progress; not deployed)

The `cloudflare-deployment-prep` branch now includes a D1-backed FastAPI API, persistent account/content/campaign/analytics stores, owner authentication, Blogger URL and separate Adsterra/Monetag Direct Link settings, Blogger draft link insertion, and installable PWA assets. The Cloudflare Worker serves the dashboard at `/app/`.

It is still **not verified as a live Cloudflare deployment**. The real D1 database ID and Worker setup secret must be configured by the owner, and the free-tier CPU limit must be benchmarked against the existing 310,000-iteration PBKDF2 login. Cloudflare Workers Free currently allows 10 ms CPU per request, so deployment may not meet the zero-cost requirement without a reviewed authentication alternative. See [CLOUDFLARE_DEPLOYMENT.md](CLOUDFLARE_DEPLOYMENT.md) before proceeding.

The dashboard can store Monetag/Adsterra URLs and insert enabled links into Blogger article drafts, but it does not publish to Blogger or social accounts. Social OAuth, live provider analytics, AI model integration, persistent post scheduling and automatic posting are not yet implemented.
