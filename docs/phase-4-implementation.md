# Phase 4 implementation record

Date: 2026-09-02
Status: complete

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
- Added typed, cookie-aware browser clients for cart mutations, checkout preview,
  idempotent order creation, and privacy-limited order status lookup.
- Added available-variant purchase controls to product detail pages with quantity,
  stock, duplicate-submit, success, and actionable failure states.
- Added responsive cart, checkout, and order confirmation routes with server-returned
  totals, accessible labels and live regions, nested address errors, retry-safe order
  submission, and explicit awaiting-payment messaging.
- Added cart entry points to desktop/mobile navigation and the footer.
- Allowed the required `Idempotency-Key` request header through credentialed CORS;
  live browser testing caught and verified this frontend/backend boundary.
- Applied restrained 180 ms status-entry feedback with reduced-motion support.

## Verification

- `uv run ruff check .` — passed
- `uv run ruff format --check .` — passed: 91 files formatted
- `uv run mypy apps config` — passed: 104 source files
- `uv run pytest` — passed: 80 tests; 1 PostgreSQL-only concurrency test skipped
- PostgreSQL 16 backend suite before the frontend slice — passed: 80 tests,
  including concurrent oversell protection
- `uv run python manage.py check` — passed
- `uv run python manage.py spectacular --validate` — passed
- `uv run python manage.py makemigrations --check --dry-run` — passed
- `uv run python manage.py migrate --settings=config.settings.test --noinput` — passed
- Production deployment checks — passed with safe dummy environment values
- `npm test -- --run` — passed: 14 tests across 10 files
- `npm run lint` — passed
- `npx tsc --noEmit` — passed
- `npx next build --webpack` — passed, including `/cart`, `/checkout`, and dynamic
  `/orders/[publicId]`; the default Turbopack build could not bind its internal CSS
  worker port in the execution environment
- `pytest config/tests/test_cors.py apps/orders/tests/test_api.py -q` — passed: 13 tests
- Live browser journey — passed: product add, cookie cart retrieval, checkout preview,
  idempotent order creation, and awaiting-payment status
- Mobile browser check at 390×844 — passed with no horizontal overflow

## Configuration and operator actions

Run `uv run python manage.py migrate` to apply `carts.0001_initial`,
`inventory.0002_alter_inventorytransaction_reason`, `orders.0001_initial`, and
`orders.0002_order_orders_restored_only_when_cancelled`.
Optional cart, checkout, and order throttle settings are documented in
`backend/.env.example`. Production must keep `CART_COOKIE_SECURE=true`.

The frontend requires `NEXT_PUBLIC_API_BASE_URL` to point at the browser-reachable
API origin. The API origin must remain explicitly allowlisted for credentialed CORS.

## Remaining Phase 4 work

None. Live payment capture, refunds, and customer account order history remain Phase 5 scope.
