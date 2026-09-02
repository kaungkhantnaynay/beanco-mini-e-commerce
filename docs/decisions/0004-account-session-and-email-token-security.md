# ADR 0004: Account sessions and email-token security

- Status: accepted
- Date: 2026-09-02

## Context and constraints

Phase 5 adds customer identity before payment credentials or provider callbacks.
BeanCo already uses Django, DRF, credentialed browser requests, and same-parent-domain
deployment assumptions. Repository policy prefers HTTP-only sessions, requires CSRF
protection, forbids browser token storage and token logging, and requires account and
password-reset enumeration resistance.

## Decision

- Use Django server-side sessions with an HTTP-only, secure-in-production,
  `SameSite=Lax` cookie. Do not issue browser-stored bearer tokens.
- Bootstrap Django's CSRF cookie through an explicit read endpoint and require the
  matching `X-CSRFToken` header on every authentication mutation, including
  anonymous registration, login, verification, and password-reset requests.
- Normalize email addresses and require email verification before API login.
  Registered users remain inactive until a single-use, time-limited signed token is
  verified.
- Use Django's password validators and password-reset token generator. Verification
  uses a separate salt and includes verification/active state in its signature so a
  successful verification invalidates the token.
- Return the same accepted response for existing and missing registration or reset
  addresses, and the same login failure for unknown, unverified, and incorrect
  credentials.
- Send authentication links through a separately configured Django email backend.
  Local/test defaults use the in-memory backend so signed tokens do not appear in
  console/application logs. Production uses the configured SMTP backend.
- Store only `email_verified_at`; do not persist verification or reset tokens.

## Alternatives considered

- JWT access/refresh tokens in browser storage.
- A third-party authentication framework before the required behavior was known.
- Console delivery for verification and reset links.
- Allowing login before email ownership is verified.

## Consequences and follow-up work

The frontend must fetch a CSRF cookie before authentication mutations and include
credentials plus `X-CSRFToken`. Production needs a functioning transactional email
provider and correct public verification/reset URLs. Account UI, resend UX, profile,
saved addresses, guest-cart merge, owned order APIs, and payment work remain later
Phase 5 slices.
