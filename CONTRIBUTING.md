# Contributing

SentinelFlow changes should be small, reviewable, and tied to platform behavior.

## Commit Style

Use conventional commit prefixes:

- `feat` for new behavior
- `fix` for bug fixes
- `test` for test coverage
- `docs` for documentation
- `chore` for maintenance

## Development Rules

- Keep organization scoping explicit.
- Add tests when changing incident, alert, auth, or workflow behavior.
- Prefer deterministic rule logic before using AI triage.
- Document new Silver task candidates in `docs/task-bank.md`.

