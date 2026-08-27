# Phase 2: Catalog, Inventory, and Communications

## Goal

Make products, availability, partnership inquiries, and newsletter subscriptions
manageable through Django and accessible through a tested public API.

## Domain model

### Catalog

- `Category`: name, slug, description, active state, display order.
- `Product`: name, slug, type, description, profile, featured/active state, SEO data.
- `ProductVariant`: product, SKU, option values, price, weight, active state.
- `ProductImage`: product/variant association, image, alt text, display order.

### Inventory

- `InventoryRecord`: variant, available/reserved quantities, stock policy.
- `InventoryTransaction`: immutable quantity change, reason, reference, actor, time.

### Communications

- `PartnershipInquiry`: contact/company data, inquiry type, requirements, consent,
  status, assignment, timestamps.
- `NewsletterSubscription`: normalized email, status, consent source/time, timestamps.

## Work items

- [x] Implement models, constraints, migrations, factories, and model tests.
- [x] Configure searchable/filterable Django Admin screens and safe bulk actions.
- [x] Create an idempotent data migration or seed command for the eight existing
      products in `lib/data.ts`.
- [x] Implement public category and product list/detail serializers and endpoints.
- [x] Add pagination, documented filters, search, ordering, and query-count tests.
- [x] Implement inquiry creation with validation, throttling, and spam defenses.
- [x] Implement idempotent newsletter subscription with privacy-safe responses.
- [x] Queue or safely send staff/customer email notifications.
- [x] Publish all contracts in the OpenAPI schema.
- [x] Add API, permission, validation, admin, and failure-path tests.

## API surface

```text
GET  /api/v1/categories/
GET  /api/v1/products/
GET  /api/v1/products/{slug}/
POST /api/v1/inquiries/
POST /api/v1/newsletter/subscriptions/
```

Product filters initially include category, type, featured, availability, search,
minimum price, maximum price, and ordering by name or price.

## Acceptance criteria

- Staff can manage categories, products, variants, images, stock, inquiries, and
  subscriptions in Django Admin.
- Existing products are reproducibly imported without duplication.
- Anonymous users can read only active catalog records.
- Product list requests remain bounded and avoid N+1 queries.
- Inquiry and subscription inputs are validated, throttled, stored, and tested.
- Money is serialized consistently and documented in OpenAPI.

## Out of scope

- Customer cart and checkout
- Payment processing
- Customer-specific wholesale prices
