# MoAI-Style Career Review Enhancement Plan

## TL;DR
> **Summary**: Extend `resume-claim-ledger` from an evidence checker into an offline career-quality reviewer that adds HR risk, career framing, and Korean polish suggestions without depending on private MoAI skill files.
> **Deliverables**:
> - `advise` CLI command for career/HR and Korean polish suggestions.
> - Independent rule modules for career risk and Korean AI-sounding phrase detection.
> - Markdown and JSON advice outputs that preserve original facts and suggest safer phrasing.
> - Tests, docs, QA evidence, and release notes.
> **Effort**: Medium
> **Parallel**: YES - 3 waves
> **Critical Path**: data model -> rule engines -> CLI/report integration -> docs/release verification

## Context

### Original Request
The user asked whether MoAI career/HR perspective suggestions and Korean humanization/polish review should be reflected in this project.

### Interview Summary
No extra user decision is required before implementation. Use the following defaults:
- Build an open-source independent implementation inspired by MoAI guidance.
- Do not import, vendor, or require local MoAI skill files.
- Prefer "suggestions" over automatic rewriting.
- Keep evidence checking as the core value; career/HR and Korean polish become an opt-in review layer.

### Relevant Skills Surveyed
- `omo:ulw-plan`: required because the user explicitly asked for an ultrawork plan.
- `moai-career-resume-builder`: relevant for Korean hiring-market framing such as USP/CAR, ATS, HR scan risk, AI authenticity, and role/result clarity.
- `humanize-korean`: relevant for Korean AI-sounding phrase detection, fact preservation, surgical edits, and over-polish guardrails.
- `omo:programming`: must be used during implementation because production changes will touch Python files.

### Research Findings
- Current CLI commands live in `src/resume_claim_ledger/cli.py`.
- Current claim model is `src/resume_claim_ledger/models.py::Claim`.
- Existing report generation is `src/resume_claim_ledger/reporter.py::build_report`.
- Existing scanner already creates `suggested_rewrite` for broad claims in `src/resume_claim_ledger/scanner.py`.
- Existing CLI E2E test pattern is `tests/test_cli_e2e.py::run_cli`.
- Current package dependencies are only `rich` and `typer`; keep new rules dependency-free unless a task explicitly proves a dependency is needed.

### Metis Review (gaps addressed)
- Risk: scope creep into full AI resume rewriting. Addressed by limiting v1 to deterministic suggestions.
- Risk: private skill dependency. Addressed by defining public, local rule modules.
- Risk: hallucinated career facts. Addressed by requiring suggestions to preserve original text facts and never invent metrics.
- Risk: English/global users. Addressed by making Korean polish opt-in and safe when no Korean patterns are present.
- Risk: output contract ambiguity. Addressed by supporting Markdown by default and JSON via `--format json`.
- Risk: HR attractiveness conflicting with evidence safety. Addressed by making evidence status the highest-priority signal.

## Work Objectives

### Core Objective
Add a deterministic `career review mode` that reviews claim ledgers for Korean-market HR readability and Korean AI-sounding phrasing while preserving the evidence ledger's fact-safety guarantees.

### Deliverables
- New data structures for career and polish suggestions.
- New rule module for career/HR review.
- New rule module for Korean polish suggestions.
- New `resume-ledger advise` CLI command.
- Report integration for `Evidence`, `Career Review`, and `Korean Polish` sections.
- Machine-readable JSON output for automation.
- README, ledger schema docs, maintenance docs, and changelog updates.
- QA artifacts under `evidence/`.

### Definition of Done
- `uv run pytest -q` passes.
- `uv run ruff check .` passes.
- `uv run basedpyright` passes.
- `uv build` passes.
- Manual QA through tmux proves:
  - career advice appears for broad/unclear Korean claims.
  - Korean polish suggestions appear for AI-sounding patterns.
  - empty/verified-only ledgers produce a calm no-suggestions result.

