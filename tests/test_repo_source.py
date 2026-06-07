import subprocess
from collections.abc import Callable
from pathlib import Path
from shutil import which

import pytest

from resume_claim_ledger.repo_source import (
    NO_RECURSE_SUBMODULES,
    GitCommand,
    GitCommandResult,
    RepoSourceError,
    resolve_repository_source,
    sanitize_remote_url,
)

RecordingRunner = tuple[list[GitCommand], Callable[[GitCommand], GitCommandResult]]
RECURSE_SUBMODULES = "--" + "recurse-submodules"


def test_resolve_local_repo_returns_root_without_mutating_source(tmp_path: Path) -> None:
    # Given: an existing local Git worktree with an untracked source file.
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(("init",), repo)
    readme = repo / "README.md"
    _ = readme.write_text("# Demo\n", encoding="utf-8")
    before = _git_status(repo)

    # When: the source resolver inspects the worktree.
    resolved = resolve_repository_source(str(repo))

    # Then: it returns the root and does not mutate tracked or untracked state.
    assert resolved.root == repo.resolve()
    assert resolved.source_label == "local"
    assert resolved.cleanup_dir is None
    assert _git_status(repo) == before
    assert readme.read_text(encoding="utf-8") == "# Demo\n"


def test_resolve_non_git_directory_raises_user_safe_error(tmp_path: Path) -> None:
    # Given: an existing directory that is not a Git worktree.
    plain_dir = tmp_path / "plain"
    plain_dir.mkdir()

    # When/Then: resolution fails without leaking the absolute input path.
    with pytest.raises(RepoSourceError, match="not a Git repository") as error:
        _ = resolve_repository_source(str(plain_dir))
    assert str(tmp_path) not in str(error.value)


def test_clone_url_uses_promptless_lfs_safe_git_command(tmp_path: Path) -> None:
    # Given: a remote URL and a recording command runner.
    commands, runner = _new_recording_runner()

    # When: the resolver clones into a caller-provided workspace.
    resolved = resolve_repository_source(
        "https://github.com/acme/demo.git",
        workspace=tmp_path,
        runner=runner,
    )

    # Then: clone is shallow, promptless, LFS-smudge-safe, and path metadata is sanitized.
    assert resolved.root == tmp_path / "demo"
    assert resolved.source_label == "github.com/acme/demo"
    assert commands[0].args == (
        "git",
        "clone",
        "--depth",
        "1",
        "--no-tags",
        NO_RECURSE_SUBMODULES,
        "https://github.com/acme/demo.git",
        str(tmp_path / "demo"),
    )
    clone_env = commands[0].env
    assert clone_env is not None
    assert clone_env["GIT_TERMINAL_PROMPT"] == "0"
    assert clone_env["GIT_LFS_SKIP_SMUDGE"] == "1"


def test_clone_url_with_ref_uses_fetch_and_detached_checkout(tmp_path: Path) -> None:
    # Given: a remote URL, ref, and recording runner.
    commands, runner = _new_recording_runner()

    # When: the resolver is asked for a specific ref.
    resolved = resolve_repository_source(
        "https://github.com/acme/demo.git",
        ref="feature/evidence",
        workspace=tmp_path,
        runner=runner,
    )

    # Then: it fetches only that ref and checks out FETCH_HEAD detached.
    assert resolved.ref == "feature/evidence"
    assert commands[1].args == (
        "git",
        "-C",
        str(tmp_path / "demo"),
        "fetch",
        "--depth",
        "1",
        "origin",
        "feature/evidence",
    )
    assert commands[2].args == (
        "git",
        "-C",
        str(tmp_path / "demo"),
        "checkout",
        "--detach",
        "FETCH_HEAD",
    )


def test_remote_url_with_credentials_is_sanitized_in_metadata() -> None:
    # Given: a credential-bearing URL.
    remote = "https://token:secret@github.com/acme/private-demo.git"

    # When: it is converted for metadata.
    sanitized = sanitize_remote_url(remote)

    # Then: credentials are removed and only host/owner/repo remain.
    assert sanitized == "github.com/acme/private-demo"
    assert "token" not in sanitized
    assert "secret" not in sanitized


def test_clone_command_never_enables_submodule_recursion(tmp_path: Path) -> None:
    # Given: a recording runner for remote intake.
    commands, runner = _new_recording_runner()

    # When: clone command arguments are prepared.
    _ = resolve_repository_source(
        "https://github.com/acme/demo.git",
        workspace=tmp_path,
        runner=runner,
    )

    # Then: submodule recursion is explicitly disabled.
    clone_args = commands[0].args
    assert NO_RECURSE_SUBMODULES in clone_args
    assert RECURSE_SUBMODULES not in clone_args


def _new_recording_runner() -> RecordingRunner:
    commands: list[GitCommand] = []

    def record(command: GitCommand) -> GitCommandResult:
        commands.append(command)
        return GitCommandResult(stdout="", stderr="")

    return commands, record


def _run_git(args: tuple[str, ...], cwd: Path) -> None:
    git = _git_path()
    _ = subprocess.run(
        [git, *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )


def _git_status(repo: Path) -> str:
    git = _git_path()
    completed = subprocess.run(
        [git, "status", "--short"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _git_path() -> str:
    git = which("git")
    if git is None:
        pytest.fail("git executable is required for repo source tests")
    return git
