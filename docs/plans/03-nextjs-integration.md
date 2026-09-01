# Phase 3: Next.js Integration

## Goal

Replace hard-coded product and form behavior with the Django API while retaining the
current visual experience, accessibility, and server-rendering benefits.

## Work items

- [x] Add documented public/server API base URL configuration.
- [x] Create a centralized typed API client with timeout and error normalization.
- [x] Add TypeScript types matching the published catalog contract.
- [x] Fetch featured products for the home page from Django.
- [x] Fetch product collections with pagination and filters.
- [x] Change product detail routing from numeric IDs to product slugs.
- [x] Define Next.js caching/revalidation behavior for catalog requests.
- [x] Configure backend media/image origins in Next.js.
- [x] Replace the `mailto:` contact form with an accessible API submission flow.
- [x] Connect newsletter subscription to the API.
- [x] Add loading, empty, success, field-error, server-error, and offline states.
- [x] Remove `lib/data.ts` only after all consumers use the API.
- [x] Add frontend tests for API mapping and critical form interactions.
- [x] Verify responsive behavior and keyboard/screen-reader usage.

Completion verified on 2026-08-27. Catalog reads revalidate every five minutes;
inquiry and newsletter writes are never cached. Responsive browser verification
covered the live home/catalog/detail/contact routes, filtering, 404 behavior,
semantic controls, mobile navigation, and horizontal overflow at 390 px.

## Acceptance criteria

- Product edits in Django Admin appear on the storefront according to the documented
  cache policy.
- No storefront code imports hard-coded product records.
- Invalid product slugs use the proper Next.js not-found response.
- Contact and newsletter submissions work without opening an email client.
- Forms prevent accidental duplicate submission and show useful outcomes.
- Lint, TypeScript checks, tests, and production build pass.

## Out of scope

- Cart UI
- Checkout
- Customer login
