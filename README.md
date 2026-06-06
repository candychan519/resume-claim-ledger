# Resume Claim Ledger

Track and verify resume claims, then suggest safer wording before submission.

## Install

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

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

Release and publishing details live in [docs/releasing.md](docs/releasing.md).

For local development:

```bash
uv sync --dev
uv run pytest -q
uv run ruff check .
uv run basedpyright
uv build
```

## Usage

```bash
resume-ledger scan resume.md --out claims.yml
resume-ledger review claims.yml
resume-ledger doctor claims.yml
resume-ledger doctor claims.yml --policy policy/submission-policy.yml
resume-ledger report claims.yml --out claim-review.md
resume-ledger report claims.yml --out claim-review.md --strict
resume-ledger advise claims.yml --out advice.md
resume-ledger advise claims.yml --format json --out advice.json
resume-ledger coordinate claims.yml --job jd.md --evidence-dir evidence --out submission-plan.md
resume-ledger coordinate claims.yml --summary --out submission-summary.md
resume-ledger coordinate claims.yml --summary --format json --out submission-summary.json
resume-ledger coordinate claims.yml --format json --out submission-plan.json
resume-ledger coordinate claims.yml --strict --out submission-plan.md
```

Use `doctor` as the quick submission gate: unresolved claims or malformed ledger
warnings exit non-zero before a final resume handoff. Use `report --strict` when
you also need to write the markdown review file as part of the same gate.
Malformed ledger files are reported as warnings, including `Malformed ledger`
messages, instead of editing the source file.

## Recommended Workflow

Start by turning a resume into a local claim ledger:

```bash
resume-ledger scan resume.md --out claims.yml
```

Start with `--summary` when you want a quick submission triage view:

```bash
resume-ledger coordinate claims.yml --summary --out submission-summary.md
```

Use the full submission plan when you have a job description and evidence files:

```bash
resume-ledger coordinate claims.yml --job jd.md --evidence-dir evidence --out submission-plan.md
```

Use JSON when another tool needs stable structured output:

```bash
resume-ledger coordinate claims.yml --format json --out submission-plan.json
```

Before a final handoff, run the submission gate:

```bash
resume-ledger doctor claims.yml
resume-ledger doctor claims.yml --policy policy/submission-policy.yml
```

For agent-assisted work, use the default policy file and checklist in
[policy/submission-policy.yml](policy/submission-policy.yml) and
[docs/agent-guardrails.md](docs/agent-guardrails.md).

Agents that support repository skills can use
[$resume-submission-coordinator](skills/resume-submission-coordinator/SKILL.md)
for the end-to-end safe submission workflow.

## Why This Exists

AI-assisted resume writing can quietly inflate scope, impact, and metrics. Resume Claim Ledger keeps a local evidence ledger so each resume bullet can be reviewed before submission. Advice is report-only: it can suggest safer wording, but it does not rewrite your source resume or ledger.

## Career Advice Mode

`advise` adds offline career/HR and Korean polish suggestions on top of the evidence ledger:

```bash
resume-ledger advise claims.yml --out advice.md
resume-ledger advise claims.yml --out advice.md --no-polish-ko
resume-ledger advise claims.yml --format json --out advice.json
```

- Career review flags claims that may read as overbroad or unclear to a recruiter.
- Korean polish flags AI-sounding phrases such as `~를 통해` without rewriting the source resume.
- Suggestions are report-only. They do not edit the ledger or resume file.
- Evidence safety comes first: the tool does not invent metrics, dates, employers, or stronger claims.

Use `--polish-ko` to keep Korean polish enabled, or `--no-polish-ko` to produce only career/HR advice.
Advice JSON uses a stable report-only schema; see [docs/ledger-schema.md](docs/ledger-schema.md).

## Coordinate Mode

`coordinate` turns a claim ledger, optional job description, and optional evidence directory into a submission action plan:

```bash
resume-ledger coordinate claims.yml --job jd.md --evidence-dir evidence --out submission-plan.md
resume-ledger coordinate claims.yml --summary --out submission-summary.md
resume-ledger coordinate claims.yml --summary --format json --out submission-summary.json
resume-ledger coordinate claims.yml --format json --out submission-plan.json
resume-ledger coordinate claims.yml --strict --out submission-plan.md
```

- Coordinate mode is report-only. It does not edit your resume, ledger, job description, or evidence files.
- Job matching uses deterministic keyword matching, not AI scoring.
- Evidence files are loaded from direct `.md` or `.txt` files in the evidence directory and shown by relative evidence IDs.
- Use `--summary` for a compact summary that lists action counts and non-ready claims only.
- Use `--summary --format json` when an agent needs a compact structured triage payload.
- Use `--strict` to fail when malformed inputs or submission blockers remain after the plan is written.

Coordinate JSON uses a stable schema; see [docs/ledger-schema.md](docs/ledger-schema.md).

## Sample

Input:

```md
- 대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다.
- 배포 체크리스트를 도입했습니다. [evidence: release checklist]
```

Output:

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

For the full ledger, Advice JSON, and Coordinate JSON schema, see [docs/ledger-schema.md](docs/ledger-schema.md).
