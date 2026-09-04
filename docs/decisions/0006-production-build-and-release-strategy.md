# ADR 0006: Production build and release strategy

- Status: accepted
- Date: 2026-09-04

## Context and constraints

Phase 6 requires repeatable production builds, explicit migrations, automated security
checks, and post-deployment verification. ADR 0002 already selects Vercel for Next.js
and Render for Django/PostgreSQL. Local development must remain lightweight, and an
application container must never apply schema changes implicitly when it starts.

## Decision

- Build the Next.js storefront with digest-pinned Node 24 and standalone output.
- Build the Django API with digest-pinned Python 3.12 and uv, and serve it with
  Gunicorn as a non-root user.
- Install dependencies strictly from `package-lock.json` and `uv.lock` during image
  builds.
- Keep database migration execution separate from application startup. Operators run
  the release command only after reviewing its migration plan and confirming a usable
  database backup.
- Run application checks against PostgreSQL in CI, audit locked dependencies, scan for
  committed secrets, validate the OpenAPI schema, and build both production images.
- Use explicit liveness, readiness, and storefront smoke checks after deployment.

## Alternatives considered

- Running Django's development server in production.
- Applying migrations automatically whenever an application replica starts.
- Maintaining hand-written requirements files in addition to `uv.lock`.
- Building deployment images only on developer workstations.

## Consequences and follow-up work

Container startup cannot race migrations or hide a failed schema change. Releases require
an explicit operator or platform pre-deploy command. Base image and CI action versions
must be reviewed by dependency automation. Provider provisioning, backup restoration,
alert delivery, and target-environment smoke tests remain separate Phase 6 gates.
