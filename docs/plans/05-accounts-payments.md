# Phase 5: Accounts and Payments

## Goal

Add customer identity, order history, and a verified payment lifecycle without
handling raw card data on BeanCo servers.

## Work items

### Accounts

- [x] Implement registration, email verification, login, logout, and password reset.
- [x] Use secure HTTP-only session cookies and CSRF protection for browser sessions.
- [x] Add customer profile and saved-address management.
- [x] Merge a guest cart safely after login.
- [x] Add authenticated order list/detail endpoints and Next.js account pages.
- [x] Prevent account and password-reset enumeration.

### Payments

- [x] Record a provider decision ADR based on THB support, fees, refunds, settlement,
      hosted checkout, webhook quality, and local compliance.
- [x] Add `PaymentAttempt` and stored webhook event models.
- [x] Create a provider abstraction around checkout-session creation and refunds.
- [x] Redirect/embed only provider-hosted secure payment UI.
- [x] Verify webhook signatures using the raw body.
- [x] Process webhook events idempotently and outside long request transactions.
- [x] Transition orders only through allowed payment/order states.
- [x] Send order confirmation and payment-failure notifications.
- [x] Add controlled cancellation and refund workflows.
- [x] Reconcile orders against provider payment state.

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

## Progress note

Phase 5 started on 2026-09-02 with the backend authentication/session foundation.
ADR 0004 records the approved secure-cookie, CSRF, verification-token, neutral-response,
and token-safe email delivery rules. Registration, verification, login, logout,
current-account, and password-reset APIs now have automated security coverage. The
The Next.js authentication flows, profile and saved-address management, safe guest-cart
merge, and strictly owned order history are now implemented. ADR 0005 selects
Stripe-hosted Checkout with THB cards and PromptPay. Payment-attempt storage, Checkout
Session creation, raw-body signature verification, idempotent webhook processing,
notifications, customer cancellation/full-refund controls, and provider reconciliation
are implemented. Phase 5 remains in progress only until real Stripe test-mode purchase,
failure, expiry, cancellation, refund, and webhook journeys are executed and recorded.
