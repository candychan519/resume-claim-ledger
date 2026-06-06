from pathlib import Path


def test_readme_mentions_core_commands() -> None:
    # Given: the project README.
    readme = Path("README.md")

    # When: the README content is read.
    content = readme.read_text(encoding="utf-8")

    # Then: the README documents the publishable CLI surface.
    assert "resume-ledger scan" in content
    assert "resume-ledger review" in content
    assert "resume-ledger doctor" in content
    assert "resume-ledger report" in content


def test_readme_documents_release_install_paths() -> None:
    # Given: the project README.
    readme = Path("README.md")

    # When: the README content is read.
    content = readme.read_text(encoding="utf-8")

    # Then: it documents install paths for source and PyPI distribution.
    assert "uv tool install git+https://github.com/candychan519/resume-claim-ledger" in content
    assert "uv tool install resume-claim-ledger" in content
    assert "uv run pytest -q" in content


def test_readme_documents_advise_command() -> None:
    # Given: the project README.
    readme = Path("README.md")

    # When: the README content is read.
    content = readme.read_text(encoding="utf-8")

    # Then: it documents the career advice command and output formats.
    assert "resume-ledger advise" in content
    assert "--polish-ko" in content
    assert "--format json" in content


def test_readme_describes_report_only_advice_not_source_rewriting() -> None:
    # Given: the project README.
    content = Path("README.md").read_text(encoding="utf-8")

    # When: the product promise is inspected.
    # Then: it avoids implying that the tool rewrites source resumes automatically.
    assert "rewrite resume claims" not in content
    assert "suggest safer wording" in content
    assert "report-only" in content


def test_readme_sample_matches_versioned_ledger_schema() -> None:
    # Given: the project README.
    content = Path("README.md").read_text(encoding="utf-8")

    # When: the sample ledger output is inspected.
    # Then: it shows the current versioned ledger fields.
    assert "schema_version: 1" in content
    assert "category: impact" in content
    assert "suggested_rewrite:" in content


def test_readme_documents_python_and_uv_prerequisites() -> None:
    # Given: the project README.
    content = Path("README.md").read_text(encoding="utf-8")

    # When: the install section is inspected.
    # Then: first-time users can see the runtime and tool prerequisites.
    assert "Python 3.13" in content
    assert "uv" in content


def test_readme_links_schema_and_release_docs() -> None:
    # Given: the project README.
    content = Path("README.md").read_text(encoding="utf-8")

    # When: public documentation links are inspected.
    # Then: users can find schema and publishing details without duplicated policy text.
    assert "docs/ledger-schema.md" in content
    assert "docs/releasing.md" in content


def test_readme_documents_strict_and_malformed_ledger_behavior() -> None:
    # Given: the project README.
    content = Path("README.md").read_text(encoding="utf-8")

    # When: submission-gate and invalid-ledger guidance is inspected.
    # Then: users can anticipate strict failures and malformed-ledger warnings.
    assert "--strict" in content
    assert "submission gate" in content
    assert "Malformed ledger" in content


def test_readme_documents_advice_json_schema_or_schema_doc_link() -> None:
    # Given: the project README.
    content = Path("README.md").read_text(encoding="utf-8")

    # When: JSON advice output guidance is inspected.
    # Then: users can find the stable Advice JSON contract.
    assert "--format json" in content
    assert "Advice JSON" in content
    assert "docs/ledger-schema.md" in content


def test_readme_documents_coordinate_command() -> None:
    # Given: the project README.
    content = Path("README.md").read_text(encoding="utf-8")

    # When: coordinate usage guidance is inspected.
    # Then: users can find Markdown, JSON, and strict coordinate examples.
    markdown_command = (
        "resume-ledger coordinate claims.yml --job jd.md --evidence-dir evidence "
        "--out submission-plan.md"
    )
    assert markdown_command in content
    assert "resume-ledger coordinate claims.yml --format json --out submission-plan.json" in content
    assert "resume-ledger coordinate claims.yml --strict --out submission-plan.md" in content


def test_readme_describes_coordinate_as_report_only_and_deterministic() -> None:
    # Given: the project README.
    content = Path("README.md").read_text(encoding="utf-8")

    # When: the coordinate product promise is inspected.
    # Then: it avoids implying automatic rewriting or AI scoring.
    assert "Coordinate mode is report-only" in content
    assert "does not edit your resume, ledger, job description, or evidence files" in content
    assert "deterministic keyword matching" in content
    assert "not AI scoring" in content


def test_readme_documents_coordinate_summary_mode() -> None:
    # Given: the project README.
    content = Path("README.md").read_text(encoding="utf-8")

    # When: coordinate summary guidance is inspected.
    # Then: users can find the compact triage output command and purpose.
    assert "resume-ledger coordinate claims.yml --summary --out submission-summary.md" in content
    assert "compact summary" in content
    assert "non-ready claims" in content


def test_maintenance_docs_describe_coordinate_summary_as_report_only() -> None:
    # Given: maintenance documentation.
    content = Path("docs/maintenance.md").read_text(encoding="utf-8")

    # When: coordinate maintenance rules are inspected.
    # Then: summary mode is held to the same report-only contract.
    assert "summary mode" in content
    assert "non-ready claims" in content
    assert "report-only" in content
