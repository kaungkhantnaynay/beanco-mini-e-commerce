# ADR 0005: Stripe hosted payment provider

- Status: accepted
- Date: 2026-09-02

## Context and constraints

BeanCo requires THB card and PromptPay acceptance without handling raw card data.
Payment confirmation must be webhook-authoritative, idempotent, and compatible with
the existing stock deduction at order creation.

## Decision

- Use one Stripe Thailand account and Stripe-hosted Checkout Sessions in THB.
- Enable cards and PromptPay. BeanCo never receives or stores raw payment credentials.
- Create Sessions only in Django, with Stripe and local idempotency keys.
- Treat signed webhooks as authoritative. Store event IDs and outcomes, not full
  payment payloads. Verify signatures against the untouched request body.
- Confirm an order only after a paid Checkout event. Duplicate paid events are no-ops.
- Expire Checkout after 30 minutes. Expired or asynchronously failed unpaid Sessions
  cancel awaiting-payment orders and restore stock exactly once.
- A paid event received for an already cancelled/restocked order requires manual
  reconciliation and must not silently reconfirm it.
- Keep refunds behind the provider abstraction; controlled refund UI and policy are
  a later Phase 5 slice.

## Consequences and follow-up work

Production requires Stripe secret and webhook-signing keys in its secret manager.
The frontend must redirect only to the returned Stripe URL. Sandbox purchase,
failure, expiry, cancellation, refund, and reconciliation testing remain required
before Phase 5 completion.
