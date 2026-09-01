# ADR 0003: Phase 4 commerce rules

- Status: accepted
- Date: 2026-09-01

## Context and constraints

Phase 4 introduces retail carts and durable orders, but Phase 0 deliberately deferred
the commercial rules needed for server-authoritative totals and stock handling. The
owner approved proceeding with the smallest complete Thailand-only policy on
2026-09-01. Payment capture and refunds remain Phase 5 work.

## Decision

- All amounts use THB decimal values with two fractional digits. Calculations round
  half up at each order-line total and at each aggregate total.
- Subtotal is the sum of server-priced line totals. Phase 4 has no discounts.
- Catalog prices are treated as tax-inclusive. Phase 4 adds no separate tax charge,
  so `tax_total` is `0.00`.
- Phase 4 offers one Thailand-only standard delivery method with a `0.00` shipping
  charge and a non-guaranteed target of three to five business days after
  fulfillment. These launch terms require an operator review before public checkout.
- Cart item quantities are whole numbers from 1 through 99.
- Guest carts expire after 30 days of inactivity. Access tokens are random, stored
  only in secure HTTP-only cookies, and persisted only as hashes.
- Adding an item to a cart does not reserve stock. Every cart mutation revalidates
  the current server price, catalog visibility, and available-to-sell quantity.
- Order creation atomically deducts tracked stock and writes an immutable inventory
  transaction. A pre-fulfillment cancellation may restore stock exactly once.
- Live refunds and post-fulfillment return decisions remain out of scope until the
  Phase 5 payment-provider and refund policy decision.

## Alternatives considered

- Reserving stock while products sit in a cart.
- Adding tax or shipping charges before their production operation is confirmed.
- Allowing backorders, international addresses, promotional discounts, or partial
  quantities in the initial cart implementation.

## Consequences and follow-up work

Cart totals are deterministic and require no external tax or shipping service.
Demand can exceed stock while items remain in carts, so order creation must lock
inventory records and reject insufficient stock. Before enabling public checkout,
the owner/operator must review tax registration, shipping cost, delivery coverage,
and customer-facing cancellation/return wording; any change must be recorded and
covered by new tests without rewriting historical order totals.
