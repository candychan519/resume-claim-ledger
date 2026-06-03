from pathlib import Path


def test_ledger_schema_docs_define_versioned_fields() -> None:
    # Given: ledger schema documentation.
    content = Path("docs/ledger-schema.md").read_text(encoding="utf-8")

    # When: required schema fields are inspected.
    required = [
        "schema_version",
        "claims",
        "claim_id",
        "status",
        "evidence_note",
        "suggested_rewrite",
    ]

    # Then: every generated ledger field is documented.
    for field in required:
        assert field in content
