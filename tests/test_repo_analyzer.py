import subprocess
from pathlib import Path
from shutil import which

import pytest

from resume_claim_ledger.repo_analyzer import RepoAnalysisError, analyze_repository
from resume_claim_ledger.repo_models import repo_knowledge_pack_to_dict

EXPECTED_RECENT_COMMITS = 2


def test_analyze_repo_detects_readme_package_ci_tests_and_claim_candidates(
    tmp_path: Path,
) -> None:
    # Given: a tracked repository with docs, manifest, CI, tests, and source files.
    repo = _init_repo(tmp_path)
    _write(repo / "README.md", "# Demo Repo\n\nPython CLI for deployment checks.\n")
    _write(repo / "pyproject.toml", '[project]\nname = "demo"\n')
    _write(repo / ".github/workflows/ci.yml", "name: CI\n")
    _write(repo / "tests/test_cli.py", "def test_cli() -> None:\n    assert True\n")
    _write(repo / "src/demo/cli.py", "def main() -> None:\n    pass\n")
    _write(repo / "docs/usage.md", "# Usage\n\nRun the CLI.\n")
    _commit_all(repo, "initial evidence")

    # When: the static analyzer builds a knowledge pack.
    pack = analyze_repository(
        repo,
        name="demo",
        source_label="github.com/acme/demo",
        remote="github.com/acme/demo",
        max_commits=5,
    )

    # Then: repo signals and report-only claim candidates are stable.
    assert pack.profile.name == "demo"
    assert pack.profile.source == "github.com/acme/demo"
    assert "Python" in pack.profile.languages
    assert pack.profile.package_manifests == ("pyproject.toml",)
    assert pack.profile.ci_workflows == (".github/workflows/ci.yml",)
    assert pack.profile.test_files == ("tests/test_cli.py",)
    assert "README.md" in pack.profile.documentation_files
    evidence_kinds = tuple(item.kind for item in pack.evidence_items)
    assert "readme" in evidence_kinds
    assert "manifest" in evidence_kinds
    assert "ci_workflow" in evidence_kinds
    assert "test" in evidence_kinds
    assert pack.claim_candidates != ()
    first_candidate = pack.claim_candidates[0]
    assert first_candidate.confidence in ("low", "medium", "high")
    assert first_candidate.supporting_files != ()
    assert "Confirm personal contribution" in first_candidate.missing_confirmation


def test_analyze_repo_redacts_sensitive_files_without_reading_contents(tmp_path: Path) -> None:
    # Given: a tracked repository with a secret-like file.
    repo = _init_repo(tmp_path)
    _write(repo / "README.md", "# Secret Demo\n")
    _write(repo / ".env", "TOKEN=super-secret-value\n")
    _commit_all(repo, "add sensitive fixture")

    # When: the analyzer inspects the repository.
    pack = analyze_repository(repo, name="secret-demo", source_label="local")
    payload_text = str(repo_knowledge_pack_to_dict(pack))

    # Then: it records sensitive presence but never copies the file body.
    assert "super-secret-value" not in payload_text
    sensitive_items = tuple(item for item in pack.evidence_items if item.kind == "sensitive_file")
    assert len(sensitive_items) == 1
    assert sensitive_items[0].path == ".env"
    assert "contents were not read" in sensitive_items[0].summary


def test_analyze_repo_does_not_emit_absolute_paths(tmp_path: Path) -> None:
    # Given: a local repository under a temporary absolute path.
    repo = _init_repo(tmp_path)
    _write(repo / "README.md", "# Demo\n")
    _commit_all(repo, "init")

    # When: the analyzer serializes repository facts.
    pack = analyze_repository(repo, name="demo", source_label="local")
    payload_text = str(repo_knowledge_pack_to_dict(pack))

    # Then: output metadata uses relative paths only.
    assert str(tmp_path) not in payload_text
    assert "README.md" in payload_text


def test_analyze_empty_repo_returns_evidence_gap_not_crash(tmp_path: Path) -> None:
    # Given: an empty Git repository.
    repo = _init_repo(tmp_path)

    # When: the analyzer runs on it.
    pack = analyze_repository(repo, name="empty", source_label="local")

    # Then: it returns an evidence gap instead of failing.
    assert pack.evidence_items == ()
    assert pack.evidence_gaps != ()
    assert "No tracked repository files" in pack.evidence_gaps[0].text


def test_analyze_repo_respects_max_files_with_controlled_limit_error(tmp_path: Path) -> None:
    # Given: a repository with more tracked files than the configured limit.
    repo = _init_repo(tmp_path)
    _write(repo / "README.md", "# Demo\n")
    _write(repo / "docs/usage.md", "# Usage\n")
    _commit_all(repo, "two files")

    # When/Then: analysis fails with a controlled message and no absolute path.
    with pytest.raises(RepoAnalysisError, match="exceeds --max-files") as error:
        _ = analyze_repository(repo, name="demo", source_label="local", max_files=1)
    assert str(tmp_path) not in str(error.value)


def test_analyze_repo_skips_large_file_body_and_records_gap(tmp_path: Path) -> None:
    # Given: a repository with a tracked text file larger than the read limit.
    repo = _init_repo(tmp_path)
    _write(repo / "README.md", "# Demo\n")
    _write(repo / "docs/large.md", "private-large-body\n" * 20)
    _commit_all(repo, "large file")

    # When: the analyzer runs with a small byte limit.
    pack = analyze_repository(repo, name="demo", source_label="local", max_file_bytes=10)
    payload_text = str(repo_knowledge_pack_to_dict(pack))

    # Then: the large file body is omitted and a gap names only the relative path.
    assert "private-large-body" not in payload_text
    assert any(gap.related_files == ("docs/large.md",) for gap in pack.evidence_gaps)


def test_analyze_repo_limits_recent_commit_facts_to_configured_count(tmp_path: Path) -> None:
    # Given: a repository with more commits than the configured recent-log limit.
    repo = _init_repo(tmp_path)
    _write(repo / "README.md", "# Demo\n")
    _commit_all(repo, "first")
    _write(repo / "README.md", "# Demo\n\nSecond\n")
    _commit_all(repo, "second")
    _write(repo / "README.md", "# Demo\n\nThird\n")
    _commit_all(repo, "third")

    # When: analysis limits recent commit evidence to two entries.
    pack = analyze_repository(repo, name="demo", source_label="local", max_commits=2)

    # Then: only the two most recent commit subjects are retained.
    commit_summaries = tuple(
        item.summary for item in pack.evidence_items if item.kind == "commit"
    )
    assert len(commit_summaries) == EXPECTED_RECENT_COMMITS
    assert "third" in commit_summaries[0]
    assert "second" in commit_summaries[1]
    assert "first" not in " ".join(commit_summaries)


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(("init",), repo)
    return repo


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(content, encoding="utf-8")


def _commit_all(repo: Path, message: str) -> None:
    _run_git(("add", "."), repo)
    _run_git(
        ("-c", "user.email=qa@example.com", "-c", "user.name=QA", "commit", "-m", message),
        repo,
    )


def _run_git(args: tuple[str, ...], cwd: Path) -> None:
    git = _git_path()
    _ = subprocess.run(
        [git, *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _git_path() -> str:
    git = which("git")
    if git is None:
        pytest.fail("git executable is required for repo analyzer tests")
    return git
