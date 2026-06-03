from pathlib import Path


def test_pyproject_contains_publishable_metadata() -> None:
    # Given: the project metadata file.
    pyproject = Path("pyproject.toml")

    # When: metadata is read.
    content = pyproject.read_text(encoding="utf-8")

    # Then: required PyPI-facing metadata is present.
    assert 'license = "MIT"' in content
    assert '{ name = "candychan519" }' in content
    assert '"resume"' in content
    assert '"Development Status :: 3 - Alpha"' in content
    assert 'Repository = "https://github.com/candychan519/resume-claim-ledger"' in content
