# Release and rollback runbook

## Before release

1. Confirm CI is green for the exact commit being released.
2. Confirm no unexplained critical or high security finding exists.
3. Confirm the latest PostgreSQL backup completed and record its timestamp.
4. Review application changes and every new migration for reversibility and data loss.
5. Record the current frontend/backend deployment identifiers and image digests.

## Release

1. Deploy the frontend and backend artifacts built from the same commit.
2. In the backend release environment, run `backend/scripts/release.sh`. This performs
   Django deployment checks, prints the migration plan, and then applies migrations.
3. Start or restart application replicas only after the release command succeeds.
4. Run:

   ```bash
   FRONTEND_URL=https://shop.example.com \
   BACKEND_URL=https://api.example.com \
   ./scripts/smoke-test.sh
   ```

5. Verify one privacy-safe correlated request in backend logs and watch error/latency
   signals during the release observation window.

## Rollback

1. Stop rollout of the failing artifact and retain logs plus the request IDs involved.
2. Redeploy the recorded previous frontend/backend artifacts.
3. Prefer leaving a backward-compatible migration applied. Do not reverse a schema or
   data migration merely because application code was rolled back.
4. If reversal is necessary, confirm the migration is reversible and a fresh backup
   exists, then run from `backend/`:

   ```bash
   python manage.py showmigrations APP_LABEL
   python manage.py migrate APP_LABEL PREVIOUS_MIGRATION
   ```

5. If migration reversal is unsafe, restore to a new database using the data-restore
   runbook and point the API to it only after validation.
6. Run smoke tests again and record the incident timeline and final deployed versions.