### Must Have
- Suggestions must cite the original `claim_id`.
- Suggestions must not mutate ledger files unless a future explicit command is added.
- Suggestions must not invent facts, dates, employers, metrics, or links.
- Korean polish must preserve original proper nouns, numbers, dates, and quoted phrases.
- CLI output must remain useful without network access.
- Evidence safety outranks HR appeal: a claim cannot be strengthened just because it would sound better to a recruiter.
- JSON output must include `claim_id`, `kind`, `severity`, `title`, `detail`, and `suggested_text`.

### Must NOT Have
- No LLM/API calls.
- No dependency on local MoAI skill directories.
- No automatic overwrite of the user's resume.
- No broad refactor of scanner/ledger parsing beyond what is required.
- No PyPI release attempt until TestPyPI/PyPI Trusted Publisher setup is completed by the account owner.

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.

- Test decision: TDD with pytest. Each production task starts by adding a failing test.
- QA policy: Every task includes an agent-run CLI scenario through tmux.
- Evidence path pattern: `evidence/task-{N}-{slug}.txt`.
- Full gate command:
  ```bash
  uv run pytest -q && uv run ruff check . && uv run basedpyright && uv build
  ```

## Execution Strategy

### Parallel Execution Waves
Wave 1:
- Task 1: Add suggestion data model.
- Task 2: Add career/HR rule engine.
- Task 3: Add Korean polish rule engine.

Wave 2:
- Task 4: Integrate suggestions into Markdown reporting.
- Task 5: Add `advise` CLI command.

Wave 3:
- Task 6: Add docs and README usage.
- Task 7: Add release/deployment verification and final QA.

### Dependency Matrix
- Task 1 blocks Tasks 2, 3, 4, 5.
- Tasks 2 and 3 block Tasks 4 and 5.
- Task 4 blocks Task 5 only if `advise` reuses report rendering.
- Tasks 4 and 5 block Task 6.
- All tasks block Task 7.

## TODOs

- [x] 1. Add Suggestion Data Model

  **What to do**:
  - Add `SuggestionKind = Literal["career", "korean_polish"]`.
  - Add `SuggestionSeverity = Literal["info", "warning", "critical"]`.
  - Add frozen dataclass `Suggestion` with `claim_id`, `kind`, `severity`, `title`, `detail`, `suggested_text`.
  - Add `suggestion_to_dict(suggestion: Suggestion) -> dict[str, str]` for JSON output.
  - Keep existing `Claim` unchanged in this task.

  **Must NOT do**:
  - Do not add CLI behavior.
  - Do not change ledger serialization.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 2, 3, 4, 5 | Blocked By: none

  **References**:
  - Pattern: `src/resume_claim_ledger/models.py` - existing frozen dataclass and Literal style.
  - Tests: create `tests/test_suggestions_model.py`.

  **Acceptance Criteria**:
  - [ ] Test first: `uv run pytest tests/test_suggestions_model.py::test_suggestion_model_preserves_claim_reference -q` fails before implementation.
  - [ ] Test first: `uv run pytest tests/test_suggestions_model.py::test_suggestion_to_dict_exposes_stable_output_contract -q` fails before implementation.
  - [ ] Same tests pass after implementation.
  - [ ] `uv run basedpyright` reports zero errors.

  **QA Scenarios**:
  ```text
  Scenario: suggestion model can be imported by the installed package
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-model 'uv run python -c "from resume_claim_ledger.models import Suggestion; print(Suggestion(claim_id=\"CLM-001\", kind=\"career\", severity=\"warning\", title=\"Role unclear\", detail=\"역할이 불명확합니다.\", suggested_text=\"역할을 분리해 쓰세요.\"))"'
      tmux capture-pane -pt ulw-qa-model -S -200
    Expected: output contains "CLM-001" and "career"
    Evidence: evidence/task-1-suggestion-model.txt
  ```

  **Commit**: YES | Message: `feat(model): add review suggestion model` | Files: `src/resume_claim_ledger/models.py`, `tests/test_suggestions_model.py`

