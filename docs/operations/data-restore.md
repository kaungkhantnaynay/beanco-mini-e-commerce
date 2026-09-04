# Database and media restore runbook

No restoration is complete until it has been tested against an isolated target. The
initial recovery objectives are:

- Recovery time objective (RTO): restore customer-facing service within four hours.
- Recovery point objective (RPO): lose no more than one hour of committed data.
- Backup retention: 35 rolling days.

The selected Render and R2 plans must be checked against these targets before purchase.
The targets remain provisional until an isolated restore drill demonstrates them.

## PostgreSQL restore drill

1. Record the chosen backup identifier, timestamp, and expected recovery point.
2. Restore it to a new isolated Render PostgreSQL instance; never overwrite the active
   production database during a drill.
3. Restrict connectivity to the validation operator and a temporary backend service.
4. Run `python manage.py migrate --plan`, then apply only migrations released after the
   backup.
5. Run `python manage.py check --deploy`, the backend test smoke subset, and read-only
   counts for users, products, inventory transactions, orders, and payment attempts.
6. Confirm order totals and inventory transaction history remain internally consistent.
7. Record restore duration and recovered timestamp, then compare them with the approved
   RTO and RPO.
8. Destroy the isolated restored service after evidence is approved under the provider's
   deletion procedure.

## Product media restore drill

1. Restore a versioned R2 backup into a new private bucket.
2. Verify object count, representative checksums, content types, and access controls.
3. Point a temporary backend configuration to the restored bucket and verify product
   images through approved public delivery URLs.
4. Record duration and evidence, then remove the temporary bucket after approval.
