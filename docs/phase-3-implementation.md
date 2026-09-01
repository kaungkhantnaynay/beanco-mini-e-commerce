# Phase 3 implementation record

Date: 2026-08-27
Status: complete — all Phase 3 acceptance criteria are covered and verified.

## Implemented

- Separate server/private and browser-visible API URLs, plus an explicit public
  media origin for `next/image`.
- Central typed API requests with an eight-second timeout, stable API field errors,
  and normalized configuration, timeout, network, and server failures.
- OpenAPI-aligned TypeScript types for paginated catalog data, product detail,
  inquiries, and newsletter subscriptions.
- Server-rendered featured products, filterable/paginated collections, slug product
  detail pages, proper Next.js not-found handling, and five-minute catalog
  revalidation.
- Accessible inquiry and newsletter client forms with server field errors,
  privacy-safe outcomes, live regions, consent, spam honeypots, and duplicate-submit
  protection.
- Loading, empty, unavailable, validation, network, server, and success states.
- Responsive media origins, mobile overflow protection, labeled navigation and form
  controls, visible focus treatment, touch-safe hover behavior, press feedback, and
  reduced-motion behavior.
- Vitest and Testing Library coverage for API mapping, error normalization, filter
  mapping, inquiry submission/error behavior, duplicate prevention, and newsletter
  submission.
- Removal of numeric product routes and `lib/data.ts` after all catalog consumers
  migrated to the API.

## Cache policy

Catalog and category reads use Next.js server caching with a five-minute revalidation
window. Product edits therefore appear on the storefront within five minutes without
a redeploy. Inquiry and newsletter mutations use `cache: "no-store"`.

## Verification

- `npm run lint` — passed
- `npx tsc --noEmit` — passed
- `npm test` — passed: 7 tests across 5 files
- `npm run build` — passed on Next.js 16.3.3
- `npm audit --omit=dev` — passed: 0 vulnerabilities
- Local browser verification — passed for live catalog data, filtering, valid and
  invalid slug routes, semantic forms/navigation, and 390 px responsive layout

## Configuration and operator actions

Set `API_BASE_URL`, `NEXT_PUBLIC_API_BASE_URL`, and
`NEXT_PUBLIC_MEDIA_BASE_URL` as documented in `.env.example`. The backend must be
reachable during production builds if the initial generated home page should contain
catalog products immediately; otherwise the error state revalidates on the documented
five-minute interval.

## Next step

Phase 4 must not begin until the owner approves tax, shipping, delivery, refund,
totals, rounding, cart expiry, and stock-reservation rules required by its plan and
ADR 0001.
