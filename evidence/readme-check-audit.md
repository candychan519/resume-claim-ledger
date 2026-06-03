# README Check Audit

| README claim or gap | Source of truth | Status | Action |
| --- | --- | --- | --- |
| `uv tool install .` is documented without prerequisites | `pyproject.toml` requires Python `>=3.13`; project uses `uv` | Weak | Add README prerequisite wording for Python 3.13+ and uv. |
| GitHub install path is documented | `pyproject.toml` project name and repository URL | Accurate | Keep as-is. |
| PyPI install is documented as future-gated | No first PyPI release was executed in this workstream; `docs/releasing.md` documents release process | Accurate but isolated | Keep future-gated wording and link release docs. |
| Usage examples include `scan`, `review`, `report`, `report --strict`, and `advise` | `src/resume_claim_ledger/cli.py`; `tests/test_cli_e2e.py` | Accurate | Keep command order and clarify strict mode as a submission gate. |
| README says advice is report-only | `docs/ledger-schema.md` Advice Output; `tests/test_readme_contract.py` | Accurate | Keep report-only wording. |
| Advice JSON output is documented only by command | `docs/ledger-schema.md` documents Advice JSON fields | Weak | Link README users to schema docs for Advice JSON. |
| Sample YAML includes schema v1 fields | `docs/ledger-schema.md`; `qa/claims.yml` | Accurate | Keep sample and add schema-doc pointer. |
| Malformed ledger behavior is not discoverable from README | `tests/test_cli_e2e.py::test_report_when_ledger_is_malformed_does_not_crash` | Weak | Add concise note that malformed ledgers produce warnings in reports, not source edits. |
| Source behavior changes | Plan scope forbids `src/` edits | N/A | Do not edit `src/`. |
