# README Check Plan

## Objective

Make `README.md` accurate and publication-ready for the public `resume-claim-ledger` GitHub repository without changing CLI behavior.

## Target

- Repository: `C:\Users\wjfeo\dev\resume-claim-ledger`
- Public remote: `https://github.com/candychan519/resume-claim-ledger`
- Primary file: `README.md`
- Supporting public-contract files:
  - `tests/test_readme_contract.py`
  - `tests/test_cli_e2e.py`
  - `docs/ledger-schema.md`
  - `docs/releasing.md`
  - `pyproject.toml`
  - `.github/workflows/ci.yml`
  - `.github/workflows/release.yml`

## Scope

### Include

- Verify README product promise against actual CLI behavior.
- Verify install instructions against project metadata and release state.
- Verify every README command example against the CLI surface.
- Verify sample YAML against ledger schema v1.
- Verify career/HR and Korean polish wording describes report-only advice.
- Add or tighten README contract tests before any README wording change.
- Capture local RED, GREEN, full-gate, and tmux manual-QA evidence.

### Exclude

- No CLI behavior changes.
- No edits under `src/`.
- No schema migration.
- No PyPI/TestPyPI release.
- No broad documentation rewrite outside README unless a contradiction is found.
- No GitHub PR/merge unless the user explicitly asks to execute this plan.

## Current Findings

- README already documents `scan`, `review`, `report`, and `advise`.
- README already states advice is report-only and does not edit the ledger or resume file.
- README sample now includes `schema_version: 1`, `category`, and `suggested_rewrite`.
- `docs/ledger-schema.md` documents ledger schema v1 and Advice JSON output.
- `docs/releasing.md` documents TestPyPI-first release and Trusted Publisher setup.
- CI and release workflows run `pytest`, `ruff`, `basedpyright`, and `uv build`.

## Acceptance Criteria

1. README makes only behavior-true claims.
2. README install paths distinguish local source install, GitHub install, and future PyPI install.
3. README command examples can be copied into a fresh terminal flow and produce the documented artifacts.
4. README sample output matches schema v1 and does not imply advice suggestions are written back into source resumes.
5. README links or references the schema and release docs where a public user would need details.
6. All README changes are protected by tests written before the README edits.
7. Manual QA is captured through tmux transcripts, not inferred from tests.

## Test And QA Matrix

| Scenario | Automated Test Written First | Manual-QA Channel | Concrete Manual Invocation | Binary Observable |
| --- | --- | --- | --- | --- |
| Happy path README command flow | `tests/test_readme_contract.py::test_readme_usage_commands_match_cli_flow` | tmux | `tmux new-session -d -s ulw-qa-readme-happy 'bash'`; send `uv run resume-ledger scan qa/sample-resume.md --out /tmp/readme-claims.yml`, `uv run resume-ledger review /tmp/readme-claims.yml`, `uv run resume-ledger report /tmp/readme-claims.yml --out /tmp/readme-report.md`, `uv run resume-ledger advise /tmp/readme-claims.yml --out /tmp/readme-advice.md` | Transcript contains `Wrote 3 claims`, `too_broad`, `Wrote report`, and `Wrote advice`; generated files exist. |
| Empty resume boundary | `tests/test_readme_contract.py::test_readme_mentions_empty_resume_behavior_or_links_cli_docs` | tmux | `tmux new-session -d -s ulw-qa-readme-empty 'bash'`; send `uv run resume-ledger scan qa/empty-resume.md --out /tmp/readme-empty.yml` | Transcript contains `Wrote 0 claims`; ledger contains `schema_version: 1`. |
| Malformed ledger failure surface | `tests/test_readme_contract.py::test_readme_links_error_or_schema_guidance_for_malformed_ledgers` | tmux | `tmux new-session -d -s ulw-qa-readme-malformed 'bash'`; send `uv run resume-ledger report qa/malformed.yml --out /tmp/readme-malformed-report.md` | Transcript exits cleanly; report contains `Malformed ledger`. |
| Strict mode unresolved-claim gate | `tests/test_readme_contract.py::test_readme_documents_strict_mode_as_submission_gate` | tmux | `tmux new-session -d -s ulw-qa-readme-strict 'bash'`; send `uv run resume-ledger report qa/claims.yml --out /tmp/readme-strict.md --strict` | Transcript shows non-zero strict failure and stderr mentions unresolved status. |
| Advice report-only regression | `tests/test_readme_contract.py::test_readme_advice_section_separates_ledger_rewrites_from_report_suggestions` | tmux | `tmux new-session -d -s ulw-qa-readme-advise 'bash'`; send `cp qa/claims.yml /tmp/readme-advice-claims.yml`, `cp /tmp/readme-advice-claims.yml /tmp/readme-advice-claims.before.yml`, `uv run resume-ledger advise /tmp/readme-advice-claims.yml --out /tmp/readme-advice.md`, `diff -u /tmp/readme-advice-claims.before.yml /tmp/readme-advice-claims.yml` | Transcript shows `Wrote advice`; ledger diff command exits zero. |
| Advice JSON public contract | `tests/test_readme_contract.py::test_readme_documents_advice_json_schema_or_schema_doc_link` | tmux | `tmux new-session -d -s ulw-qa-readme-json 'bash'`; send `uv run resume-ledger advise qa/claims.yml --format json --out /tmp/readme-advice.json`, then `grep '"schema_version": 1' /tmp/readme-advice.json` and `grep '"suggestions"' /tmp/readme-advice.json` | Transcript shows JSON advice written and both grep commands exit zero. |

