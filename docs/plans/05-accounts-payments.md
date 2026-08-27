# Phase 5: Accounts and Payments

## Goal

Add customer identity, order history, and a verified payment lifecycle without
handling raw card data on BeanCo servers.

## Work items

### Accounts

- [ ] Implement registration, email verification, login, logout, and password reset.
- [ ] Use secure HTTP-only session cookies and CSRF protection for browser sessions.
- [ ] Add customer profile and saved-address management.
- [ ] Merge a guest cart safely after login.
- [ ] Add authenticated order list/detail endpoints and Next.js account pages.
- [ ] Prevent account and password-reset enumeration.

### Payments

- [ ] Record a provider decision ADR based on THB support, fees, refunds, settlement,
      hosted checkout, webhook quality, and local compliance.
- [ ] Add `PaymentAttempt` and stored webhook event models.
- [ ] Create a provider abstraction around checkout-session creation and refunds.
- [ ] Redirect/embed only provider-hosted secure payment UI.
- [ ] Verify webhook signatures using the raw body.
- [ ] Process webhook events idempotently and outside long request transactions.
- [ ] Transition orders only through allowed payment/order states.
- [ ] Send order confirmation and payment-failure notifications.
- [ ] Add controlled cancellation and refund workflows.
- [ ] Reconcile orders against provider payment state.

## Acceptance criteria

- Authentication secrets never enter browser storage or application logs.
- Customers can access only their own profile, addresses, and orders.
- A valid payment event moves an order to paid exactly once.
- Forged, replayed, duplicated, or out-of-order webhook events are handled safely.
- Failed payment does not produce a paid order or permanently lose stock.
- Staff can inspect payment attempts without seeing sensitive payment credentials.
- Sandbox end-to-end purchase, failure, cancellation, and refund flows pass.

## Out of scope

- Marketplace/split payments
- Loyalty points
- Multiple payment providers active at once unless required for launch

