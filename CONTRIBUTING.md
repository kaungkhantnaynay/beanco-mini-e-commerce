# Contributing to BeanCo

## Before starting

1. Read [the engineering standards](RULES.md).
2. Find the relevant item in [the delivery roadmap](docs/plans/README.md).
3. Inspect the current working tree and preserve unrelated changes.
4. Record material architectural decisions in `docs/decisions/`.

## Change expectations

- Keep each change focused and leave the repository runnable.
- Keep business rules in the Django backend rather than duplicating them in the UI.
- Add regression coverage for behavior changes and bug fixes.
- Update API, environment, migration, and operational documentation with the code.
- Never commit secrets, customer data, credentials, local databases, or generated
  dependency directories.

## Verification

Run the checks relevant to your change before opening a pull request:

```bash
npm ci
npm run lint
npx tsc --noEmit
npm test
npm run build

cd backend
uv sync --frozen --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy apps config
uv run pytest
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

## Pull requests

Explain the problem, the chosen solution, affected contracts or migrations, checks
performed, and remaining risks. CI must be green before merge.
