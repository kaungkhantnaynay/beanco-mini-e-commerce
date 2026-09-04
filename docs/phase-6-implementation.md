# Phase 6 implementation record

Date started: 2026-09-04
Status: in progress — repository production and operations foundation implemented

## Scope of this slice

- Added version- and digest-pinned, multi-stage production containers for the Next.js
  storefront and Django API.
- Enabled Next.js standalone output and non-root runtime execution.
- Added Gunicorn as the Django production WSGI server and kept migrations outside
  application startup.
- Upgraded Pillow and pytest to versions without the vulnerabilities reported by the
  new backend dependency audit.
- Added an explicit release command that runs deployment checks, prints the migration
  plan, and applies migrations non-interactively.
- Expanded CI to test Django against PostgreSQL, validate migrations and OpenAPI,
  audit frontend/backend dependencies, scan committed content for secrets, and build
  both production images.
- Added post-deployment storefront, liveness, and readiness smoke checks.
- Recorded the production build and release approach in ADR 0006.
- Added UUID request correlation and fixed-field JSON request logs that exclude query
  strings, bodies, customer identity, and exception messages.
- Strengthened readiness with an actual database query while keeping liveness and
  readiness responses minimal and non-cacheable.
- Added configurable request-memory, file-memory, and product-image limits.
- Added release/rollback, incident, restore, key-rotation, health/availability, and
  retention/privacy runbooks under [`docs/operations/`](operations/README.md).

## Operator requirements

Before running `backend/scripts/release.sh`, confirm that the target database has a
current usable backup and review the printed migration plan. Roll back application code
first when possible. Reverse a Django migration only after confirming it is reversible,
recording the target migration name, and taking another backup.

Run post-deployment checks with public HTTPS origins:

```bash
FRONTEND_URL=https://shop.example.com \
BACKEND_URL=https://api.example.com \
./scripts/smoke-test.sh
```

## Deferred release gates

- The complete real Stripe sandbox acceptance matrix was deferred by explicit user
  direction and remains required before launch.
- Vercel, Render PostgreSQL/private networking, Cloudflare R2, and Resend provisioning.
- Target-environment webhook and email verification.
- Monitoring/alert routing and a successful backup restoration drill.
- Accountant/privacy-adviser review of the provisional retention periods and a tested
  privacy-request process.
- Accessibility, performance, SEO, and manual security reviews.

## Verification

- Frontend lint and TypeScript checks — passed.
- Frontend component tests — passed: 20 tests across 13 files.
- Frontend webpack production build and standalone output check — passed.
- Backend Ruff, formatting, and mypy checks — passed: 134 typed source files.
- Backend tests — passed: 102 tests; 1 PostgreSQL-only concurrency test skipped locally.
- Django system check, migration drift check, and OpenAPI validation — passed.
- Backend dependency audit — passed with no known vulnerabilities after upgrades.
- Django production deployment check — passed with representative non-secret values.
- Request correlation, safe-log allow-listing, upload configuration, and database
  readiness tests — passed as part of the backend suite.
- Release command — passed against a fresh disposable database, including deployment
  checks, migration plan output, and all migrations.
- Digest-pinned frontend and backend Docker builds — passed.
- Non-root container runtime and local deployment smoke checks — passed.
- Frontend npm advisory audit — passed with no known vulnerabilities after updating
  the transitive development-only `@humanfs/node` package to 0.16.8.
- Hosted GitHub Actions run and PostgreSQL CI result — pending push.

## Initial operating decisions

- The BeanCo owner/operator is the default incident owner and email is the alert channel;
  the monitored address still needs to be supplied.
- Recovery targets are a four-hour RTO and one-hour RPO, subject to provider-plan review
  and a successful restore drill.
- A provisional Thailand-oriented retention schedule is recorded in
  [`docs/operations/data-retention-and-privacy.md`](operations/data-retention-and-privacy.md).
- No paid resource may be created without presenting its cost to the user first.
