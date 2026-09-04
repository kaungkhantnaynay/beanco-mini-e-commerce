# BeanCo backend

The Django REST Framework backend serves the BeanCo catalog, inventory, guest cart,
order, account authentication, partnership inquiry, and newsletter domains through versioned JSON under
`/api/v1/`.

## Setup

Install [uv](https://docs.astral.sh/uv/) and Python 3.12 or newer. Copy the local
configuration template, then install the locked environment:

```bash
cp .env.example .env
uv sync --group dev
```

The template defaults to local PostgreSQL. To run only the Phase 1 service without
PostgreSQL, remove `DATABASE_URL` from `backend/.env`; development then uses the
ignored `backend/db.sqlite3` fallback. Production never uses this fallback.

## Local commands

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py seed_catalog
uv run python manage.py runserver
```

Endpoints:

- `GET /health/live/`
- `GET /health/ready/`
- `GET /api/v1/schema/`
- `GET /api/v1/docs/`
- `GET /api/v1/categories/`
- `GET /api/v1/products/`
- `GET /api/v1/products/{slug}/`
- `POST /api/v1/inquiries/`
- `POST /api/v1/newsletter/subscriptions/`
- `GET /api/v1/cart/`
- `POST /api/v1/cart/items/`
- `PATCH /api/v1/cart/items/{public_id}/`
- `DELETE /api/v1/cart/items/{public_id}/`
- `POST /api/v1/checkout/preview/`
- `POST /api/v1/orders/`
- `GET /api/v1/orders/{public_id}/status/`
- `GET /api/v1/auth/csrf/`
- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/verify-email/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `POST /api/v1/auth/password-reset/`
- `POST /api/v1/auth/password-reset/confirm/`
- `GET /api/v1/account/`
- `POST /api/v1/orders/{public_id}/payment-session/`
- `POST /api/v1/payments/stripe/webhook/`
- `/admin/`

`seed_catalog` idempotently imports the eight original products and their available
images, variants, and initial inventory. Local notifications use the configured
console email backend. Production uses Resend's SMTP interface and requires
`EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, and `STAFF_NOTIFICATION_EMAIL`.

Every response includes a UUID `X-Request-ID`; a valid incoming value is preserved so
requests can be traced across the storefront and API. JSON access logs contain only the
request ID, method, path without its query string, status, duration, and exception type.
Do not add bodies, query strings, credentials, customer identity, or exception messages
to request logs.

Request and in-memory file thresholds are controlled by
`DATA_UPLOAD_MAX_MEMORY_SIZE` and `FILE_UPLOAD_MAX_MEMORY_SIZE`. Product images also
have an explicit `PRODUCT_IMAGE_MAX_BYTES` validation cap. The deployment proxy or
platform must enforce a compatible total request-size limit.

Guest carts use an opaque HTTP-only `beanco_cart` cookie. Keep
`CART_COOKIE_SECURE=true` in production; the local environment template disables it
only so the cookie works over local HTTP.

Checkout preview accepts a transient Thailand shipping address and the
`standard_th` method. It does not store contact data; it revalidates the current
catalog, stock, prices, and totals on every request.

Order creation requires an `Idempotency-Key` header containing 16–128 safe
characters. It snapshots the validated cart and shipping address, atomically deducts
stock, and returns the existing order when the same request key is retried.

Browser authentication uses Django's HTTP-only session cookie. Fetch
`GET /api/v1/auth/csrf/` first, then send the CSRF cookie value as `X-CSRFToken` with
credentials on every authentication mutation. Verification and reset messages use
`ACCOUNT_EMAIL_BACKEND`; keep this separate from a console backend so signed tokens
never enter logs. Production also requires public `ACCOUNT_EMAIL_VERIFICATION_URL`
and `ACCOUNT_PASSWORD_RESET_URL` values. Order confirmation, failed-payment, and
refund messages use `PAYMENT_EMAIL_BACKEND`; configure it as a transactional backend
in production.

Stripe-hosted Checkout uses THB cards and PromptPay. Payment-session creation requires
the order's guest-cart cookie or authenticated owner plus an `Idempotency-Key` header.
Set `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_SUCCESS_URL`, and
`STRIPE_CANCEL_URL`; use the Stripe CLI to forward signed sandbox events locally.
Customers can cancel unpaid orders and can cancel/refund confirmed orders before
fulfilment begins. Operators can reconcile stored attempts with Stripe in bounded
batches:

```bash
uv run python manage.py reconcile_payments --limit 100
```

Preview product media uses a private Supabase Storage bucket through its
S3-compatible endpoint. Production requires the endpoint, access key, secret key,
bucket name, and project region. The backend uses path-style addressing, SigV4
signing, private signed URLs, and a 15-minute signed-URL lifetime by default. Keep
S3 access keys server-side only. See
[`docs/operations/supabase-storage.md`](../docs/operations/supabase-storage.md) for
provisioning and verification.

Concurrency verification requires PostgreSQL. With a disposable test database set
in `DATABASE_URL`, run:

```bash
uv run pytest --ds=config.settings.postgres_test
```

## Verification

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy apps config
uv run pytest
uv run python manage.py check
uv run python manage.py spectacular --validate --file /tmp/beanco-openapi.yaml
uv run python manage.py check --deploy --settings=config.settings.production
```

The production check requires production environment variables such as
`DJANGO_SECRET_KEY`, `DATABASE_URL`, `DJANGO_ALLOWED_HOSTS`, and
`FRONTEND_ORIGIN`. Do not place their real values in this repository.

## Production container and release

From the repository root, build the API image with:

```bash
docker build --tag beanco-backend backend
```

The image starts Gunicorn as a non-root user and does not run migrations automatically.
Configure the deployment platform to run this command once before new application
replicas start:

```bash
backend/scripts/release.sh
```

Confirm a usable database backup before running the release command and review its
migration plan. See [`docs/phase-6-implementation.md`](../docs/phase-6-implementation.md)
and the [`docs/operations/`](../docs/operations/README.md) runbooks for rollback,
health, recovery, incident, credential-rotation, and smoke-test guidance.
