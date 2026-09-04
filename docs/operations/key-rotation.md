# Key rotation runbook

Rotate credentials one integration at a time. Store values only in the provider secret
manager and never print them in logs, tickets, chat, or shell history.

## Standard rotation

1. Identify affected services and confirm whether the provider permits overlapping old
   and new credentials.
2. Create the replacement credential with the minimum required permissions.
3. Update preview/staging, deploy, and verify health plus one non-destructive integration
   operation.
4. Update production and redeploy all consumers.
5. Revoke the old credential only after every consumer is confirmed on the replacement.
6. Record credential name, scope, owner, rotation time, and next review date—never its
   value.

## Credential-specific notes

- **Django secret key:** rotating invalidates signed tokens and sessions. Coordinate a
  customer login/reset impact window.
- **PostgreSQL:** rotate application credentials, update the backend secret, verify
  readiness, then revoke the old role/password.
- **Stripe API key:** update the backend secret and verify a read-only test-mode request
  before revocation. Rotate webhook signing secrets separately and verify signed delivery.
- **R2:** verify media read/write using the replacement access key before revocation.
- **Resend:** send to an approved internal test recipient before revocation.
- **GitHub/Vercel/Render tokens:** review installation scope and remove unused grants.

