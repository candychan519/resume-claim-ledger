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

Current releases are artifact-only releases. Do not publish to TestPyPI or PyPI
from the release workflow while package-index publishing is intentionally deferred.
Keep TestPyPI and PyPI Trusted Publishing setup in `docs/releasing.md`
as future guidance, not an active maintenance requirement.

## Living Rules and Skills

This project is still evolving. Treat repository rules, skills, and guardrails
as working agreements rather than permanent policy.

- When real work shows friction, make the smallest relevant update in the
  same PR that exposed it.
- Prefer one local edit over a new backlog, automation, or evaluation process.
- Promote a rule only after the same issue has repeated across multiple tasks.
- Add or strengthen hard rules immediately only for safety, data loss, security,
  secret leakage, or claim-inflation risk.
- Do not add automation, evaluation frameworks, or SkillOpt while the workflow
  is still changing quickly.
- Keep contract tests focused on triggers, hard stops, metadata, and safety
  boundaries; avoid pinning full skill prose unless the exact wording is itself
  the contract.

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

## Repository Intake Rules

Repository intake must stay static, deterministic, and report-only:

- Keep no code execution in target repositories: no package managers, tests, builds, scripts, imports, or hooks.
- Do not infer metrics, ownership, employer, dates, production usage, or scope from repository contents.
- Keep all generated paths repository-relative and redact private remotes or secret contents.
- Add a failing CLI test before changing `repo intake` behavior, including one safety regression for non-git input, secrets, or path leakage.
- Keep `knowledge-graph.json` export-ready, but do not document unsupported import commands.

## Agent Guardrails

Keep the default policy in `policy/submission-policy.yml` conservative. Agent-facing workflows should run `resume-ledger doctor claims.yml --policy policy/submission-policy.yml` before handoff and should treat any policy violation as a submission blocker.
