# Phase 2 implementation record

Status: complete — all Phase 2 acceptance criteria are covered and verified.

## Implemented

- Domain-focused `catalog`, `inventory`, and `communications` Django apps with
  constrained models, migrations, factories, and tests.
- Searchable and filterable Django Admin screens. Inventory edits create immutable
  audit transactions; transaction history cannot be edited or deleted in Admin.
- An idempotent `seed_catalog` command for the eight original `lib/data.ts` products,
  including categories, variants, initial stock, managed local images, and legacy
  external images.
- Paginated anonymous category and product list/detail APIs with active-record
  visibility, slug lookup, documented filters and ordering, optimized prefetching,
  and bounded query-count coverage.
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
- `uv run pytest` — passed: 31 tests
- `uv run python manage.py check` — passed
- `uv run python manage.py spectacular --validate` — passed
- `uv run python manage.py makemigrations --check --dry-run` — passed
- `uv run python manage.py migrate --settings=config.settings.test` — passed
- Production deployment checks — passed with safe dummy environment values

## Operator actions

Run `uv run python manage.py migrate`, then `uv run python manage.py seed_catalog`.
Production must provide the documented R2 and Resend SMTP environment variables.

## Next step

Phase 3 can replace the frontend's hard-coded catalog and form behavior with these
published API contracts. `lib/data.ts` remains intentionally in place until all
frontend consumers have migrated.
