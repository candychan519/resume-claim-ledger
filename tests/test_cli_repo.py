import subprocess
from pathlib import Path
from shutil import which

UV = which("uv") or "uv"
EXPECTED_PACK_FILES = (
    "agent-brief.md",
    "claim-candidates.yml",
    "evidence-catalog.json",
    "evidence-gaps.md",
    "knowledge-graph.json",
    "repo-profile.json",
    "repo-profile.md",
)
GIT_REQUIRED_MESSAGE = "git executable is required for CLI repo tests"


def test_repo_intake_writes_knowledge_pack_for_local_repo(tmp_path: Path) -> None:
    # Given: a local Git repository with repository evidence signals.
    source = _init_repo(tmp_path / "source")
    _write(source / "README.md", "# Demo Repo\n\nPython CLI for deployment checks.\n")
    _write(source / "pyproject.toml", '[project]\nname = "demo"\n')
    _write(source / ".github/workflows/ci.yml", "name: CI\n")
    _write(source / "tests/test_cli.py", "def test_cli() -> None:\n    assert True\n")
    _commit_all(source, "init")
    out = tmp_path / "knowledge" / "demo"

    # When: repo intake runs through the installed CLI.
    result = run_cli(["repo", "intake", str(source), "--out", str(out), "--name", "demo"])

    # Then: it writes the full knowledge pack and prints file names only.
    assert result.returncode == 0
    assert "Wrote repository knowledge pack." in result.stdout
    assert _pack_files(out) == EXPECTED_PACK_FILES
    assert "repo-profile.md" in result.stdout
    assert "# Repository Profile" in (out / "repo-profile.md").read_text(encoding="utf-8")


def test_repo_intake_writes_knowledge_pack_for_file_url_remote_repo(tmp_path: Path) -> None:
    # Given: a local bare remote exposed through a file URL.
    remote, work = _init_file_remote(tmp_path)
    _write(work / "README.md", "# Remote Demo\n")
    _commit_all(work, "remote main")
    _run_git(("push", "origin", "HEAD:master"), work)
    out = tmp_path / "out" / "remote-demo"

    # When: repo intake clones the file URL.
    result = run_cli(
        ["repo", "intake", remote.as_uri(), "--out", str(out), "--name", "remote-demo"],
    )

    # Then: it succeeds without an interactive prompt and writes the profile.
    assert result.returncode == 0
    assert _pack_files(out) == EXPECTED_PACK_FILES
    assert "Remote Demo" in (out / "repo-profile.md").read_text(encoding="utf-8")


def test_repo_intake_with_ref_analyzes_requested_ref(tmp_path: Path) -> None:
    # Given: a remote with different README content on a feature ref.
    remote, work = _init_file_remote(tmp_path)
    _write(work / "README.md", "# Main\n")
    _commit_all(work, "main")
    _run_git(("push", "origin", "HEAD:master"), work)
    _run_git(("checkout", "-b", "feature"), work)
    _write(work / "README.md", "# Feature\n")
    _commit_all(work, "feature")
    _run_git(("push", "origin", "HEAD:feature"), work)
    out = tmp_path / "out" / "feature"

    # When: repo intake is pinned to the feature ref.
    result = run_cli(
        [
            "repo",
            "intake",
            remote.as_uri(),
            "--ref",
            "feature",
            "--out",
            str(out),
            "--name",
            "demo",
        ],
    )

    # Then: generated output reflects the requested ref.
    assert result.returncode == 0
    assert "Feature" in (out / "repo-profile.md").read_text(encoding="utf-8")
    assert "Main" not in (out / "repo-profile.md").read_text(encoding="utf-8")


def test_repo_intake_when_source_is_not_git_exits_nonzero(tmp_path: Path) -> None:
    # Given: a plain directory.
    plain = tmp_path / "plain"
    plain.mkdir()

    # When: repo intake receives it as a source.
    result = run_cli(["repo", "intake", str(plain), "--out", str(tmp_path / "out")])

    # Then: it fails with a controlled message.
    assert result.returncode != 0
    assert "not a Git repository" in result.stderr