- [x] 2. Add Career/HR Rule Engine

  **What to do**:
  - Add `src/resume_claim_ledger/career_advisor.py`.
  - Implement `advise_career(claims: list[Claim]) -> list[Suggestion]`.
  - Rules for v1:
    - Broad impact claim without concrete metric -> warning: "성과 범위가 넓습니다."
    - Execution claim with no role/action clarity -> info: "본인 역할을 더 분명히 쓰세요."
    - Verified claim with evidence remains calm and does not get a career warning; Korean polish may still flag style separately.
    - Terms like `대규모`, `안정적인`, `최적화`, `개선했습니다`, `향상` trigger HR risk when evidence is weak.
  - Suggested text must soften overclaiming and avoid invented metrics.
  - Evidence status is authoritative: `too_broad`, `needs_evidence`, and `rewrite_needed` may receive career warnings; `verified` cannot be strengthened or downgraded by HR appeal alone.

  **Must NOT do**:
  - Do not use LLM calls.
  - Do not add ATS/JD matching yet.
  - Do not modify scanner classification in this task.
  - Do not quote or expose internal URLs, file paths, account IDs, or ticket IDs inside generated suggestion detail.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4, 5 | Blocked By: 1

  **References**:
  - Pattern: `src/resume_claim_ledger/scanner.py::_safer_rewrite` - deterministic Korean rewrite style.
  - Pattern: `tests/test_scanner.py::test_extract_claims_when_resume_has_markdown_bullets`.

  **Acceptance Criteria**:
  - [ ] Test first: `uv run pytest tests/test_career_advisor.py::test_career_advice_flags_broad_unproven_impact_claim -q` fails before implementation.
  - [ ] Test first: `uv run pytest tests/test_career_advisor.py::test_career_advice_does_not_warn_verified_execution_claim -q` fails before implementation.
  - [ ] Test first: `uv run pytest tests/test_career_advisor.py::test_career_advice_redacts_sensitive_evidence_details -q` fails before implementation.
  - [ ] All tests pass after implementation.

  **QA Scenarios**:
  ```text
  Scenario: broad Korean impact claim receives HR warning
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-career 'uv run python -c "from resume_claim_ledger.models import Claim; from resume_claim_ledger.career_advisor import advise_career; claims=[Claim(\"CLM-001\",\"대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다.\",\"impact\",\"too_broad\",\"근거 필요\",\"\")]; print(advise_career(claims)[0].title)"'
      tmux capture-pane -pt ulw-qa-career -S -200
    Expected: output contains "성과 범위"
    Evidence: evidence/task-2-career-warning.txt
  ```

  **Commit**: YES | Message: `feat(advisor): add career risk rules` | Files: `src/resume_claim_ledger/career_advisor.py`, `tests/test_career_advisor.py`

- [x] 3. Add Korean Polish Rule Engine

  **What to do**:
  - Add `src/resume_claim_ledger/korean_polish.py`.
  - Implement `advise_korean_polish(claims: list[Claim]) -> list[Suggestion]`.
  - Rules for v1:
    - Detect `~를 통해`, `~에 있어서`, `성장했습니다`, `탁월한`, `뛰어난`, `결론적으로`, `시사하는 바`.
    - Preserve numbers, English abbreviations, dates, and quoted phrases.
    - Return suggestions only; do not mutate claim text.
    - Include a conservative suggested text when a deterministic replacement is safe.
  - Add invariant helper tests that compare original and suggested text for preserved numbers and quoted spans.

  **Must NOT do**:
  - Do not build a full humanizer pipeline.
  - Do not calculate change-rate metrics in v1.
  - Do not alter original resume files.
  - Do not replace a factual claim with a stronger claim.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 4, 5 | Blocked By: 1

  **References**:
  - MoAI guidance source: `humanize-korean` says fact preservation and surgical edits are mandatory.
  - Pattern: `src/resume_claim_ledger/scanner.py::EVIDENCE_PATTERN` for simple regex constants.

  **Acceptance Criteria**:
  - [ ] Test first: `uv run pytest tests/test_korean_polish.py::test_polish_flags_through_phrase_without_changing_numbers -q` fails before implementation.
  - [ ] Test first: `uv run pytest tests/test_korean_polish.py::test_polish_returns_no_suggestion_for_plain_specific_sentence -q` fails before implementation.
  - [ ] Test first: `uv run pytest tests/test_korean_polish.py::test_polish_preserves_quoted_phrases -q` fails before implementation.
  - [ ] All tests pass after implementation.

  **QA Scenarios**:
  ```text
  Scenario: Korean AI-like phrasing receives polish suggestion
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-polish 'uv run python -c "from resume_claim_ledger.models import Claim; from resume_claim_ledger.korean_polish import advise_korean_polish; claims=[Claim(\"CLM-001\",\"배포 자동화를 통해 처리 시간을 30% 개선했습니다.\",\"impact\",\"needs_evidence\",\"근거 필요\",\"\")]; print(advise_korean_polish(claims)[0].detail)"'
      tmux capture-pane -pt ulw-qa-polish -S -200
    Expected: output contains "를 통해" and preserves "30%"
    Evidence: evidence/task-3-korean-polish.txt
  ```

  **Commit**: YES | Message: `feat(polish): add Korean polish rules` | Files: `src/resume_claim_ledger/korean_polish.py`, `tests/test_korean_polish.py`

