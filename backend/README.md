# BeanCo backend

The Django REST Framework backend serves the BeanCo catalog, inventory, guest cart,
partnership inquiry, and newsletter domains through versioned JSON under `/api/v1/`.

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
- `/admin/`

`seed_catalog` idempotently imports the eight original products and their available
images, variants, and initial inventory. Local notifications use the configured
console email backend. Production uses Resend's SMTP interface and requires
`EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`, and `STAFF_NOTIFICATION_EMAIL`.

Guest carts use an opaque HTTP-only `beanco_cart` cookie. Keep
`CART_COOKIE_SECURE=true` in production; the local environment template disables it
only so the cookie works over local HTTP.

Checkout preview accepts a transient Thailand shipping address and the
`standard_th` method. It does not store contact data; it revalidates the current
catalog, stock, prices, and totals on every request.

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
