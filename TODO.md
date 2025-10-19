- to do task
+ completed task

Scope deployment

+ Configure RBAC in backend (ensure that certain endpoints can only be reached with a specific role)
+ Protect the scraping function
+ Fix RBAC in the frontend
+ Hide logout button if not logged in
+ Show logout button if logged in
+ Hide signup button if logged in
+ Show signup button if not logged in
+ Add pagination in job search
+ add a password reset function
+ add a delete account
+ fix treemap
+ add a simple settings page
+ connect changes of user to backend (change names, change password)
+ Add alerts
+ Add email confirmation --> Start with Resend
+ add a password forgoten function in the backend


TODO:
- OAuth with Google
- add pytests tests
- launch tool
- Rate limiting
-  Monitoring --- Sentry for error tracking | Structured logging (structlog) | Health check endpoints | Performance metrics (optional: Prometheus)
- Refresh tokens + session management --- Short-lived access tokens | Long-lived refresh tokens | Refresh endpoint | Session list (active sessions) | Revoke all sessions | Frontend auto-refresh logic


Out of Scope:
- Multi-tenancy
- Stripe Monetization
- Usage Tracking
- File Uploading
- 2FA
- Postal Email handling
- Add blacklisting tokens
- perhaps take the latest stored data item and set the scraper to look from then to now
- Background jobs -- Celery + Redis setup | Email sending in background | Scheduled job scraping | Job queue monitoring