def test_repo_intake_does_not_leak_absolute_paths_to_outputs_or_streams(tmp_path: Path) -> None:
    # Given: a local repository under a temporary absolute path.
    source = _init_repo(tmp_path / "source")
    _write(source / "README.md", "# Path Demo\n")
    _commit_all(source, "init")
    out = tmp_path / "out" / "path-demo"

    # When: repo intake writes the knowledge pack.
    result = run_cli(["repo", "intake", str(source), "--out", str(out), "--name", "path-demo"])

    # Then: command streams and generated outputs avoid the local path.
    generated = _generated_text(out)
    assert result.returncode == 0
    assert str(tmp_path) not in result.stdout
    assert str(tmp_path) not in result.stderr
    assert str(tmp_path) not in generated


def test_repo_intake_redacts_secret_like_files_from_outputs(tmp_path: Path) -> None:
    # Given: a repository with a tracked secret-like file.
    source = _init_repo(tmp_path / "source")
    _write(source / "README.md", "# Secret Demo\n")
    _write(source / ".env", "TOKEN=super-secret-value\n")
    _commit_all(source, "init")
    out = tmp_path / "out" / "secret-demo"

    # When: repo intake writes the knowledge pack.
    result = run_cli(["repo", "intake", str(source), "--out", str(out), "--name", "secret-demo"])

    # Then: the path is recorded but the secret body is absent.
    generated = _generated_text(out)
    assert result.returncode == 0
    assert ".env" in generated
    assert "super-secret-value" not in generated


def test_repo_intake_when_max_files_exceeded_exits_nonzero(tmp_path: Path) -> None:
    # Given: a repository larger than the requested max-files limit.
    source = _init_repo(tmp_path / "source")
    _write(source / "README.md", "# Demo\n")
    _write(source / "docs/usage.md", "# Usage\n")
    _commit_all(source, "init")

    # When: repo intake runs with a too-small limit.
    result = run_cli(
        ["repo", "intake", str(source), "--out", str(tmp_path / "out"), "--max-files", "1"],
    )

    # Then: it exits non-zero with a controlled limit error.
    assert result.returncode != 0
    assert "exceeds --max-files" in result.stderr


def test_repo_intake_when_remote_is_inaccessible_exits_nonzero_without_prompting(
    tmp_path: Path,
) -> None:
    # Given: an inaccessible file URL remote.
    missing_remote = (tmp_path / "missing.git").as_uri()

    # When: repo intake tries to clone it.
    result = run_cli(["repo", "intake", missing_remote, "--out", str(tmp_path / "out")])

    # Then: it fails without prompting or leaking the remote path.
    assert result.returncode != 0
    assert "Git clone failed" in result.stderr
    assert str(tmp_path) not in result.stderr


def test_repo_intake_refuses_non_empty_output_directory(tmp_path: Path) -> None:
    # Given: a valid source repo and a non-empty output directory.
    source = _init_repo(tmp_path / "source")
    _write(source / "README.md", "# Demo\n")
    _commit_all(source, "init")
    out = tmp_path / "out"
    out.mkdir()
    _write(out / "existing.txt", "do not overwrite\n")

    # When: repo intake targets the non-empty directory.
    result = run_cli(["repo", "intake", str(source), "--out", str(out)])

    # Then: it refuses to overwrite existing user output.
    assert result.returncode != 0
    assert "Output directory is not empty" in result.stderr
    assert (out / "existing.txt").read_text(encoding="utf-8") == "do not overwrite\n"


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [UV, "run", "--quiet", "resume-ledger", *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _init_repo(path: Path) -> Path:
    _ = path.mkdir(parents=True)
    _run_git(("init",), path)
    return path


def _init_file_remote(tmp_path: Path) -> tuple[Path, Path]:
    remote = tmp_path / "remote.git"
    work = tmp_path / "work"
    _run_git(("init", "--bare", str(remote)), tmp_path)
    _ = _init_repo(work)
    _run_git(("remote", "add", "origin", str(remote)), work)
    return remote, work


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
    git = which("git")
    if git is None:
        raise AssertionError(GIT_REQUIRED_MESSAGE)
    _ = subprocess.run(
        [git, *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _pack_files(out: Path) -> tuple[str, ...]:
    return tuple(sorted(path.name for path in out.iterdir() if path.is_file()))


def _generated_text(out: Path) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in sorted(out.iterdir()))
