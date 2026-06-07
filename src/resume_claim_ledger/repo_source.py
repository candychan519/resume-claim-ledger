import os
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

MISSING_SOURCE_MESSAGE = "Repository source does not exist."
NOT_GIT_REPOSITORY_MESSAGE = "Source is not a Git repository."
CLONE_WORKSPACE_EXISTS_MESSAGE = "Clone workspace already exists."


class RepoSourceError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class GitCommand:
    args: tuple[str, ...]
    cwd: Path | None = None
    env: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class GitCommandResult:
    stdout: str
    stderr: str


GitRunner = Callable[[GitCommand], GitCommandResult]


@dataclass(frozen=True, slots=True)
class ResolvedRepo:
    root: Path
    source_label: str
    remote: str
    ref: str
    cleanup_dir: Path | None


def run_git_command(command: GitCommand) -> GitCommandResult:
    env = os.environ.copy()
    if command.env is not None:
        env.update(command.env)
    completed = subprocess.run(
        list(command.args),
        cwd=command.cwd,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RepoSourceError(_safe_git_failure(command.args))
    return GitCommandResult(stdout=completed.stdout, stderr=completed.stderr)


def resolve_repository_source(
    source: str,
    *,
    ref: str | None = None,
    workspace: Path | None = None,
    runner: GitRunner = run_git_command,
) -> ResolvedRepo:
    if _looks_like_git_url(source):
        return _resolve_remote_source(source, ref, workspace, runner)
    return _resolve_local_source(Path(source).expanduser(), runner)


def cleanup_repository_source(resolved: ResolvedRepo) -> None:
    if resolved.cleanup_dir is None:
        return
    if resolved.cleanup_dir.name.startswith("resume-ledger-repo-"):
        _make_tree_writable(resolved.cleanup_dir)
        shutil.rmtree(resolved.cleanup_dir)


def sanitize_remote_url(remote: str) -> str:
    if remote == "":
        return ""
    sanitized = "remote"
    if remote.startswith("git@") and ":" in remote:
        host_owner_repo = remote.removeprefix("git@").replace(":", "/", 1)
        sanitized = _strip_git_suffix(host_owner_repo)
    else:
        parsed = urlparse(remote)
        if parsed.scheme == "file":
            sanitized = "file-remote"
        elif parsed.scheme in ("http", "https", "ssh", "git"):
            path = parsed.path.lstrip("/")
            if parsed.hostname is not None and path != "":
                sanitized = _strip_git_suffix(f"{parsed.hostname}/{path}")
        else:
            path = Path(remote)
            sanitized = "local-remote" if path.is_absolute() or remote.startswith(".") else remote
    return _strip_git_suffix(sanitized)


def _resolve_local_source(path: Path, runner: GitRunner) -> ResolvedRepo:
    if not path.exists():
        raise RepoSourceError(MISSING_SOURCE_MESSAGE)
    try:
        inside = runner(
            GitCommand(args=("git", "-C", str(path), "rev-parse", "--is-inside-work-tree")),
        ).stdout.strip()
    except RepoSourceError as error:
        raise RepoSourceError(NOT_GIT_REPOSITORY_MESSAGE) from error
    if inside != "true":
        raise RepoSourceError(NOT_GIT_REPOSITORY_MESSAGE)
    root_text = runner(
        GitCommand(args=("git", "-C", str(path), "rev-parse", "--show-toplevel")),
    ).stdout.strip()
    remote = _read_optional_remote(Path(root_text), runner)
    return ResolvedRepo(
        root=Path(root_text).resolve(),
        source_label="local",
        remote=remote,
        ref="",
        cleanup_dir=None,
    )


def _resolve_remote_source(
    source: str,
    ref: str | None,
    workspace: Path | None,
    runner: GitRunner,
) -> ResolvedRepo:
    workspace_root = (
        workspace
        if workspace is not None
        else Path(tempfile.mkdtemp(prefix="resume-ledger-repo-"))
    )
    workspace_root.mkdir(parents=True, exist_ok=True)
    destination = workspace_root / _repo_slug(source)
    if destination.exists():
        raise RepoSourceError(CLONE_WORKSPACE_EXISTS_MESSAGE)
    _ = runner(
        GitCommand(
            args=(
                "git",
                "clone",
                "--depth",
                "1",
                "--no-tags",
                "--no-recurse-submodules",
                source,
                str(destination),
            ),
            env={"GIT_TERMINAL_PROMPT": "0", "GIT_LFS_SKIP_SMUDGE": "1"},
        ),
    )
    if ref is not None:
        _ = runner(
            GitCommand(
                args=(
                    "git",
                    "-C",
                    str(destination),
                    "fetch",
                    "--depth",
                    "1",
                    "origin",
                    ref,
                ),
            ),
        )
        _ = runner(
            GitCommand(
                args=("git", "-C", str(destination), "checkout", "--detach", "FETCH_HEAD"),
            ),
        )
    cleanup_dir = workspace_root if workspace is None else None
    return ResolvedRepo(
        root=destination,
        source_label=sanitize_remote_url(source),
        remote=sanitize_remote_url(source),
        ref=ref or "",
        cleanup_dir=cleanup_dir,
    )


def _read_optional_remote(root: Path, runner: GitRunner) -> str:
    try:
        result = runner(GitCommand(args=("git", "-C", str(root), "remote", "get-url", "origin")))
    except RepoSourceError:
        return ""
    return sanitize_remote_url(result.stdout.strip())


def _looks_like_git_url(source: str) -> bool:
    parsed = urlparse(source)
    return parsed.scheme in ("file", "http", "https", "ssh", "git") or source.startswith("git@")


def _repo_slug(source: str) -> str:
    sanitized = sanitize_remote_url(source)
    if sanitized in ("", "remote", "file-remote", "local-remote"):
        return "repository"
    name = sanitized.rstrip("/").split("/")[-1]
    if name == "":
        return "repository"
    return name


def _strip_git_suffix(value: str) -> str:
    if value.endswith(".git"):
        return value[:-4]
    return value


def _safe_git_failure(args: tuple[str, ...]) -> str:
    if "clone" in args:
        return "Git clone failed without interactive prompting."
    if "rev-parse" in args:
        return "Source is not a Git repository."
    if "fetch" in args:
        return "Git ref fetch failed."
    if "checkout" in args:
        return "Git ref checkout failed."
    return "Git command failed."


def _make_tree_writable(root: Path) -> None:
    if not root.exists():
        return
    for path in root.rglob("*"):
        path.chmod(0o700)
    root.chmod(0o700)
