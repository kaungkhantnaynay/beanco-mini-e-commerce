# Phase 6: Production Readiness

## Goal

Deploy a secure, observable, recoverable application with documented operational
procedures.

## Work items

- [ ] Containerize frontend and backend with deterministic production builds.
- [ ] Provision managed PostgreSQL and private application connectivity.
- [ ] Configure object storage/CDN for product media.
- [ ] Configure HTTPS, trusted hosts/proxies, secure cookies, HSTS, CORS, and CSRF.
- [ ] Store secrets in the deployment platform's secret manager.
- [ ] Run migrations as an explicit, rollback-aware release step.
- [ ] Configure transactional email and domain authentication.
- [ ] Add application error reporting, structured logs, metrics, and alerting.
- [ ] Define service-level health and availability signals.
- [ ] Configure database/media backups and perform a restore drill.
- [ ] Add rate limiting, upload limits, data retention, and privacy procedures.
- [ ] Run dependency, secret, static-analysis, and Django deployment checks in CI.
- [ ] Add smoke tests after deployment.
- [ ] Document release, rollback, incident, data restore, and key rotation runbooks.
- [ ] Complete accessibility, performance, SEO, and security reviews.

## Release gates

- All migrations have been tested on a production-like database copy or fixture.
- All phase acceptance criteria needed for launch are green in CI.
- No critical/high dependency or application security finding remains unexplained.
- Payment webhook and email delivery are verified in the target environment.
- Backup restoration succeeds within the documented recovery objective.
- Monitoring alerts reach an accountable operator.
- A rollback can be performed without guessing undocumented commands.

## Acceptance criteria

- Production deploys are repeatable and do not depend on a developer workstation.
- The application exposes useful health signals without leaking internal details.
- Operators can diagnose errors using correlated, privacy-safe logs.
- Database and media recovery procedures have been tested.
- Security-sensitive settings pass automated and manual review.

## Continuing backlog

- B2B company accounts and approval workflows
- Quote requests and quote-to-order conversion
- Contract/minimum-quantity and customer-specific pricing
- Purchase-order and invoice payment terms
- Recurring office coffee orders/subscriptions
- Automated customer-service chatbot for common questions, with human handoff for
  unresolved or sensitive requests
- Promotions, coupons, reviews, wishlists, and loyalty
- Analytics and business reporting
