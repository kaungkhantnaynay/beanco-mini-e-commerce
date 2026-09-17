# Customer Support Service Deployment

The Customer Support AI repository owns the Render Blueprint and detailed deployment
sequence in `docs/RENDER_DEPLOYMENT.md`. It provisions a separate FastAPI service and
PostgreSQL database in Singapore; do not reuse BeanCO's Django database.

Before deployment:

1. Review Render's displayed prices. Creating the Blueprint provisions paid resources.
2. Confirm both repositories' tests and hosted checks pass.
3. Create the support Blueprint from the Customer Support repository.

After Render reports the support service healthy:

1. Copy its HTTPS origin into Vercel as `SUPPORT_API_BASE_URL`.
2. Copy the generated Render `SUPPORT_API_TOKEN` into the matching server-only Vercel
   variable. Never use a `NEXT_PUBLIC_` prefix.
3. Redeploy the Vercel project because environment changes do not alter an existing
   deployment.
4. Test a new support question and one continuation from the deployed storefront.
5. Configure a Vercel firewall rate limit for `POST /api/support/chat` before public
   launch and record the chosen threshold in the service inventory.

Keep the first deployment in offline AI mode. Enable OpenAI and pgvector only after the
Customer Support project's bounded live evaluation and one-time knowledge indexing
complete successfully.
