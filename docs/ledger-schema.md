# Ledger Schema

## Version 1

Generated ledgers use:

```yaml
schema_version: 1
claims:
  - claim_id: CLM-001
    text: "Resume claim text"
    category: execution
    status: needs_evidence
    evidence_note: "Evidence note"
    suggested_rewrite: ""
```

## Fields

- `schema_version`: integer schema marker. Current value is `1`.
- `claims`: list of claim records.
- `claim_id`: stable generated ID such as `CLM-001`.
- `text`: resume claim text.
- `category`: one of `impact`, `execution`, or `scope`.
- `status`: one of `verified`, `needs_evidence`, `too_broad`, or `rewrite_needed`.
- `evidence_note`: evidence summary or missing-evidence explanation.
- `suggested_rewrite`: safer rewrite suggestion when available.

Legacy MVP ledgers without `schema_version` remain readable.

## Advice Output

Suggestions are report-only and are not written back to ledger schema version 1. The
`advise` command reads a ledger and writes Markdown or Advice JSON output.

Advice JSON uses:

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

## Advice JSON Fields

- `schema_version`: integer advice-output schema marker. Current value is `1`.
- `suggestions`: list of report-only suggestion records.
- `claim_id`: source claim ID from the ledger.
- `kind`: one of `career` or `korean_polish`.
- `severity`: one of `info`, `warning`, or `critical`.
- `title`: short user-facing suggestion title.
- `detail`: explanation of the HR or Korean polish issue.
- `suggested_text`: conservative wording suggestion that must preserve known facts.

## Coordinate Output

Coordinate suggestions are report-only and are not written back to ledger schema version 1. The
`coordinate` command reads a ledger, optional job description, and optional evidence directory,
then writes Markdown or Coordinate JSON output.

Coordinate JSON uses:

```json
{
  "schema_version": 1,
  "items": [
    {
      "claim_id": "CLM-001",
      "source_text": "Python MLOps 배포 체크리스트를 정리했습니다.",
      "action": "ready",
      "evidence_status": "verified",
      "requirement_match": "direct_keyword_match",
      "matched_requirements": ["REQ-001"],
      "matched_evidence": ["EVD-001"],
      "next_step": "제출 가능 상태입니다."
    }
  ],
  "warnings": []
}
```

## Coordinate JSON Fields

- `schema_version`: integer coordinate-output schema marker. Current value is `1`.
- `items`: list of coordinate action records.
- `claim_id`: source claim ID from the ledger.
- `source_text`: source claim text copied from the ledger.
- `action`: one of `ready`, `needs_evidence`, `soften_wording`, `jd_gap`, or `submission_blocker`.
- `evidence_status`: source ledger status for the claim.
- `requirement_match`: one of `direct_keyword_match`, `weak_keyword_match`, `no_match`, or `not_evaluated`.
- `matched_requirements`: list of matched job requirement IDs.
- `matched_evidence`: list of matched evidence IDs. Absolute local paths are not exposed.
- `next_step`: conservative next action that must not invent facts.
- `warnings`: malformed input or parse warnings surfaced during coordination.
