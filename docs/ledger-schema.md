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
