# Metricool-inspired upgrades for Asfandyar AI Studio

This roadmap extends the existing private, owner-controlled workspace. It is an implementation plan, not a claim that third-party publishing APIs are already connected.

## Product direction
Build a Metricool-inspired control center with original workflows for social account management, a visual publishing calendar, content planning, performance analytics, and Blogger monetization. Keep the project zero-cost-first and require explicit owner approval before external publishing.

## Existing capabilities verified in the repository
- Private single-owner authentication and CSRF-protected state-changing API requests.
- Social account registry with up to 10 slots per supported platform.
- Per-account content preferences and global publishing safety controls.
- Draft storage, starter SEO/keyword analysis, campaign planning, and manually entered analytics.

## Upgrade modules

### 1. Unified social dashboard
- Account status, platform, handle, content preferences, and per-account publishing controls.
- Distinguish registered account slots from authenticated provider connections.
- Never request or store a user's social-network password.

### 2. Visual content calendar and scheduler
- Calendar views: month, week, and agenda.
- Create, edit, reschedule, cancel, and filter scheduled content.
- Store each scheduled item with platform, account slot, planned time, timezone, approval state, and publication state.
- Start in planning/draft mode. Do not send content to providers until official OAuth, provider permissions, and an approved publishing adapter exist.
- Show timezone clearly; never silently interpret a local time as UTC.

### 3. Content studio
- Reusable drafts and platform-specific variants.
- AI-assisted captions, article outlines, hashtags, and calls to action when a configured AI provider is available.
- Human review and approval before publishing.
- Blogger article workflow with separately configurable Adsterra and Monetag link placements; disclose that link insertion does not guarantee ad approval, traffic, or earnings.

### 4. Analytics and reports
- Per-account and per-platform performance views.
- Track available metrics such as reach/impressions, clicks, engagement, visitors, pageviews, CTR, CPM, RPM, and earnings.
- Date filters and exportable reports.
- Label manually entered data separately from verified provider data.
- Only show live metrics after an official API or trusted import source is connected.

### 5. Best-time recommendations
- Derive suggestions from the owner's own historical engagement data.
- If there is insufficient data, label recommendations as general test suggestions rather than measured facts.

### 6. Traffic and monetization workspace
- Blogger campaign links and UTM tracking.
- Separate Adsterra and Monetag configuration fields and placement controls.
- No bought traffic, fake clicks, spam, or claims of guaranteed revenue.

## Delivery order
1. Add persistent scheduled-post records and CRUD API.
2. Add a responsive calendar and agenda in the dashboard.
3. Add per-account performance summaries and charts using available records.
4. Add platform OAuth adapters one provider at a time, only through official APIs.
5. Add Blogger publishing and monetization-link workflow after secure credentials and API permissions are configured.

## Zero-cost and platform constraints
- Prefer SQLite, FastAPI, open-source libraries, and local development.
- Free hosting is not guaranteed to provide always-on background scheduling. A laptop-hosted app only runs jobs while the laptop and server are running.
- Social publishing, analytics, and account limits depend on each platform's current API access, review, and rate limits. Some features may require paid plans or may not be available for personal profiles.
- AI generation may require a provider with a free quota or a local model; free quotas and hardware requirements can change.
- Do not add paid services or incur costs without explicit owner approval.

## Acceptance criteria
- Scheduled posts persist across app restarts.
- Every schedule entry has an explicit timezone and account association.
- The owner can review, edit, cancel, and filter planned posts.
- Publishing stays OFF by default and approval is required by default.
- UI clearly distinguishes planned, approved, published, failed, and not-connected states.
- Tests cover schedule validation, timezone handling, permissions, and CRUD behavior.
