# Supabase Storage operating procedure

ADR 0007 selects Supabase Storage for private preview product media. This integration
does not use Supabase Auth, Data API, or Postgres; Django remains the application and
authentication authority, and Render PostgreSQL remains the preview database.

## Preview provisioning

1. Create a Supabase Free project named `beanco-preview` in the closest available
   Southeast Asia region.
2. Create a standard bucket named `beanco-preview-media`. Keep **Public bucket** off,
   set the file-size limit to `10 MB`, and allow `image/jpeg`, `image/png`, and
   `image/webp` MIME types.
3. In Storage settings, enable the S3 protocol and generate server-side S3 credentials.
4. Save the access-key ID, secret access key, direct storage endpoint, and region in a
   password manager. Never place them in chat, Git, browser-visible configuration, or a
   `NEXT_PUBLIC_` variable.
5. Add the values listed in `backend/.env.example` to the Render preview service.
   Keep path-style addressing, SigV4 signing, private signed URLs, and the default
   15-minute signed-URL lifetime.

Generated Supabase S3 keys grant broad S3 access across the project's buckets and bypass
Storage RLS. Keep this Supabase project limited to BeanCo-controlled resources and treat
the credentials as production-grade server secrets even during preview.

## Verification gate

The integration is not complete until all of the following pass:

- A fictional product image uploads through Django Admin and appears in the private
  bucket with the expected content type.
- The API returns a time-limited signed image URL and the storefront renders it.
- An unauthenticated direct bucket listing or unsigned object request is rejected.
- Replacing and deleting a disposable test image produces the expected object state.
- No S3 credential appears in frontend output, logs, Git history, or network responses.
- The backend still uses Render PostgreSQL and Django sessions; no Supabase database or
  authentication dependency has been introduced.

## Recovery limitation

Supabase Storage does not support S3 object versioning. Deleting an object permanently
removes it from the primary bucket. Free preview storage therefore contains no production
or customer media. Before production approval, configure and test the independent
35-day backup described in [`data-restore.md`](data-restore.md).

## Cost and lifecycle

The Supabase Free limits and inactivity-pausing rules can change and must be checked on
the [official pricing page](https://supabase.com/pricing) before provisioning or launch.
Any paid upgrade requires a separate cost presentation and owner approval. If production
uses a paid Supabase plan, verify that its spend cap is enabled before accepting traffic.
