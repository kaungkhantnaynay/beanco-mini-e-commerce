# BeanCo Mini E-Commerce

BeanCo is a Next.js coffee catalog and partnership storefront. A Django REST
Framework backend will provide catalog management, lead capture, inventory, carts,
orders, customer accounts, and payments through phased implementation.

## Current state

- Next.js 16.3, React 19, TypeScript, and Tailwind CSS frontend
- Live Django-backed catalog, product purchase controls, anonymous cart, checkout,
  order confirmation, partnership inquiry, and newsletter forms
- Django REST Framework backend foundation in `backend/`
- Phases 0–4 complete; Phase 5 implementation complete with its Stripe acceptance
  matrix deferred; Phase 6 production readiness in progress

## Required reading before implementation

All contributors and implementation agents must read:

1. [`AGENTS.md`](AGENTS.md)
2. [`RULES.md`](RULES.md)
3. [`docs/plans/README.md`](docs/plans/README.md)
4. The plan document for the phase being implemented

## Frontend setup

```bash
npm ci
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

To test from another device on the same network, open the `Network` URL printed by
Next.js (for example, `http://192.168.137.229:3000`). BeanCO automatically permits
the workstation's active LAN IPv4 addresses so the development client can hydrate.
If you use a custom local hostname, add it to `BEANCO_DEV_ALLOWED_ORIGINS` in
`.env.local`; multiple hostnames can be comma-separated.

For cart, account, and form testing from that device, replace `<LAN_IP>` with the
workstation's current address and configure both services before starting them:

```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://<LAN_IP>:8000/api/v1

# backend/.env
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,<LAN_IP>
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://<LAN_IP>:3000
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://<LAN_IP>:3000
```

Start Django with `uv run python manage.py runserver 0.0.0.0:8000`. These LAN values
are development-only; do not copy them into production configuration.

`API_BASE_URL` is used for server-rendered catalog requests and may use private
networking in hosted environments. `NEXT_PUBLIC_API_BASE_URL` is browser-visible and
used for commerce and inquiry/newsletter submissions. `NEXT_PUBLIC_MEDIA_BASE_URL` is the approved
public media origin for `next/image`. Catalog reads revalidate every five minutes;
form submissions are never cached.

`SUPPORT_API_BASE_URL` is the server-only origin of the Customer Support AI service.
`SUPPORT_API_TOKEN` is the matching server-only shared secret. Neither value may use a
`NEXT_PUBLIC_` prefix.
For local development, run that service with its BeanCO knowledge pack on port 8001:

```bash
cd "/path/to/Customer Support"
KNOWLEDGE_BASE_DIR=data/knowledge_beanco uv run uvicorn app.main:app --port 8001
```

The storefront sends chat messages through `/api/support/chat`; the upstream service
origin and service token are not exposed to browser code. The proxy sends the token in
`X-Support-Token`, waits up to 30 seconds for the bounded upstream request, and fails
safely when either server setting is missing. Support conversation credentials stay in
memory, and a page refresh starts a new conversation.

Verification commands:

```bash
npm run lint
npx tsc --noEmit
npm test
npm run build
```

Build the standalone production container with:

```bash
docker build --tag beanco-frontend .
```

## Backend setup

Install Python 3.12+ and [uv](https://docs.astral.sh/uv/), then:

```bash
cd backend
cp .env.example .env
uv sync --group dev
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

The backend runs at [http://localhost:8000](http://localhost:8000). Its health,
schema, documentation, and verification commands are documented in
[backend/README.md](backend/README.md).

Build the production API container from the repository root with:

```bash
docker build --tag beanco-backend backend
```

Database migrations are deliberately not run when an application container starts.
After confirming a usable backup, run `backend/scripts/release.sh` as the platform's
pre-deploy command. Deployment and rollback details are recorded in
[`docs/phase-6-implementation.md`](docs/phase-6-implementation.md), with operator
procedures indexed under [`docs/operations/`](docs/operations/README.md).

## Plans

The complete roadmap and phase status are maintained in
[`docs/plans/README.md`](docs/plans/README.md).