- [x] 4. Integrate Suggestions Into Markdown Reports

  **What to do**:
  - Extend `build_report` to accept optional `suggestions: list[Suggestion] | None`.
  - Add sections:
    - `## Career Review`
    - `## Korean Polish`
  - Group suggestions by `claim_id`.
  - Keep existing report output unchanged when `suggestions` is omitted or empty.

  **Must NOT do**:
  - Do not change summary counts.
  - Do not change existing warning behavior.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 5, 6 | Blocked By: 1, 2, 3

  **References**:
  - Pattern: `src/resume_claim_ledger/reporter.py::build_report`.
  - Regression test: `tests/test_reporter.py::test_build_report_when_claims_have_mixed_statuses`.

  **Acceptance Criteria**:
  - [ ] Test first: `uv run pytest tests/test_reporter.py::test_build_report_includes_career_and_polish_suggestions -q` fails before implementation.
  - [ ] Regression: `uv run pytest tests/test_reporter.py::test_build_report_when_claims_have_mixed_statuses -q` still passes.
  - [ ] New report sections are absent when no suggestions are passed.

  **QA Scenarios**:
  ```text
  Scenario: report renderer includes suggestion sections
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-report 'uv run pytest tests/test_reporter.py::test_build_report_includes_career_and_polish_suggestions -q'
      tmux capture-pane -pt ulw-qa-report -S -200
    Expected: pytest exits 0 and output contains "1 passed"
    Evidence: evidence/task-4-report-suggestions.txt
  ```

  **Commit**: YES | Message: `feat(report): include career review suggestions` | Files: `src/resume_claim_ledger/reporter.py`, `tests/test_reporter.py`

