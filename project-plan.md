# Asfandyar AI Studio

## Project overview
A zero-cost-first AI-assisted digital marketing and automation platform.

## Social platforms and account limits
The account registry supports these seven platforms:
- Facebook
- Instagram
- X (Twitter)
- YouTube
- LinkedIn
- TikTok
- Pinterest

Each platform has its own independent limit of **5 registered account slots** (up to 35 account slots overall). For example, five Facebook accounts and five Instagram accounts can be registered independently.

A registered slot is not yet an authenticated connection. Actual publishing and account insights require the relevant platform's official OAuth/API permissions. Credentials must never be collected in plain text or committed to GitHub. Build provider-specific OAuth and encrypted token storage as a separate stage.

## Core features and roadmap
1. Social account registry, per-platform limits, account selection and connection status.
2. Official OAuth integrations and publishing adapters, only where provider APIs and account eligibility permit.
3. AI-assisted articles and social content, with review before publishing.
4. Blogger integration and scheduled publishing.
5. SEO checks, keyword research and content planning.
6. Traffic campaign planning using genuine, policy-compliant traffic.
7. Account-wise and website analytics.
8. Adsterra and Monetag reporting/integration where supported by their official interfaces.

## Zero-cost and safety rules
- Prefer free tiers and open-source components.
- Clearly flag any feature that needs paid access, approval, or API eligibility.
- Never buy traffic, generate fake engagement, or spam.
- Follow each platform's terms, rate limits, and automation rules.
- Never spend money without explicit permission.
- Protect credentials; never store plaintext passwords or API tokens in source control.

## Current implementation status
- FastAPI application and starter marketing endpoints.
- SQLite-backed social account registry with five independent slots per supported platform.
- Account listing, registration, removal, and limit-summary API endpoints.
- OAuth authorization and real publishing are not implemented yet.


## Owner security and access control
- Single owner login; no public signup.
- Password hashing, expiring HttpOnly session cookie, CSRF protection, login lockout, password change, and logout.
- All application APIs require an authenticated owner session except health, first-run setup, and login.
- Publishing and external integrations remain disabled until official OAuth credentials and explicit owner approval are configured.
- Secrets must live in server environment variables, never in the repository.
