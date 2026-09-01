# Phase 4: Cart and Orders

## Goal

Implement a server-authoritative guest/customer cart and create durable orders with
correct price and inventory behavior. Payment is not captured in this phase.

## Domain model

- `Cart` and `CartItem`
- `Address`
- `Order` and immutable `OrderItem` snapshots
- Explicit order status transitions
- Inventory reservations or atomic stock deductions, based on the Phase 0 decision

## Work items

- [x] Define totals, rounding, tax, shipping, expiry, and stock-reservation rules.
- [x] Implement guest cart tokens stored in secure cookies.
- [x] Implement cart retrieval and add/update/remove operations.
- [x] Re-fetch prices and validate active products/variants on every mutation.
- [x] Add backend-computed subtotal, discount, shipping, tax, and total fields.
- [x] Implement address validation and available shipping methods.
- [ ] Implement idempotent order creation inside a database transaction.
- [ ] Snapshot all commercial order-line fields.
- [ ] Protect stock changes against concurrent checkout.
- [ ] Add cart and checkout pages/components to Next.js.
- [ ] Add staff order views and controlled status actions in Django Admin.
- [ ] Test tampered prices, unavailable variants, insufficient stock, duplicate
      checkout requests, concurrency, permissions, and rollback behavior.

## API surface

```text
GET    /api/v1/cart/
POST   /api/v1/cart/items/
PATCH  /api/v1/cart/items/{id}/
DELETE /api/v1/cart/items/{id}/
POST   /api/v1/checkout/preview/
POST   /api/v1/orders/
GET    /api/v1/orders/{public_id}/status/
```

## Acceptance criteria

- Anonymous customers can maintain a cart without exposing sequential identifiers.
- The server rejects manipulated prices and invalid quantities.
- Two concurrent orders cannot oversell tracked stock.
- Repeating an order request with the same idempotency key does not duplicate it.
- Created orders remain historically correct after product edits.
- Checkout failure leaves cart, order, and inventory in a consistent state.

## Out of scope

- Live payment capture
- Refunds
- Customer account dashboard

## Progress note

The guest cart and checkout-preview backend slices were completed on 2026-09-01.
The approved commercial rules are recorded in ADR 0003. Order creation, inventory
deduction, frontend cart/checkout UI, and staff order management remain open and
must be implemented before Phase 4 is complete.
