# Phase 4 implementation record

Date: 2026-09-01
Status: in progress — transactional backend complete; frontend cart/checkout remains.

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
- Added immutable `Address` and `OrderItem` snapshots plus protected commercial
  totals on UUID-addressed `Order` records with explicit status transitions.
- Added idempotent transactional order creation using hashed retry keys and request
  fingerprints. Retries return the existing order; conflicting reuse is rejected.
- Locked inventory rows in deterministic variant order, atomically deducted stock,
  wrote traceable sale transactions, converted carts only after success, and rolled
  back address/order/item/inventory/cart changes together on failure.
- Added privacy-limited public order status lookup and read-only Django Admin order,
  address, and item views with controlled fulfillment/cancellation actions.
- Added one-time cancellation stock restoration with a dedicated immutable inventory
  transaction reason.

## Verification

- `uv run ruff check .` — passed
- `uv run ruff format --check .` — passed: 90 files formatted
- `uv run mypy apps config` — passed: 103 source files
- `uv run pytest` — passed: 79 tests; 1 PostgreSQL-only concurrency test skipped
- PostgreSQL 16 full suite — passed: 80 tests, including concurrent oversell protection
- `uv run python manage.py check` — passed
- `uv run python manage.py spectacular --validate` — passed
- `uv run python manage.py makemigrations --check --dry-run` — passed
- `uv run python manage.py migrate --settings=config.settings.test --noinput` — passed
- Production deployment checks — passed with safe dummy environment values

## Configuration and operator actions

Run `uv run python manage.py migrate` to apply `carts.0001_initial`,
`inventory.0002_alter_inventorytransaction_reason`, `orders.0001_initial`, and
`orders.0002_order_orders_restored_only_when_cancelled`.
Optional cart, checkout, and order throttle settings are documented in
`backend/.env.example`. Production must keep `CART_COOKIE_SECURE=true`.

## Remaining Phase 4 work

Implement the Next.js cart and checkout pages/components, connect product purchase
controls to the guest cart API, present validation and order outcomes accessibly, and
run frontend interaction, responsive, accessibility, lint, type, test, and build
verification.
