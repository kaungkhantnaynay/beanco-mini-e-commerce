# ADR 0009: Free preview database bootstrap

- Status: accepted
- Date: 2026-10-19

## Context and constraints

ADR 0006 keeps schema migrations separate from normal application startup. Render's
free web services do not provide a separate pre-deploy command, while BeanCo's disposable
preview environment must be able to initialize a newly provisioned database and load the
starter catalog without a paid release job.

## Decision

- Keep normal application startup migration-free.
- When `SEED_CATALOG_ON_START=true` explicitly opts a service into preview bootstrap,
  run `python manage.py migrate --noinput` before the idempotent `seed_catalog` command.
- Keep the flag disabled for established production catalogs, which continue to use the
  reviewed `backend/scripts/release.sh` workflow from ADR 0006.

## Consequences

The free single-instance preview service can recover against a fresh database without a
manual shell or paid pre-deploy job. Its first boot can take longer, and a failed migration
prevents Gunicorn from starting instead of allowing the application to run against an
incompatible schema. Enabling this preview flag on multiple replicas is unsupported; a
production-scale deployment must retain the explicit release step.
