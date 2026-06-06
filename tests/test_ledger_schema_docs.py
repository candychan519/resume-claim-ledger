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


def test_ledger_schema_notes_suggestions_are_report_only() -> None:
    # Given: ledger schema documentation.
    content = Path("docs/ledger-schema.md").read_text(encoding="utf-8")

    # When: suggestion storage policy is inspected.
    # Then: suggestions are explicitly kept outside the ledger schema.
    assert "Suggestions are report-only" in content
    assert "not written back to ledger schema version 1" in content


def test_docs_define_advice_json_contract() -> None:
    # Given: ledger schema documentation.
    content = Path("docs/ledger-schema.md").read_text(encoding="utf-8")

    # When: advice JSON contract documentation is inspected.
    # Then: every public advice JSON field is documented.
    required = [
        "Advice JSON",
        "suggestions",
        "kind",
        "severity",
        "title",
        "detail",
        "suggested_text",
    ]
    for field in required:
        assert field in content


def test_docs_define_coordinate_json_contract() -> None:
    # Given: ledger schema documentation.
    content = Path("docs/ledger-schema.md").read_text(encoding="utf-8")

    # When: coordinate JSON contract documentation is inspected.
    # Then: every public coordinate field is documented.
    required = [
        "Coordinate JSON",
        "items",
        "source_text",
        "action",
        "evidence_status",
        "requirement_match",
        "matched_requirements",
        "matched_evidence",
        "next_step",
        "warnings",
    ]
    for field in required:
        assert field in content
