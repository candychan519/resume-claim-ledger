from pathlib import Path


def test_readme_mentions_core_commands() -> None:
    # Given: the project README.
    readme = Path("README.md")

    # When: the README content is read.
    content = readme.read_text(encoding="utf-8")

    # Then: the README documents the publishable CLI surface.
    assert "resume-ledger scan" in content
    assert "resume-ledger review" in content
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
