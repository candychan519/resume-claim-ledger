from pathlib import Path


def test_releasing_docs_define_semver_rollback_and_hotfix_flow() -> None:
    # Given: release documentation.
    content = Path("docs/releasing.md").read_text(encoding="utf-8")

    # When: the release policy is inspected.
    required = ["vMAJOR.MINOR.PATCH", "rollback", "hotfix", "TestPyPI", "PyPI"]

    # Then: release operators have a concrete policy.
    for phrase in required:
        assert phrase in content


def test_release_docs_define_testpypi_first_flow() -> None:
    # Given: release documentation.
    content = Path("docs/releasing.md").read_text(encoding="utf-8")

    # When: the publishing order is inspected.
    testpypi_index = content.index("TestPyPI")
    pypi_index = content.index("production PyPI")

    # Then: TestPyPI is documented before production PyPI.
    assert testpypi_index < pypi_index


def test_release_docs_describe_yank_not_replace_policy() -> None:
    # Given: release documentation.
    content = Path("docs/releasing.md").read_text(encoding="utf-8")

    # When: rollback policy is inspected.
    policy = content.casefold()

    # Then: PyPI rollback uses yanking and patch releases, not replacement.
    assert "yank" in policy
    assert "cannot be replaced" in policy
    assert "patch release" in policy
