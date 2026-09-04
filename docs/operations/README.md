# BeanCo operations

These runbooks are the operator-facing procedures for Phase 6. Replace every remaining
`TBD-before-launch` provider identifier in the deployment platform before launch; never
replace placeholders with secrets in this repository.

- [`release-and-rollback.md`](release-and-rollback.md)
- [`incident-response.md`](incident-response.md)
- [`data-restore.md`](data-restore.md)
- [`key-rotation.md`](key-rotation.md)
- [`health-and-availability.md`](health-and-availability.md)
- [`data-retention-and-privacy.md`](data-retention-and-privacy.md)

Production service inventory:

| Component | Approved provider | Identifier/owner |
| --- | --- | --- |
| Storefront | Vercel | TBD-before-launch |
| API and PostgreSQL | Render Singapore | TBD-before-launch |
| Product media | Cloudflare R2 | TBD-before-launch |
| Transactional email | Resend | TBD-before-launch |
| Payments | Stripe | TBD-before-launch |
| Incident lead | Internal operator | BeanCo owner/operator |

The primary alert channel is email. The monitored recipient address remains
`TBD-user-email` and must be supplied before monitoring can be activated.
