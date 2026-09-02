# BeanCo Implementation Plans

These documents define the approved implementation sequence for the Django-backed
BeanCo storefront. Read [`AGENTS.md`](../../AGENTS.md) and [`RULES.md`](../../RULES.md)
before using any plan.

## Product direction

BeanCo will support two connected customer journeys:

1. Retail customers browse products and later purchase through cart and checkout.
2. Hospitality, office, event, and wholesale customers submit partnership or quote
   inquiries.

The first release focuses on replacing hard-coded data and non-functional forms.
Transactional commerce follows after the catalog and API foundation are stable.

## Phase index

| Phase | Plan | Outcome | Dependency |
| --- | --- | --- | --- |
| 0 | [Stabilization and specification](00-stabilization.md) | Reproducible, documented baseline | None |
| 1 | [Backend foundation](01-backend-foundation.md) | Secure Django/DRF/PostgreSQL skeleton | Phase 0 |
| 2 | [Catalog and communications](02-catalog-communications.md) | Admin-managed products, inventory, inquiries, newsletter | Phase 1 |
| 3 | [Next.js integration](03-nextjs-integration.md) | Storefront backed by live API data | Phase 2 |
| 4 | [Cart and orders](04-cart-orders.md) | Transactional checkout foundation | Phase 3 |
| 5 | [Accounts and payments](05-accounts-payments.md) | Customer accounts and verified payments | Phase 4 |
| 6 | [Production readiness](06-production-readiness.md) | Deployable, observable, recoverable system | Phases 1-5 |

## Delivery policy

- Complete phases in order unless the user explicitly changes priority.
- A phase may be delivered through small pull requests, but each pull request must
  leave the repository in a runnable state.
- Do not mark a checkbox complete merely because files exist; verify its acceptance
  criterion.
- New scope belongs in the relevant plan's backlog until approved.
- Architecture choices with long-term consequences belong in `docs/decisions/`.

## Current status

- Current phase: Phase 5 in progress; authentication/session backend foundation complete
- Backend: Django/DRF guest carts, idempotent orders, account-auth foundation, Stripe Checkout Sessions, signed idempotent webhooks, inventory locking, and staff controls implemented
- Database: all migrations and concurrency behavior verified against an empty PostgreSQL 16 test database
- API: health, catalog, communications, accounts, cart, checkout, orders, Stripe payment-session/webhook, OpenAPI schema, and docs implemented
- Frontend: live catalog, anonymous commerce journey, Stripe-hosted payment redirect, inquiry/newsletter submissions, and catalog revalidation implemented
- Next gate: connect Next.js to Stripe-hosted Checkout and complete authentication UI; then add refund/reconciliation and remaining account ownership flows
