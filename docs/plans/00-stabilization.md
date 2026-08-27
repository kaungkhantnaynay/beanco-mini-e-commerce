# Phase 0: Stabilization and Specification

## Goal

Create a clean, reproducible baseline and settle the business decisions that affect
the backend data model.

## Work items

- [x] Install frontend dependencies from the lockfile.
- [x] Run lint, TypeScript checking, and production build; record/fix baseline errors.
- [x] Repair the README and document local frontend setup.
- [x] Add backend/frontend environment variable templates without secrets.
- [x] Decide the initial launch mode: catalog/inquiries, retail checkout, or hybrid.
- [x] Define supported product variants such as weight and grind.
- [x] Define stock policy: tracked, backorderable, preorder, or inquiry-only.
- [x] Define B2B quote, minimum quantity, and price visibility rules.
- [x] Document currency, tax, shipping origin, delivery area, and refund assumptions.
- [x] Select deployment targets, media storage, transactional email, and payment
      provider evaluation criteria.
- [x] Create the initial entity relationship diagram and API conventions.
- [x] Add CI baseline for existing frontend checks.

## Decisions required from the owner

1. Is retail checkout required for the first public release?
2. Can all users see prices, or are some wholesale prices account-specific?
3. Which countries/regions can place orders?
4. Which bean sizes and grind choices should be purchasable?
5. Is stock physically tracked for all products?

## Acceptance criteria

- A new developer can run and verify the frontend using documented commands.
- The repository has no unresolved conflict markers.
- The current frontend check results are known and repeatable.
- Business decisions needed by the first models are written down.
- No production credentials are required for local development.

## Out of scope

- Django models or API endpoints
- Storefront redesign
- Payment-provider implementation
