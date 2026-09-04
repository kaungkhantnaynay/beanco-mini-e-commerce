# Incident response runbook

## Severity

- **SEV-1:** confirmed data exposure, payment integrity failure, or complete checkout/API
  outage.
- **SEV-2:** material degradation, delayed webhooks/email, or partial customer impact.
- **SEV-3:** isolated defect with a safe workaround and no sensitive-data risk.

## Response

1. The BeanCo owner/operator acknowledges the alert and acts as incident lead unless
   responsibility has been explicitly delegated.
2. Record start time, affected service, release identifier, and representative request
   IDs. Never copy passwords, tokens, full payment payloads, or customer addresses into
   the incident record.
3. Check `/health/live/`, `/health/ready/`, deployment status, database availability,
   error rate, and recent releases.
4. Contain impact: stop rollout, disable the affected integration, or restore the last
   known-good artifact. Do not delete evidence.
5. For suspected secret exposure, follow the key-rotation runbook and revoke before
   investigating convenience or continuity.
6. For payment state uncertainty, stop fulfillment of affected orders and run bounded
   reconciliation after Stripe connectivity is restored.
7. Communicate status through the approved customer/status channel
   (`TBD-before-launch`) without exposing internal or personal data.
8. Resolve, run smoke tests, monitor recovery, and document follow-up actions with owners.
