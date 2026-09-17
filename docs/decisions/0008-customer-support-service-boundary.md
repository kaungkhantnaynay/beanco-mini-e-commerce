# ADR 0008: Customer support service boundary

- Status: accepted
- Date: 2026-09-16

## Context

The Phase 6 backlog includes an automated customer-service assistant with human handoff. A separate FastAPI Customer Support AI project already provides grounded retrieval, conversation access tokens, escalation rules, ticket creation, an admin queue, PostgreSQL migrations, and offline/live evaluation tooling.

Connecting the browser directly to that service would expose its deployment origin, require a cross-origin policy, and make the storefront responsible for another public API boundary. Reimplementing the assistant in Django would duplicate the existing tested service.

## Decision

- Keep Next.js as the storefront, Django as the commerce backend, and FastAPI as the bounded support service.
- Send browser chat requests to a same-origin Next.js route at `/api/support/chat`.
- Configure the upstream origin only through the server-side `SUPPORT_API_BASE_URL` variable.
- Authenticate the public support origin with a shared `SUPPORT_API_TOKEN` sent only
  by the Next.js server as `X-Support-Token`.
- Keep the support conversation ID and opaque access token in React memory. Do not place either value in `localStorage`.
- Run the support service with its BeanCO-specific knowledge directory and evaluation dataset.
- Do not send Django sessions, account records, order records, addresses, cart contents, or payment details to the assistant. Questions requiring private data create a human-support ticket.

## Consequences

The storefront gains a portable support experience without changing the commerce API
or weakening its session boundary. The Next.js server must be able to reach the support
service, and the support service needs independent database migration, secrets,
monitoring, and deployment configuration. A browser refresh intentionally starts a new
support conversation. Direct requests to protected support endpoints fail when the
configured service token is absent or incorrect.
