# Resume Claim Ledger

Track, verify, and rewrite resume claims with evidence before submission.

## Install

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
resume-ledger report claims.yml --out claim-review.md
resume-ledger report claims.yml --out claim-review.md --strict
```

## Why This Exists

AI-assisted resume writing can quietly inflate scope, impact, and metrics. Resume Claim Ledger keeps a local evidence ledger so each resume bullet can be reviewed before submission.

## Sample

Input:

```md
- 대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다.
- 배포 체크리스트를 도입했습니다. [evidence: release checklist]
```

Output:

```yaml
claims:
  - claim_id: CLM-001
    status: too_broad
    evidence_note: 범위나 판단 기준을 뒷받침할 근거가 필요합니다.
  - claim_id: CLM-002
    status: verified
    evidence_note: release checklist
```
