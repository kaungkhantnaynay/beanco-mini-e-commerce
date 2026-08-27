# Phase 1: Backend Foundation

## Goal

Create a production-shaped Django REST Framework service with a custom user model,
environment-driven configuration, API documentation, and automated tests.

## Work items

- [x] Create `backend/` using Python 3.12+ and Django 5.2 LTS.
- [x] Pin direct dependencies and commit a reproducible lock file.
- [x] Add `config` settings for development, test, and production.
- [x] Configure PostgreSQL through environment variables.
- [x] Create `apps.accounts.User` before the first application migration.
- [x] Configure Django REST Framework and `/api/v1/` routing.
- [x] Add CORS and CSRF configuration appropriate to local Next.js development.
- [x] Add OpenAPI schema and interactive development documentation.
- [x] Add `/health/live/` and database-aware `/health/ready/` endpoints.
- [x] Configure structured logging without sensitive values.
- [x] Configure static/media development behavior and production interfaces.
- [x] Register the custom user in Django Admin.
- [x] Add pytest configuration, factories, and initial health/settings tests.
- [x] Add backend linting/formatting/type-checking commands and CI jobs.
- [x] Document setup, migrations, superuser creation, and verification.

## Verification note

All local checks pass. The initial migrations, including `accounts.0001_initial`,
were applied successfully to an empty temporary PostgreSQL 16 database on
2026-08-25. The verification container was removed after the check.

## Initial API surface

```text
GET /health/live/
GET /health/ready/
GET /api/v1/schema/
GET /api/v1/docs/
```

## Acceptance criteria

- The backend starts locally from documented steps.
- Development and test environments run without production secrets.
- PostgreSQL migrations apply to an empty database.
- A superuser can sign in to Django Admin.
- Health endpoints and OpenAPI schema are tested.
- Production settings pass Django's deployment checks once required variables are
  supplied.
- CI runs frontend and backend checks independently.

## Out of scope

- Product catalog
- Customer-facing authentication UI
- Cart, order, or payment behavior
