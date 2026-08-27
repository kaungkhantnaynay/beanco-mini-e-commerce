# Phase 3: Next.js Integration

## Goal

Replace hard-coded product and form behavior with the Django API while retaining the
current visual experience, accessibility, and server-rendering benefits.

## Work items

- [ ] Add documented public/server API base URL configuration.
- [ ] Create a centralized typed API client with timeout and error normalization.
- [ ] Add TypeScript types matching the published catalog contract.
- [ ] Fetch featured products for the home page from Django.
- [ ] Fetch product collections with pagination and filters.
- [ ] Change product detail routing from numeric IDs to product slugs.
- [ ] Define Next.js caching/revalidation behavior for catalog requests.
- [ ] Configure backend media/image origins in Next.js.
- [ ] Replace the `mailto:` contact form with an accessible API submission flow.
- [ ] Connect newsletter subscription to the API.
- [ ] Add loading, empty, success, field-error, server-error, and offline states.
- [ ] Remove `lib/data.ts` only after all consumers use the API.
- [ ] Add frontend tests for API mapping and critical form interactions.
- [ ] Verify responsive behavior and keyboard/screen-reader usage.

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

