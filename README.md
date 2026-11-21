# Asfandyar AI Studio

Private, owner-controlled digital marketing manager. The project prefers free/open-source services and keeps publishing disabled until the owner explicitly enables it.

## Quick start on Windows (local testing)

1. Install Python 3.11 or newer from https://www.python.org/downloads/ and enable **Add Python to PATH**.
2. Download the repository using GitHub's **Code → Download ZIP**, then extract it.
3. Double-click `run_windows.bat`. It creates a local virtual environment, installs dependencies, creates a private `.env` file and starts the app.
4. The first run prints a one-time setup key in the black terminal window. Keep it private.
5. Open http://127.0.0.1:8000/app/ in your browser.
6. Create your owner username and a unique password (minimum 12 characters), using the one-time setup key.
7. After the owner account is created, stop the server with Ctrl+C. Open `.env`, delete the `ADMIN_SETUP_KEY=...` line, save, and run `run_windows.bat` again.
8. Sign in with your own username and password.

Keep the terminal window open while using the dashboard. This local server is only accessible from your own computer; it is not a public website.

## Run tests

In the extracted project folder, open Command Prompt and run:

```bat
.venv\Scripts\python.exe -m unittest discover -v
```

GitHub Actions also runs dependency installation, Python compilation, unit tests and dashboard/API smoke tests on every push.

## Security and deployment

- The Windows quick-start uses HTTP only on `127.0.0.1` for local testing. It is not suitable for public hosting.
- For public deployment, use HTTPS behind a properly configured reverse proxy, firewall, secure environment variables, database backups and monitoring. Set `COOKIE_SECURE=true`.
- Never commit `.env`, passwords, setup keys, OAuth secrets or access tokens to GitHub.
- There is one owner account and no public registration.
- Passwords are salted and hashed with PBKDF2-HMAC-SHA256 (310,000 iterations).
- Session tokens are random; only their SHA-256 digests are stored in SQLite.
- Login attempts are rate-limited; state-changing API calls require CSRF protection.
- Security response headers are enabled; API docs/OpenAPI are disabled by default.

## Current dashboard features

- Private owner login, logout and password change.
- Five independent account slots per supported platform: Facebook, Instagram, X, YouTube, LinkedIn, TikTok and Pinterest.
- Each registered account has its own owner-selected niche, content formats and publishing approval preference.
- Global publishing control defaults OFF; approval defaults ON.
- Account registration and niche settings are saved in SQLite.

## Important limitations — not yet a complete automation service

Registering a social account does not connect it to the social platform. Official OAuth, provider permissions, encrypted OAuth token storage and provider-specific publishing APIs must be implemented and approved before real posts can be sent. AI content generation, video rendering, scheduling, Blogger publishing, Adsterra/Monetag live reporting, production backups and a full analytics pipeline are also not yet complete.

Some legacy content/analytics managers still use in-memory storage. Do not use this MVP for public production hosting or real social account credentials yet. Never buy traffic, generate fake engagement, spam, or automate actions contrary to platform rules. No paid service should be enabled without the owner's explicit permission.
