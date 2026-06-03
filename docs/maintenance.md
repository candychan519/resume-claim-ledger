# Maintenance

## Routine Checks

Run the local gate before merging:

```bash
uv run pytest -q
uv run ruff check .
uv run basedpyright
uv build
```

## Dependencies

Dependabot tracks GitHub Actions and uv/Python dependencies. Review dependency updates with the same local gate.

## Release Safety

Use GitHub environments for TestPyPI and PyPI. Keep production publishing behind manual approval.

## Advice Rules

Career and Korean polish rules are deterministic and offline. Keep them conservative:

- Evidence safety outranks recruiter appeal.
- Do not add metrics, employers, dates, links, or stronger claims that are not already present.
- Do not import private local MoAI skill files; public package behavior must be reproducible from this repository alone.
- Add a failing test before each new rule, including one quiet-case test that proves specific verified wording is not flagged.
