# Asfandyar AI Studio — project plan

## Goal
A zero-cost-first, owner-controlled digital marketing workspace. Prefer free tiers and open-source tools; do not spend money without explicit owner approval.

## Current MVP
- FastAPI local application with a private single-owner login.
- SQLite social account registry.
- Separate Facebook Profile and Facebook Page account types.
- Ten slots per supported platform: Facebook Profile, Facebook Page, Instagram, X, YouTube, LinkedIn, TikTok and Pinterest.
- Per-account niche and content-format preferences.
- Global publishing control OFF by default and owner approval enabled by default.
- Content draft creation and listing.
- Starter SEO and keyword analysis.
- Traffic campaign planning.
- Manual analytics entry and summary.
- Responsive owner dashboard with Social Accounts, Content Studio, SEO & Campaigns, Analytics and Security sections.

## Not implemented yet
- Real social account OAuth or authentication.
- Encrypted OAuth token storage and provider-specific publishing APIs.
- AI-generated articles/posts, image/video generation or rendering.
- Blogger publishing and scheduling.
- Automated social scheduling or cross-posting.
- Live traffic acquisition, live Adsterra/Monetag earnings, or live analytics integrations.
- Production deployment, backups and monitoring.

A registered account slot is only a local record, not a connected social account. Provider API access and eligibility vary by platform. Never collect social passwords in this app.

## Next development stages
1. Run the local MVP and verify owner setup/login and each dashboard module.
2. Add automated tests for content, SEO, campaigns and analytics.
3. Implement approved provider OAuth one platform at a time, with secure token storage.
4. Add content assistance with human review.
5. Add Blogger integration and scheduling where official APIs permit.
6. Add compliant analytics/reporting integrations where official interfaces exist.

## Safety
- No bought traffic, fake engagement, spam or policy-violating automation.
- Publishing remains disabled unless the owner explicitly changes the safety settings.
- Do not commit .env, credentials, passwords, setup keys or provider tokens.
- Do not claim a service is free until its current limits and requirements are checked.
