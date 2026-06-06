## Summary
- Add deterministic `resume-ledger coordinate` submission planning for claim ledgers, optional JDs, and optional evidence directories.
- Add `resume-ledger coordinate --summary` for compact submission triage with counts and non-ready claims.
- Dogfood the workflow on current career materials and capture observations without modifying source resume/JD files.
- Document the coordinate workflow, JSON contract, summary mode, and CI gate expectations.

## Verification
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run basedpyright`
- `uv build`
- tmux manual QA for summary, full Markdown, JSON, strict malformed, and adjacent `advise`
- scope scan for LLM/API/network/source rewrite drift

## Evidence
- `evidence/followup-final-f1-full-gates.txt`
- `evidence/followup-final-f2-dogfood-review.txt`
- `evidence/followup-final-f3-manual-qa.txt`
- `evidence/followup-final-f4-scope-fidelity.txt`
- `evidence/followup-final-f5-cleanup-review.txt`
- `evidence/followup-final-root-review.txt`
