# BeanCo Mini E-Commerce

BeanCo is a Next.js coffee catalog and partnership storefront. A Django REST
Framework backend will provide catalog management, lead capture, inventory, carts,
orders, customer accounts, and payments through phased implementation.

## Current state

- Next.js 16, React 19, TypeScript, and Tailwind CSS frontend
- Static storefront pages ready for Phase 3 API integration
- Django REST Framework backend foundation in `backend/`
- Phase 2 catalog, inventory, communications, Admin, and public APIs complete

## Required reading before implementation

All contributors and implementation agents must read:

1. [`AGENTS.md`](AGENTS.md)
2. [`RULES.md`](RULES.md)
3. [`docs/plans/README.md`](docs/plans/README.md)
4. The plan document for the phase being implemented

## Frontend setup

```bash
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

Verification commands:

```bash
npm run lint
npx tsc --noEmit
npm run build
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

## Plans

The complete roadmap and phase status are maintained in
[`docs/plans/README.md`](docs/plans/README.md).
