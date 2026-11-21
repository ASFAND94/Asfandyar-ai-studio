# Final deployment checklist

This checklist describes the current prepared release. It does not claim that third-party provider integrations or an independent security audit are complete.

## Repository package
- [x] FastAPI application and installable responsive PWA shell
- [x] Owner setup/login/logout/password change
- [x] CSRF, hashed sessions, password hashing, login throttling and security headers
- [x] TOTP authenticator MFA with rate-limited codes
- [x] Fernet-encrypted secret vault with metadata-only listing
- [x] Mandatory owner approval; publishing defaults OFF
- [x] Persistent SQLite content, campaign and analytics modules
- [x] Dockerfile and Docker Compose persistent volume
- [x] Windows local launcher
- [x] Health and storage-readiness endpoints
- [x] Automated GitHub Actions tests
- [x] Deployment and backup documentation

## Required before public launch
- [ ] Review the latest GitHub Actions run and confirm success.
- [ ] Deploy to HTTPS only with a persistent private disk.
- [ ] Set a long random ADMIN_SETUP_KEY and unique strong owner password.
- [ ] Remove ADMIN_SETUP_KEY after first owner setup and restart.
- [ ] Confirm APP_DB_PATH, AUTH_DB_PATH and SOCIAL_DB_PATH all point to the same persistent database file.
- [ ] Confirm /health and /ready return healthy/ready.
- [ ] Confirm owner login, logout, password change, CSRF rejection and session revocation.
- [ ] Set and separately back up APP_ENCRYPTION_KEY; enable authenticator MFA and safely store the authenticator seed/device.
- [ ] Confirm publishing is OFF and owner approval cannot be disabled.
- [ ] Create a test draft and campaign, restart the service, and confirm they persist.
- [ ] Configure encrypted backups and complete a test restore.
- [ ] Configure host-level MFA, restricted admin access, dependency updates and monitoring.

## Not included in this prepared release
- Provider-specific OAuth token refresh/rotation and integration with the encrypted generic vault.
- Built-in MFA recovery codes (keep a secure backup of your authenticator device and APP_ENCRYPTION_KEY).
- Official social provider OAuth and publishing adapters.
- Live Adsterra/Monetag earnings APIs.
- Hosted AI model integration; current AI utilities are local rule-based helpers and draft planning.
- Background scheduler/queue for automatic campaigns.
- Independent penetration test or security audit.

Do not connect valuable social accounts, enable public publishing or store real provider tokens until the missing integration/security work is completed and tested. Free hosting tiers are not necessarily durable; verify storage, sleep limits and current prices before selecting a host.
