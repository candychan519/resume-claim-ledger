# Resume Claim Ledger

Evidence-bound resume submission coordinator for tracking claims, proof, JD fit, and submission readiness.

## Why This Exists

AI-assisted resume writing can quietly inflate scope, impact, and metrics. Resume Claim Ledger keeps each resume bullet tied to a local claim ledger so humans and agents can see what is verified, what needs proof, and what should be softened before submission.

## What It Does

- Turns resume bullets into a versioned claim ledger.
- Flags unsupported, overbroad, malformed, or rewrite-needed claims.
- Suggests safer wording without editing the source resume.
- Builds a submission plan from claims, an optional job description, and optional evidence files.
- Runs a policy-aware doctor gate before final handoff.
- Provides agent guardrails and skills for safe resume coordination.

## What It Does Not Do

- Does not rewrite your source resume automatically.
- Does not invent metrics, employers, dates, links, certifications, or scope.
- Does not use AI scoring for JD matching.
- Does not replace human evidence review or recruiter judgment.

Report-only means outputs are suggestions and gates, not source-file edits.

## Quickstart

Create a local claim ledger:

```bash
resume-ledger scan resume.md --out claims.yml
```

Get a compact submission triage view:

```bash
resume-ledger coordinate claims.yml --summary --out submission-summary.md
```

Build the full submission plan when you have a job description and evidence files:

```bash
resume-ledger coordinate claims.yml --job jd.md --evidence-dir evidence --out submission-plan.md
```

Run the final policy gate:

```bash
resume-ledger doctor claims.yml --policy policy/submission-policy.yml
```

Read the result as a handoff decision:

- Status: Blocked means unresolved evidence, scope, rewrite, or malformed-ledger issues remain.
- Status: Ready means the ledger passed the configured submission policy.

## Typical Workflow

1. Scan the resume into `claims.yml`.
2. Review blocker counts with `review` or a compact `coordinate --summary` report.
3. Attach evidence notes or evidence files for claims that need proof.
4. Compare the ledger with the target JD using `coordinate`.
5. Use `advise` or `report` for report-only wording and recruiter-readiness notes.
6. Run `doctor` with `policy/submission-policy.yml` before calling the resume ready.

## Agent Workflow

Agents should start with compact JSON, then stop at the policy gate:

```bash
resume-ledger coordinate claims.yml --summary --format json --out submission-summary.json
resume-ledger doctor claims.yml --policy policy/submission-policy.yml
```

Never call a resume submission-ready when the policy doctor fails. Use [docs/agent-guardrails.md](docs/agent-guardrails.md) and [policy/submission-policy.yml](policy/submission-policy.yml) as the source of truth for blocker handling.

Agents that support repository skills can use:

- [$resume-submission-coordinator](skills/resume-submission-coordinator/SKILL.md) for the end-to-end safe submission workflow.
- [$evidence-triage](skills/evidence-triage/SKILL.md) when they only need to classify missing proof before editing.

## Commands

| Command | Use when |
| --- | --- |
| `scan` | Create a claim ledger from resume bullets. |
| `review` | Count claim statuses in a ledger. |
| `report` | Write a Markdown claim review. |
| `advise` | Produce report-only career and Korean polish suggestions. |
| `coordinate` | Build a submission plan from claims, JD, and evidence. |
| `doctor` | Fail the final gate when unsafe claims remain. |

Common examples:

```bash
resume-ledger review claims.yml
resume-ledger report claims.yml --out claim-review.md
resume-ledger report claims.yml --out claim-review.md --strict
resume-ledger advise claims.yml --polish-ko --out advice.md
resume-ledger advise claims.yml --format json --out advice.json
resume-ledger coordinate claims.yml --format json --out submission-plan.json
resume-ledger coordinate claims.yml --strict --out submission-plan.md
```

`doctor` is the quick submission gate. `report --strict` and `coordinate --strict` also fail when malformed inputs or submission blockers remain after writing their reports.

## Example

Input:

```md
- 대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다.
- 배포 체크리스트를 도입했습니다. [evidence: release checklist]
```

Ledger:

```yaml
schema_version: 1
claims:
  - claim_id: CLM-001
    text: "대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다."
    category: impact
    status: too_broad
    evidence_note: "범위나 판단 기준을 뒷받침할 근거가 필요합니다."
    suggested_rewrite: "MLOps 시스템 구축 작업에 참여했습니다."
  - claim_id: CLM-002
    text: "배포 체크리스트를 도입했습니다."
    category: execution
    status: verified
    evidence_note: "release checklist"
    suggested_rewrite: ""
```

The first claim remains blocked until the scope is narrowed or evidence is attached. The second claim can pass because it has explicit evidence.

## Install

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

From this repository:

```bash
uv tool install .
```

From GitHub:

```bash
uv tool install git+https://github.com/candychan519/resume-claim-ledger
```

After the first PyPI release:

```bash
uv tool install resume-claim-ledger
```

## Local Development

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
uv run basedpyright
uv build
```

## Docs

| Document | Purpose |
| --- | --- |
| [docs/ledger-schema.md](docs/ledger-schema.md) | Ledger, Advice JSON, and Coordinate JSON schemas. |
| [docs/agent-guardrails.md](docs/agent-guardrails.md) | Safe behavior for AI agents. |
| [docs/releasing.md](docs/releasing.md) | Release and publishing process. |
| [docs/maintenance.md](docs/maintenance.md) | Maintainer checks and deterministic rule guidance. |