- [x] 5. Add `advise` CLI Command

  **What to do**:
  - Add `resume-ledger advise claims.yml --out advice.md`.
  - Options:
    - `--career/--no-career`, default `--career`.
    - `--polish-ko/--no-polish-ko`, default `--polish-ko`.
    - `--format markdown|json`, default `markdown`.
    - `--strict`, exits non-zero when any `critical` suggestion exists.
  - Read ledger via `read_ledger_result`.
  - Combine career and polish suggestions.
  - Write Markdown advice using the report integration from Task 4.
  - Write JSON advice as:
    ```json
    {
      "schema_version": 1,
      "suggestions": [
        {
          "claim_id": "CLM-001",
          "kind": "career",
          "severity": "warning",
          "title": "성과 범위가 넓습니다.",
          "detail": "근거가 약한 성과 주장은 과장으로 읽힐 수 있습니다.",
          "suggested_text": "MLOps 시스템 구축 작업에 참여했습니다."
        }
      ]
    }
    ```

  **Must NOT do**:
  - Do not modify the ledger file.
  - Do not require a resume markdown input for this command.
  - Do not add external service credentials.
  - Do not print private MoAI path names or skill names in user-facing output.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 6, 7 | Blocked By: 2, 3, 4

  **References**:
  - Pattern: `src/resume_claim_ledger/cli.py::report`.
  - CLI test helper: `tests/test_cli_e2e.py::run_cli`.

  **Acceptance Criteria**:
  - [ ] Test first: `uv run pytest tests/test_cli_e2e.py::test_advise_writes_career_and_korean_polish_report -q` fails before implementation.
  - [ ] Test first: `uv run pytest tests/test_cli_e2e.py::test_advise_when_no_suggestions_writes_calm_report -q` fails before implementation.
  - [ ] Test first: `uv run pytest tests/test_cli_e2e.py::test_advise_json_outputs_stable_suggestion_contract -q` fails before implementation.
  - [ ] All tests pass after implementation.
  - [ ] `resume-ledger --help` lists `advise`.

  **QA Scenarios**:
  ```text
  Scenario: advise command writes HR and Korean polish report
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-advise 'uv run resume-ledger scan qa/sample-resume.md --out evidence/qa-advise-claims.yml && uv run resume-ledger advise evidence/qa-advise-claims.yml --out evidence/qa-advise.md && sed -n "1,220p" evidence/qa-advise.md'
      tmux capture-pane -pt ulw-qa-advise -S -300
    Expected: captured output contains "Career Review" and "Korean Polish"
    Evidence: evidence/task-5-advise-cli.txt

  Scenario: disabling Korean polish omits Korean Polish section
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-advise-no-polish 'uv run resume-ledger advise evidence/qa-advise-claims.yml --out evidence/qa-advise-no-polish.md --no-polish-ko && sed -n "1,220p" evidence/qa-advise-no-polish.md'
      tmux capture-pane -pt ulw-qa-advise-no-polish -S -300
    Expected: captured output does not contain "Korean Polish"
    Evidence: evidence/task-5-advise-cli-no-polish.txt

  Scenario: JSON advice output is machine-readable
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-advise-json 'uv run resume-ledger advise evidence/qa-advise-claims.yml --out evidence/qa-advise.json --format json && python -m json.tool evidence/qa-advise.json'
      tmux capture-pane -pt ulw-qa-advise-json -S -300
    Expected: captured output contains "\"schema_version\"" and "\"suggestions\""
    Evidence: evidence/task-5-advise-cli-json.txt
  ```

  **Commit**: YES | Message: `feat(cli): add career advice command` | Files: `src/resume_claim_ledger/cli.py`, `tests/test_cli_e2e.py`

- [x] 6. Update Documentation and Examples

  **What to do**:
  - Update `README.md` with `advise` usage and a short sample output.
  - Update `docs/ledger-schema.md` to state ledger suggestions are not part of ledger schema v1, but advice JSON has its own output contract.
  - Update `docs/maintenance.md` with rule-maintenance guidance.
  - Update `CHANGELOG.md` under `Unreleased`.
  - Add one QA fixture if needed: `qa/career-polish-resume.md`.

  **Must NOT do**:
  - Do not claim PyPI install works until actual PyPI release exists.
  - Do not mention private MoAI skills as runtime dependencies.
  - Do not imply the tool replaces professional career judgment.

  **Parallelization**: Can Parallel: YES | Wave 3 | Blocks: 7 | Blocked By: 5

  **References**:
  - Pattern: `README.md` current command examples.
  - Pattern: `docs/maintenance.md` concise maintenance sections.
  - Contract tests: `tests/test_readme_contract.py`, `tests/test_ledger_schema_docs.py`.

  **Acceptance Criteria**:
  - [ ] Test first: `uv run pytest tests/test_readme_contract.py::test_readme_documents_advise_command -q` fails before docs update.
  - [ ] Test first: `uv run pytest tests/test_ledger_schema_docs.py::test_ledger_schema_notes_suggestions_are_report_only -q` fails before docs update.
  - [ ] Test first: `uv run pytest tests/test_ledger_schema_docs.py::test_docs_define_advice_json_contract -q` fails before docs update.
  - [ ] All tests pass after docs update.

  **QA Scenarios**:
  ```text
  Scenario: README documented command works
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-docs 'uv run resume-ledger --help && uv run resume-ledger advise --help'
      tmux capture-pane -pt ulw-qa-docs -S -300
    Expected: captured output contains "advise" and "--polish-ko"
    Evidence: evidence/task-6-docs-help.txt
  ```

  **Commit**: YES | Message: `docs: document career advice mode` | Files: `README.md`, `docs/ledger-schema.md`, `docs/maintenance.md`, `CHANGELOG.md`, optional `qa/career-polish-resume.md`, docs contract tests

