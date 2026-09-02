# Phase 5 implementation record

Date started: 2026-09-02
Status: in progress — authentication/session backend foundation complete

## Completed in this slice

- Recorded the account session, CSRF, verification, enumeration, and sensitive-email
  rules in ADR 0004.
- Added `email_verified_at` while keeping unverified registrations inactive.
- Added CSRF bootstrap, registration, email verification, login, logout,
  current-account, password-reset request, and password-reset confirmation endpoints.
- Used HTTP-only Django sessions and enforced CSRF on anonymous and authenticated
  authentication mutations.
- Added neutral registration/reset responses and consistent login failures to avoid
  exposing account existence or verification state.
- Isolated verification/reset delivery from the console email backend so signed
  tokens are not logged.
- Added scoped throttles and OpenAPI annotations for the authentication surface.
- Added coverage for CSRF failure shape, secure session flags, full verification and
  session lifecycle, enumeration resistance, and password replacement.
- Recorded Stripe-hosted Checkout with THB cards and PromptPay in ADR 0005.
- Added immutable payment-attempt identity, commercial amount snapshots, one-open-
  attempt enforcement, and payload-minimizing webhook event records.
- Added a Stripe provider abstraction for hosted Checkout creation and refunds.
- Added guest-cart or authenticated-order ownership checks for payment-session creation.
- Added raw-body webhook signature verification, duplicate-event suppression, paid
  confirmation, unpaid expiry/failure cancellation, and exactly-once stock restoration.
- Added manual-reconciliation handling for late paid events after an order was
  cancelled and its stock restored.
- Added an awaiting-payment order action that requests a retry-safe Checkout Session,
  validates the returned Stripe-hosted URL, and redirects without exposing card data.

## Verification

- `uv run ruff check .` — passed
- `uv run ruff format --check .` — passed: 109 files formatted
- `uv run mypy apps config` — passed: 125 source files
- `uv run pytest` — passed: 90 tests; 1 PostgreSQL-only concurrency test skipped
- `uv run python manage.py check` — passed
- `uv run python manage.py makemigrations --check --dry-run` — passed
- `uv run python manage.py spectacular --validate` — passed
- Production deployment checks — passed with safe dummy environment values
- Stripe payment tests — passed: provider/local idempotency, forged signature
  rejection, duplicate events, paid confirmation, expiry restoration, and late-event safety
- Frontend tests — passed: 16 tests across 10 files
- Frontend lint, TypeScript, and webpack production build — passed

## Configuration and operator actions

Apply `accounts.0002_user_email_verified_at` with `uv run python manage.py migrate`.
Apply `payments.0001_initial` with the same command.
Configure the session/CSRF cookie names and secure flags, account-auth throttle rates,
`ACCOUNT_EMAIL_BACKEND`, `ACCOUNT_EMAIL_VERIFICATION_URL`, and
`ACCOUNT_PASSWORD_RESET_URL` using `backend/.env.example`. Production must use HTTPS,
secure cookies, public frontend URLs, and a non-console transactional email backend.
Stripe additionally requires `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`,
`STRIPE_SUCCESS_URL`, and `STRIPE_CANCEL_URL` in the secret/configuration manager.

## Remaining Phase 5 work

- Add Next.js registration, verification, login, logout, and password-reset flows.
- Add profile and saved-address management.
- Merge guest carts safely after login.
- Add owned order list/detail APIs and account pages.
- Add confirmation/failure notifications, controlled refunds, and reconciliation.
- Complete Stripe sandbox purchase, failure, expiry, cancellation, and refund journeys.
