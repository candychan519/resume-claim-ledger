from pathlib import Path


def test_releasing_docs_define_semver_rollback_and_hotfix_flow() -> None:
    # Given: release documentation.
    content = Path("docs/releasing.md").read_text(encoding="utf-8")

    # When: the release policy is inspected.
    required = ["vMAJOR.MINOR.PATCH", "rollback", "hotfix", "artifact-only release"]

    # Then: release operators have a concrete policy.
    for phrase in required:
        assert phrase in content


def test_release_docs_define_artifact_only_flow() -> None:
    # Given: release documentation.
    content = Path("docs/releasing.md").read_text(encoding="utf-8")

    # When: the release workflow is inspected.
    build_index = content.index("uv build")
    artifact_index = content.index("GitHub artifact")
    deferred_index = content.index("Publishing Deferred")

    # Then: release builds artifacts before discussing future publishing.
    assert build_index < artifact_index
    assert artifact_index < deferred_index


def test_release_docs_mark_testpypi_and_pypi_as_deferred() -> None:
    # Given: release documentation.
    content = Path("docs/releasing.md").read_text(encoding="utf-8")

    # When: publishing guidance is inspected.
    # Then: TestPyPI and PyPI setup is documented as a future step, not current release work.
    assert "Publishing Deferred" in content
    assert "TestPyPI and PyPI publishing are intentionally disabled" in content
    assert "project name: `resume-claim-ledger`" in content
    assert "workflow filename: `release.yml`" in content


def test_release_docs_describe_yank_not_replace_policy() -> None:
    # Given: release documentation.
    content = Path("docs/releasing.md").read_text(encoding="utf-8")

    # When: rollback policy is inspected.
    policy = content.casefold()

    # Then: PyPI rollback uses yanking and patch releases, not replacement.
    assert "yank" in policy
    assert "cannot be replaced" in policy
    assert "patch release" in policy
