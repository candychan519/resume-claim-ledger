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
