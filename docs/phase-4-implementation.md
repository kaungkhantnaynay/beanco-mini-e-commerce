# Phase 4 implementation record

Date: 2026-09-01
Status: in progress — guest cart and checkout preview complete; orders remain.

## Completed in this slice

- Recorded the approved THB totals, tax, shipping, cart-expiry, quantity, stock, and
  cancellation rules in ADR 0003.
- Added `Cart` and `CartItem` models with UUID public identifiers, constrained item
  quantities, unique variants per cart, explicit cart status, and a 30-day rolling
  expiry.
- Added opaque guest tokens stored as SHA-256 hashes in Django and sent only through
  an HTTP-only, same-site cookie that is secure by default outside development.
- Added rate-limited `GET /api/v1/cart/` and add, update, and remove item endpoints.
- Revalidated active catalog records and locked current inventory records on every
  mutation. Client-supplied price or total fields are rejected.
- Added backend-computed decimal-string subtotal, discount, shipping, tax, and total
  fields to the documented OpenAPI contract.
- Added model, API, isolation, expiry, throttling, tamper, stock, visibility, and
  failure-path regression coverage.
- Added transient Thailand-only shipping-address validation and the approved standard
  delivery method without persisting preview contact data.
- Added rate-limited `POST /api/v1/checkout/preview/` with authoritative current
  prices and totals plus full cart, catalog-visibility, and stock revalidation.
- Added fictional Bangkok address coverage for valid previews, field validation,
  unsupported shipping, empty and isolated carts, changed prices, hidden products,
  insufficient stock, tampered totals, and throttling.

## Verification

- `uv run ruff check .` — passed
- `uv run ruff format --check .` — passed: 76 files formatted
- `uv run mypy apps config` — passed: 85 source files
- `uv run pytest` — passed: 59 tests
- `uv run python manage.py check` — passed
- `uv run python manage.py spectacular --validate` — passed
- `uv run python manage.py makemigrations --check --dry-run` — passed
- `uv run python manage.py migrate --settings=config.settings.test --noinput` — passed
- Production deployment checks — passed with safe dummy environment values

## Configuration and operator actions

Run `uv run python manage.py migrate` to apply `carts.0001_initial`. The optional
`CART_THROTTLE_RATE` and `CART_COOKIE_NAME` settings are documented in
`backend/.env.example`. Production must keep `CART_COOKIE_SECURE=true`.

## Remaining Phase 4 work

Implement durable order and order item snapshots, idempotent transactional order
creation, concurrency-safe stock deduction and restoration, frontend cart/checkout
flows, Django Admin order actions, and the remaining failure/concurrency tests.
