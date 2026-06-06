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

## Coordinate Rules

Coordinate rules are deterministic and offline. Keep them submission-focused:

- Do not edit source resumes, ledgers, job descriptions, or evidence files.
- Do not add metrics, employers, dates, links, evidence, or JD matches that are not present in the inputs.
- Keep JD matching to deterministic keyword matching unless a future public dependency and schema contract are added.
- Do not expose absolute local paths in Coordinate JSON or Markdown output.
- Keep summary mode report-only; it should show action counts and non-ready claims without expanding ready claim details.
- Add a failing CLI test before changing `coordinate` behavior, including one adjacent regression check for `advise`, `doctor`, or `report`.
