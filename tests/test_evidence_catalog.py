from pathlib import Path

import pytest

from resume_claim_ledger.evidence_catalog import load_evidence_catalog


def test_load_evidence_catalog_uses_relative_display_names_and_heading_summary(
    tmp_path: Path,
) -> None:
    # Given: an evidence directory with markdown and text evidence files.
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    _ = (evidence_dir / "release.md").write_text(
        "# Release Checklist\nEvidence details\n",
        encoding="utf-8",
    )
    _ = (evidence_dir / "incident.txt").write_text(
        "Incident response note\nPrivate details\n",
        encoding="utf-8",
    )

    # When: the evidence catalog is loaded.
    items = load_evidence_catalog(evidence_dir)

    # Then: stable IDs, relative display names, and summaries are exposed.
    assert [(item.evidence_id, item.display_name, item.summary) for item in items] == [
        ("EVD-001", "incident.txt", "Incident response note"),
        ("EVD-002", "release.md", "Release Checklist"),
    ]
    assert str(tmp_path) not in items[0].display_name
    assert str(tmp_path) not in items[1].display_name


def test_load_evidence_catalog_when_directory_is_empty_returns_empty_list(
    tmp_path: Path,
) -> None:
    # Given: an empty evidence directory.
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()

    # When: the evidence catalog is loaded.
    items = load_evidence_catalog(evidence_dir)

    # Then: no synthetic evidence is invented.
    assert items == []


def test_load_evidence_catalog_when_directory_is_missing_raises_file_not_found(
    tmp_path: Path,
) -> None:
    # Given: a missing evidence directory path.
    missing = tmp_path / "missing-evidence"

    # When / Then: loading fails at the boundary.
    with pytest.raises(FileNotFoundError):
        _ = load_evidence_catalog(missing)


def test_load_evidence_catalog_prefers_markdown_heading_over_leading_body(
    tmp_path: Path,
) -> None:
    # Given: evidence content with body text before its first heading.
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    _ = (evidence_dir / "notes.md").write_text(
        "Internal note\n# Public Summary\nEvidence details\n",
        encoding="utf-8",
    )

    # When: the evidence catalog is loaded.
    items = load_evidence_catalog(evidence_dir)

    # Then: the first Markdown heading is used before falling back to body text.
    assert items[0].summary == "Public Summary"
