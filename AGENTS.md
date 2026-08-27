# BeanCo Agent Instructions

These instructions apply to the entire repository. Any more specific `AGENTS.md`
file may add constraints for its directory, but it may not weaken these rules.

## Mandatory preflight

Before editing, generating, or deleting any project file, every agent MUST:

1. Read this file completely.
2. Read [`RULES.md`](RULES.md) completely.
3. Read [`docs/plans/README.md`](docs/plans/README.md).
4. Read the plan file for the phase being implemented.
5. Inspect `git status --short` and preserve all existing user changes.
6. State which phase and acceptance criteria the work addresses.

If a required document cannot be found or conflicts with the requested work, stop
and report the problem before implementation. Do not silently invent a replacement
policy.

## Working agreement

- Implement only the requested phase or explicitly requested subset.
- Treat the phase plan's acceptance criteria as the definition of done.
- Do not begin a later phase to make the current change more impressive.
- Keep Next.js as the storefront and Django as the API/backend unless the user
  explicitly approves an architecture change.
- Add or update tests for every behavior change.
- Run the relevant verification commands before handoff. If a command cannot run,
  report the exact reason and do not claim it passed.
- Update the affected plan's progress checklist when implementation is completed.
- Record material architecture decisions in `docs/decisions/` as an ADR.
- Never commit secrets, real customer data, payment credentials, or production
  environment values.

## Required handoff

Every implementation handoff must state:

- Phase and plan item completed.
- Files and behavior changed.
- Migrations, environment variables, or operator actions required.
- Tests/checks run and their outcomes.
- Remaining risks or follow-up work.

