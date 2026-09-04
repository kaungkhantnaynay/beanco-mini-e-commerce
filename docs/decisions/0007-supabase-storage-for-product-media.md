# ADR 0007: Supabase Storage for product media

- Status: accepted for preview; production approval conditional
- Date: 2026-09-04

## Context and constraints

ADR 0002 originally selected Cloudflare R2 for product media. During Phase 6 setup,
activating R2 required accepting usage-based charges against a stored payment method.
The owner declined that billing model and requested Supabase as the alternative.

BeanCo still needs S3-compatible storage for the existing Django storage backend. The
preview environment must have no monthly subscription, media credentials must remain
server-side, and changing media storage must not replace Django authentication or the
already-provisioned Render PostgreSQL preview database.

## Decision

- Use a private Supabase Storage bucket for preview product media through Supabase's
  S3-compatible endpoint.
- Keep Django as the only authentication system and Render PostgreSQL as the application
  database. Supabase Auth, Data API, and Postgres are not application dependencies.
- Store generated Supabase S3 access keys only in Render's secret manager. These keys
  are never exposed through `NEXT_PUBLIC_` variables or committed files.
- Use server-generated, time-limited signed media URLs rather than making the preview
  bucket public.
- Treat Supabase Free as preview-only. Production use requires a separate cost review,
  confirmation that the spend cap is enabled, an independent media-backup process, and
  a successful restore drill.
- Do not claim the Phase 6 object-storage work item complete until Django configuration,
  upload/read behavior, and recovery are verified against Supabase.

## Alternatives considered

- Activate Cloudflare R2 with automatic usage-based billing.
- Store uploaded media on Render's ephemeral service filesystem.
- Replace Render PostgreSQL and Django authentication with Supabase services.
- Make the Supabase bucket public.

## Consequences and follow-up work

Supabase's S3 endpoint allows the existing `django-storages` integration to remain, but
the endpoint, region, and path-style addressing must become environment-driven and be
tested. Generated S3 keys provide broad server-side storage access and bypass Storage
RLS, so the project should contain only BeanCo-controlled buckets and the keys require
the same protection and rotation discipline as other production credentials.

Supabase Storage does not support S3 object versioning. Deleted objects cannot be
restored from the bucket itself, so production readiness depends on a separate scheduled
backup retained outside the primary bucket.

The Free plan currently includes 1 GB of file storage and 5 GB each of origin and cached
egress, but it pauses inactive projects and provides no production recovery guarantee.

## Evidence reviewed

- [Supabase pricing and Free-plan limits](https://supabase.com/pricing)
- [Supabase Storage S3 compatibility](https://supabase.com/docs/guides/storage/s3/compatibility)
- [Supabase Storage S3 authentication](https://supabase.com/docs/guides/storage/s3/authentication)
- [Supabase changelog](https://supabase.com/changelog)
