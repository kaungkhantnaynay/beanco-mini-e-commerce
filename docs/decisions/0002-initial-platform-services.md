# ADR 0002: Initial platform services

- Status: accepted; product-media portion superseded by ADR 0007
- Date: 2026-08-25

## Context and constraints

BeanCo needs selected deployment and communications targets before backend work,
while avoiding premature payment-provider integration. The implementation must
retain Next.js for the storefront, Django/DRF for the API, PostgreSQL for
production data, and environment-managed secrets.

## Decision

- Deploy the Next.js storefront on Vercel, connected to the Git repository for
  preview and production deployments.
- Deploy the Django API and its managed PostgreSQL database as Render services in
  Singapore, keeping both on Render's regional private network.
- Store product media in Cloudflare R2 using its S3-compatible API. This original
  media-provider decision was superseded by ADR 0007 after billing preferences were
  reviewed during Phase 6.
- Send transactional mail with Resend from a dedicated verified subdomain, such as
  `mail.example.com`, after SPF, DKIM, and DMARC are configured.
- Do not select or integrate a payment provider in Phase 0. Phase 5 must evaluate
  THB presentment and settlement, Thailand eligibility and local payment methods,
  fees, refunds and disputes, webhook signature verification and idempotency,
  sandbox support, reporting, and payout timing before an approved provider ADR.

## Alternatives considered

- Self-hosting the Next.js application and Django API on a single virtual machine.
- Using provider-specific media storage rather than an S3-compatible object store.
- Selecting a payment provider before checkout requirements exist.

## Consequences and follow-up work

Phase 1 settings will need deployment-specific production configuration, including
allowed hosts, CORS/CSRF origins, database URL, object-storage credentials, and
email API credentials. These values belong only in each provider's secret manager,
not in this repository. Phase 6 must verify backup restoration, monitoring,
domain authentication, and operational runbooks.

## Evidence reviewed

- [Vercel Next.js deployment documentation](https://vercel.com/docs/frameworks/full-stack/nextjs)
- [Render Django deployment documentation](https://render.com/docs/deploy-django)
- [Render regions documentation](https://render.com/docs/regions)
- [Cloudflare R2 S3 API documentation](https://developers.cloudflare.com/r2/get-started/s3/)
- [Resend domain verification documentation](https://resend.com/docs/dashboard/domains/introduction)
