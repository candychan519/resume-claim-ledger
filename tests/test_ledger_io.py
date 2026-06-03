from pathlib import Path

from resume_claim_ledger.ledger_io import read_ledger, write_ledger
from resume_claim_ledger.models import Claim


def joined_lines(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def test_read_ledger_when_generated_file_round_trips_claims(tmp_path: Path) -> None:
    # Given: generated claim records.
    ledger = tmp_path / "claims.yml"
    claims = [
        Claim(
            claim_id="CLM-001",
            text="배포 체크리스트를 도입했습니다.",
            category="execution",
            status="verified",
            evidence_note="release checklist",
            suggested_rewrite="",
        ),
    ]

    # When: claims are written and read again.
    write_ledger(ledger, claims)
    result = read_ledger(ledger)

    # Then: claim data survives the ledger boundary.
    assert result == claims


def test_write_ledger_includes_schema_version(tmp_path: Path) -> None:
    # Given: an empty generated ledger.
    ledger = tmp_path / "claims.yml"

    # When: it is written.
    write_ledger(ledger, [])

    # Then: the public ledger schema is versioned.
    assert "schema_version: 1" in ledger.read_text(encoding="utf-8")


def test_read_ledger_accepts_legacy_claims_without_schema_version(tmp_path: Path) -> None:
    # Given: a legacy MVP ledger without schema_version.
    ledger = tmp_path / "legacy.yml"
    _ = ledger.write_text(
        joined_lines(
            [
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "장애 대응 문서를 정리했습니다."',
                "    category: execution",
                "    status: needs_evidence",
                '    evidence_note: "구체적인 근거가 필요합니다."',
                '    suggested_rewrite: ""',
            ],
        ),
        encoding="utf-8",
    )

    # When: it is read.
    claims = read_ledger(ledger)

    # Then: existing ledgers remain readable.
    assert claims[0].claim_id == "CLM-001"
    assert claims[0].status == "needs_evidence"


def test_read_ledger_when_top_level_shape_is_invalid_returns_empty_list(tmp_path: Path) -> None:
    # Given: a malformed ledger.
    ledger = tmp_path / "malformed.yml"
    _ = ledger.write_text("not_claims:\n  - broken\n", encoding="utf-8")

    # When: it is read.
    claims = read_ledger(ledger)

    # Then: malformed input does not crash callers.
    assert claims == []
