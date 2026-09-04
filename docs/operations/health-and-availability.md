# Health and availability signals

## Endpoint contract

- `GET /health/live/` reports whether the Django process can serve a request.
- `GET /health/ready/` executes `SELECT 1` and returns HTTP 503 when the database is not
  usable.
- Both responses are minimal, carry `Cache-Control: no-store`, and expose no service,
  database, credential, version, or exception details.
- Stripe, email, and object storage are not readiness dependencies; transient provider
  failure must not cause the platform to restart healthy API processes.

## Signals

Monitor storefront/API availability, readiness failures, HTTP 5xx rate, request latency,
container restarts, PostgreSQL connections/storage, webhook failures/backlog, payment
reconciliation outcomes, email delivery failures, and object-storage errors. Backend request logs use
`X-Request-ID` to correlate method, path, status, duration, and exception type without
capturing query strings, bodies, account identity, or exception messages.

The initial recovery targets are a four-hour RTO and one-hour RPO. The incident owner is
the BeanCo owner/operator and the alert channel is email; the monitored email address,
alert thresholds, availability target, and latency target remain `TBD-before-launch`.
Alerts must be tested end to end and must link to the incident runbook before the
monitoring release gate can pass.
