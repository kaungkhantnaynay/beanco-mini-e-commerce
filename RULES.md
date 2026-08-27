# BeanCo Engineering Rules

This document is the shared implementation contract for the BeanCo storefront and
Django backend. It must be read before any feature implementation.

## 1. Product and scope

- BeanCo is a hybrid storefront: a public retail catalog plus B2B partnership and
  quotation workflows.
- Preserve the existing visual language and accessibility of the Next.js frontend.
- Build the smallest complete feature for the active phase. Defer optional features
  to the backlog rather than partially implementing them.
- Business rules must live on the backend. The frontend may display calculations,
  but it must not be trusted to determine price, discounts, stock, tax, shipping,
  payment state, or permissions.

## 2. Repository structure

- Keep the Next.js application in the existing repository root.
- Place Django in `backend/` with configuration in `backend/config/` and domain apps
  in `backend/apps/`.
- Prefer domain-focused Django apps such as `accounts`, `catalog`, `inventory`,
  `communications`, `carts`, `orders`, and `payments`.
- Put shared frontend API code in `lib/api/` and shared API types in `lib/types/`.
- Do not add a new framework, state library, task queue, or infrastructure service
  without an immediate requirement and a recorded decision.

## 3. Source control and file safety

- Inspect the working tree before editing and never overwrite unrelated user work.
- Keep changes focused; do not mix broad refactors with feature implementation.
- Do not commit generated artifacts, virtual environments, dependency directories,
  local databases, uploaded media, coverage output, or secrets.
- Do not rewrite migration history after it may have been shared. Add a new
  migration instead.
- Destructive data migrations require a backup/rollback note and explicit approval.

## 4. Python and Django

- Target Python 3.12+ and the latest security patch of Django 5.2 LTS unless an ADR
  approves an upgrade.
- Use Django REST Framework for the versioned JSON API under `/api/v1/`.
- Create a custom user model before the first production migration.
- Use PostgreSQL in production. SQLite may be used only for lightweight local work
  when behavior does not depend on PostgreSQL.
- Keep settings environment-driven and split into sensible base/development/test/
  production modules when the backend is scaffolded.
- Use timezone-aware datetimes and store timestamps in UTC.
- Use `DecimalField` for money. Never use binary floating point for prices or totals.
- Put multi-model business operations in explicit service functions and wrap
  transactional operations in `transaction.atomic()`.
- Avoid business logic in signals. Signals are allowed only for loose, non-critical
  side effects with tests and documentation.
- Optimize known list endpoints with `select_related()`/`prefetch_related()` and
  guard against unbounded querysets.

## 5. Data model invariants

- Public URLs use immutable, unique slugs or UUIDs rather than sequential database
  IDs where practical.
- Product variants own purchasable SKU, price, and stock identity.
- Orders store immutable snapshots of purchased name, SKU, variant, unit price,
  quantity, discount, and tax data.
- Never recalculate historical order lines from the current product record.
- Stock changes must be traceable through inventory transactions.
- Email addresses are normalized before uniqueness checks.
- Prefer explicit status enums and validate allowed state transitions.
- Add database constraints for invariants that must remain true under concurrency.

## 6. API contract

- Namespace public APIs under `/api/v1/`.
- Use consistent JSON field naming, ISO 8601 datetimes, and integer or decimal-string
  representations defined by the serializer contract.
- Paginate collection endpoints and whitelist filtering and ordering fields.
- Return stable error shapes containing a machine-readable code, human-readable
  detail, and field errors when applicable.
- Public reads are anonymous; mutations require the minimum appropriate permission.
- Generate and validate an OpenAPI schema as part of backend verification.
- Changes that break an existing API require a new version or a documented migration
  period.

## 7. Authentication and security

- Prefer secure, HTTP-only, same-site session cookies plus CSRF protection when the
  frontend and API share a parent domain.
- Never store access tokens in `localStorage`.
- Configure explicit production hosts, origins, CORS, CSRF origins, secure cookies,
  HTTPS redirect, HSTS, and trusted proxy behavior.
- Validate all input on the server and apply file type/size limits to uploads.
- Rate-limit anonymous mutation endpoints such as inquiries, subscriptions, login,
  password reset, cart creation, and checkout.
- Do not log passwords, tokens, full payment payloads, or unnecessary personal data.
- Verify payment webhook signatures against the raw request body and make webhook
  processing idempotent.
- Run Django deployment checks and dependency/security scans before release.

## 8. Frontend integration

- Fetch public catalog data in server components where practical.
- Keep client components limited to interactive behavior.
- Centralize API base URL, request handling, timeouts, and error translation.
- Define TypeScript response types from the documented API contract; do not scatter
  ad hoc response shapes across components.
- Provide loading, empty, validation-error, network-error, and success states.
- Use `next/image` with explicit approved image origins.
- Maintain keyboard access, visible focus, semantic labels, reduced-motion support,
  and useful alternative text.

## 9. Testing requirements

- Every backend model invariant, permission rule, service, and endpoint behavior must
  have automated coverage.
- Every fixed defect must receive a regression test when feasible.
- Use factories/fixtures with fictional data; never copy production data into tests.
- Test authorization failures as well as successful requests.
- Checkout, stock, payment, and webhook code requires transaction, concurrency, and
  idempotency tests appropriate to its risk.
- Frontend changes must pass lint, TypeScript checking, and production build. Add
  component or end-to-end tests for critical interactive flows when that testing
  layer is introduced.

Expected verification after the relevant tooling is installed:

```bash
npm run lint
npx tsc --noEmit
npm run build
cd backend && python manage.py check
cd backend && python manage.py check --deploy --settings=config.settings.production
cd backend && pytest
```

## 10. Definition of done

A feature is complete only when:

- Its acceptance criteria pass.
- Code, migrations, admin behavior, API schema, and documentation agree.
- Relevant automated tests pass.
- Security and permission failure paths are covered.
- Setup instructions and `.env.example` are updated for new configuration.
- No secret, debug-only setting, unresolved merge marker, or unexplained warning is
  introduced.
- The active phase plan is updated with completed work and remaining follow-ups.

