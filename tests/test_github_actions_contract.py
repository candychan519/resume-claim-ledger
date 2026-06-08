from pathlib import Path


def test_ci_workflow_runs_required_gates() -> None:
    # Given: the CI workflow.
    content = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    # When: required quality gates are inspected.
    required = [
        "uv sync --dev",
        "uv run pytest -q",
        "uv run ruff check .",
        "uv run basedpyright",
        "uv build",
    ]

    # Then: CI runs every local release gate.
    for command in required:
        assert command in content


def test_ci_workflow_uses_python_313_matrix() -> None:
    # Given: the CI workflow.
    content = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

    # When: the Python matrix is inspected.
    # Then: the only advertised runtime is Python 3.13.
    assert 'python-version: ["3.13"]' in content


def test_release_workflow_builds_artifacts_without_publishing() -> None:
    # Given: the release workflow.
    content = Path(".github/workflows/release.yml").read_text(encoding="utf-8")

    # When: release behavior is inspected.
    # Then: release builds and uploads artifacts without publishing to package indexes.
    assert "uv build" in content
    assert "actions/upload-artifact@v7.0.1" in content
    assert "publish-testpypi" not in content
    assert "publish-pypi" not in content
    assert "pypa/gh-action-pypi-publish@release/v1" not in content
    assert "repository-url: https://test.pypi.org/legacy/" not in content
    assert "id-token: write" not in content
    assert "PYPI_TOKEN" not in content


def test_release_workflow_has_release_concurrency_control() -> None:
    # Given: the release workflow.
    content = Path(".github/workflows/release.yml").read_text(encoding="utf-8")

    # When: release concurrency is inspected.
    # Then: duplicate tag workflows are serialized, not canceled mid-publish.
    assert "group: release-${{ github.ref }}" in content
    assert "cancel-in-progress: false" in content


def test_release_workflow_documents_publish_deferral() -> None:
    # Given: the release workflow.
    content = Path(".github/workflows/release.yml").read_text(encoding="utf-8")

    # When: release jobs are inspected.
    # Then: package-index publishing is intentionally absent for the current project stage.
    assert "Publishing to TestPyPI/PyPI is intentionally deferred." in content
    assert "environment: testpypi" not in content
    assert "environment: pypi" not in content


def test_workflows_use_minimal_permissions() -> None:
    # Given: CI and release workflows.
    ci = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    release = Path(".github/workflows/release.yml").read_text(encoding="utf-8")

    # When: workflow permissions are inspected.
    # Then: CI and release stay read-only while publishing is deferred.
    assert "permissions:\n  contents: read" in ci
    assert "permissions:\n  contents: read" in release
    assert "id-token: write" not in release


def test_workflows_opt_into_node24_actions_runtime() -> None:
    # Given: workflows that use JavaScript actions.
    workflow_paths = [
        Path(".github/workflows/ci.yml"),
        Path(".github/workflows/release.yml"),
        Path(".github/workflows/security.yml"),
    ]

    # When: their environment is inspected.
    # Then: they opt into Node 24 before GitHub's runner default changes.
    for workflow_path in workflow_paths:
        assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in workflow_path.read_text(
            encoding="utf-8",
        )


def test_workflows_use_node24_ready_action_versions() -> None:
    # Given: workflows that use JavaScript actions.
    workflow_text = "\n".join(
        [
            Path(".github/workflows/ci.yml").read_text(encoding="utf-8"),
            Path(".github/workflows/release.yml").read_text(encoding="utf-8"),
            Path(".github/workflows/security.yml").read_text(encoding="utf-8"),
        ],
    )

    # When: action versions are inspected.
    # Then: workflows use current Node 24-ready major versions.
    assert "actions/checkout@v6" in workflow_text
    assert "actions/setup-python@v6" in workflow_text
    assert "actions/upload-artifact@v7.0.1" in workflow_text
    assert "astral-sh/setup-uv@v8.2.0" in workflow_text