- [ ] 7. Final Deployment Readiness Verification

  **What to do**:
  - Run full local gate.
  - Build package.
  - Run CLI QA through the built source command.
  - Verify GitHub workflow contract tests still cover CI/release/security.
  - Commit any final docs or QA fixture changes.
  - Push branch and create PR if the user asks to execute and publish this plan.

  **Must NOT do**:
  - Do not publish to TestPyPI/PyPI until account-side Trusted Publisher setup is complete.
  - Do not merge without passing remote CI.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: final | Blocked By: all implementation tasks

  **References**:
  - Local gate: `docs/maintenance.md`.
  - Release setup: `docs/releasing.md`.
  - CI contracts: `tests/test_github_actions_contract.py`.

  **Acceptance Criteria**:
  - [ ] `uv run pytest -q` passes.
  - [ ] `uv run ruff check .` passes.
  - [ ] `uv run basedpyright` passes.
  - [ ] `uv build` passes.
  - [ ] `git diff --check` passes.

  **QA Scenarios**:
  ```text
  Scenario: full installed CLI flow with advice report
    Tool: tmux
    Steps:
      tmux new-session -d -s ulw-qa-final 'uv run resume-ledger scan qa/sample-resume.md --out evidence/final-claims.yml && uv run resume-ledger advise evidence/final-claims.yml --out evidence/final-advice.md && uv run resume-ledger report evidence/final-claims.yml --out evidence/final-claim-review.md && sed -n "1,260p" evidence/final-advice.md'
      tmux capture-pane -pt ulw-qa-final -S -400
    Expected: captured output contains claim IDs, "Career Review", and "Korean Polish"
    Evidence: evidence/task-7-final-cli.txt

  Scenario: cleanup receipt
    Tool: tmux
    Steps:
      tmux ls | grep 'ulw-qa-' || true
    Expected: no active ulw-qa tmux sessions remain after cleanup
    Evidence: evidence/task-7-cleanup.txt
  ```

  **Commit**: YES | Message: `chore: verify career advice release readiness` | Files: evidence artifacts only if the user wants QA artifacts versioned; otherwise do not commit evidence

## Final Verification Wave
> ALL must APPROVE before calling the implementation complete.

- [ ] F1. Plan Compliance Audit
  - Confirm each task has test-first instructions, QA scenario, acceptance criteria, and commit message.
- [ ] F2. Code Quality Review
  - Run `uv run ruff check .` and `uv run basedpyright`.
- [ ] F3. Real Manual QA
  - Run every tmux scenario listed above and capture evidence files.
- [ ] F4. Scope Fidelity Check
  - Confirm no private MoAI files are imported.
  - Confirm no source resume file is overwritten.
  - Confirm no external network/API is required.
  - Confirm JSON output schema is stable and documented.
  - Confirm advice suggestions do not strengthen unverified claims.

## Commit Strategy
- Use one conventional commit per task.
- Create a branch such as `codex/career-review-mode` during implementation.
- Do not auto-merge. Open a PR and wait for remote CI.
- Suggested PR title: `[codex] Add career review mode`.

## Success Criteria
- Users can run `resume-ledger advise claims.yml --out advice.md`.
- Users can run `resume-ledger advise claims.yml --format json --out advice.json`.
- The advice report includes HR/career suggestions and Korean polish suggestions for risky Korean resume claims.
- Verified or specific claims do not receive noisy warnings.
- Existing `scan`, `review`, and `report` behavior remains backward compatible.
- The package builds and passes all local gates.
- Remote CI passes on the implementation branch before merge.