## Implementation Plan

### Task 1: Baseline README Audit

1. Read `README.md`, `pyproject.toml`, `docs/ledger-schema.md`, `docs/releasing.md`, and CLI tests.
2. Create an audit table with columns: README claim, source of truth, status, action.
3. Record output in `evidence/readme-check-audit.md`.
4. Do not edit README in this task.

Verification:
- No code or README diff except the evidence artifact.
- `git diff -- README.md` is empty.
- `git diff -- src` is empty.

### Task 2: Add Failing README Contract Tests

1. Add the tests listed in the Test And QA Matrix to `tests/test_readme_contract.py`.
2. Tests must assert the missing or weak README contract discovered in Task 1.
3. Run only the new tests before editing README.
4. Capture RED output to `evidence/readme-check-red.txt`.
5. If the audit finds no README gap, stop and report that no README edit is needed; do not manufacture a failing test.

Verification:
- The new tests fail for README-contract reasons.
- Failure messages identify the missing README wording or link.

### Task 3: Patch README Only

1. Update `README.md` to satisfy the failing tests.
2. Keep wording concise and behavior-true.
3. Prefer links to `docs/ledger-schema.md` and `docs/releasing.md` over duplicating long policy text.
4. Do not edit CLI code.

Required README content decisions:
- Keep the tagline report-only: no automatic source rewrite claim.
- Under Install, keep PyPI wording conditional until the first PyPI release actually exists.
- Add or keep Python/uv prerequisite wording if Task 1 finds a first-time user cannot infer it.
- Under Usage, keep commands copyable and in the order `scan -> review -> report -> advise`.
- Add a short pointer to schema details after the sample.
- Add a short pointer to release/install details for first-time publishers or package users.
- Mention `advise --format json` together with `docs/ledger-schema.md` if the audit finds JSON output underexplained.

Verification:
- Run new tests and capture GREEN output to `evidence/readme-check-green.txt`.

### Task 4: Full Local Gate

Run:

```bash
uv run pytest -q
uv run ruff check .
uv run basedpyright
uv build
git diff --check
```

Capture combined output to `evidence/readme-check-full-gates.txt`.

Pass criteria:
- All commands exit zero.
- Build creates `dist/resume_claim_ledger-0.1.0.tar.gz` and `.whl`.
- `README.md` remains valid as the `pyproject.toml` package long description.
- `git diff -- src` is empty.

### Task 5: tmux Manual QA

Run one tmux session per scenario in the Test And QA Matrix.

For each session:
1. Create session with the exact scenario name.
2. Run the concrete commands.
3. Capture transcript:

```bash
tmux capture-pane -t <session> -pS -500 > evidence/<session>.txt
```

4. Kill the session:

```bash
tmux kill-session -t <session>
```

5. Record cleanup receipt:

```bash
tmux ls
```

Pass criteria:
- Each transcript contains the binary observable listed in the matrix.
- No `ulw-qa-readme-*` tmux session remains.
- Store cleanup receipt in `evidence/readme-check-tmux-cleanup.txt`.

### Optional Task 5B: Network Install Smoke, Only If User Requests Public Install Verification

Do not run this by default because it depends on network, GitHub availability, and package release state.

If requested, run in a temporary directory:

```bash
uv tool install git+https://github.com/candychan519/resume-claim-ledger
resume-ledger --help
```

Do not test `uv tool install resume-claim-ledger` until the first PyPI release exists. Before PyPI release, README must keep that command clearly future-gated.

### Task 6: Commit And PR, If Execution Is Authorized

1. Create branch: `codex/readme-check`.
2. Stage only README, tests, plan/evidence files created for this work.
3. Commit:

```bash
git commit -m "docs: improve readme public contract"
```

4. Push branch.
5. Open a PR against `main`.
6. Watch PR CI.
7. Squash merge only after CI passes and the user approves merge if not already preauthorized.

## Final Verification Wave

Before reporting done after execution:

1. Confirm `git status --short --branch`.
2. Confirm RED, GREEN, full-gate, and tmux evidence files exist.
3. Confirm no tmux sessions remain.
4. Confirm README diff is limited to audit findings.
5. Confirm every acceptance criterion maps to at least one automated test and one tmux artifact.

## Defaults Applied

- Target repository defaults to `resume-claim-ledger` because the immediately preceding work and GitHub publication were for that repo.
- Manual QA defaults to tmux because README examples are CLI-facing.
- No source behavior work is planned unless audit evidence proves README cannot be made truthful without changing the product.
- If README is already accurate after Task 1, stop after the audit and recommend no edit.
- External GitHub/PyPI install smoke is optional, not part of the default deterministic gate.

## Auto-Resolved Metis Findings

- Ambiguity resolved in favor of planning for `resume-claim-ledger`, not the parent `career` README.
- Edit scope allows `README.md`, README tests, docs links, plan, and evidence only; it explicitly forbids `src/` changes.
- Existing passing README tests do not count as RED; RED must come from newly discovered audit gaps.
- tmux evidence filenames are fixed under `evidence/` with one transcript per `ulw-qa-readme-*` session plus cleanup receipt.
- PyPI install is treated as future-gated until a real first release exists.
