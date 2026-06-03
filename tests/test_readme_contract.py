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
