# Phase 2 implementation record

Status: complete — all Phase 2 acceptance criteria are covered and verified.

## Implemented

- Domain-focused `catalog`, `inventory`, and `communications` Django apps with
  constrained models, migrations, factories, and tests.
- Searchable and filterable Django Admin screens. Inventory edits create immutable
  audit transactions; transaction history cannot be edited or deleted through
  model instances, querysets, or Admin.
- An idempotent `seed_catalog` command for the eight original `lib/data.ts` products,
  including categories, variants, initial stock, managed local images, and legacy
  external images.
- Paginated anonymous category and product list/detail APIs with active-record and
  active-variant visibility, slug lookup, documented filters and ordering, optimized
  prefetching, bounded query-count coverage, and non-null decimal-string prices.
- Validated and throttled partnership inquiry and newsletter endpoints with consent
  timestamps, honeypot fields, normalized email addresses, stable errors, and
  privacy-safe idempotent subscription responses.
- Post-commit staff/customer notifications. Local/test environments use safe
  console/in-memory backends; production requires Resend SMTP credentials.
- Validated OpenAPI contracts, including decimal-string product prices and common
  validation/throttle error responses.

## Verification

- `uv run ruff check .` — passed
- `uv run ruff format --check .` — passed
- `uv run mypy apps config` — passed
- `uv run pytest` — passed: 36 tests
- `uv run python manage.py check` — passed
- `uv run python manage.py spectacular --validate` — passed
- `uv run python manage.py makemigrations --check --dry-run` — passed
- `uv run python manage.py migrate --settings=config.settings.test` — passed
- Production deployment checks — passed with safe dummy environment values

The Phase 2 completion audit was rerun on 2026-08-27. Regression tests cover
products without active variants, bulk inventory transaction mutation attempts,
newsletter consent/honeypot validation, newsletter throttling, notification
failure persistence, and the non-null OpenAPI price contract.

## Operator actions

Run `uv run python manage.py migrate`, then `uv run python manage.py seed_catalog`.
Production must provide the documented S3-compatible media and Resend SMTP environment
variables. ADR 0007 selects Supabase Storage for preview media; the Phase 6 integration
must be verified before production use.

## Next step

Phase 3 replaced the frontend's hard-coded catalog and form behavior with these
published API contracts. `lib/data.ts` was removed after all consumers migrated.
