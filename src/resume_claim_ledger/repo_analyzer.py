from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .repo_analyzer_builders import (
    append_evidence,
    append_gap,
    claim_candidates,
    knowledge_graph,
)
from .repo_analyzer_rules import (
    MAX_SUMMARY_CHARS,
    evidence_kind,
    is_ci_workflow,
    is_documentation,
    is_excluded,
    is_manifest,
    is_sensitive_file,
    is_supported_file,
    is_test_file,
    language_for_path,
    tags_for_path,
    title_for_path,
)
from .repo_models import (
    RepoEvidenceGap,
    RepoEvidenceItem,
    RepoKnowledgePack,
    RepoProfile,
)
from .repo_source import (
    GitCommand,
    GitRunner,
    RepoSourceError,
    run_git_command,
    sanitize_remote_url,
)

DEFAULT_MAX_FILES: Final[int] = 500
DEFAULT_MAX_FILE_BYTES: Final[int] = 200_000
DEFAULT_MAX_COMMITS: Final[int] = 50
GIT_LOG_FIELD_COUNT: Final[int] = 5
MAX_FILES_EXCEEDED_MESSAGE = "Repository file count exceeds --max-files."

class RepoAnalysisError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class RecentCommit:
    commit_hash: str
    date: str
    subject: str


def analyze_repository(
    root: Path,
    *,
    name: str,
    source_label: str,
    remote: str = "",
    ref: str = "",
    max_files: int = DEFAULT_MAX_FILES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_commits: int = DEFAULT_MAX_COMMITS,
    runner: GitRunner = run_git_command,
) -> RepoKnowledgePack:
    tracked_files = _tracked_files(root, runner)
    visible_files = tuple(path for path in tracked_files if not is_excluded(path))
    if len(visible_files) > max_files:
        raise RepoAnalysisError(MAX_FILES_EXCEEDED_MESSAGE)

    evidence_items: list[RepoEvidenceItem] = []
    evidence_gaps: list[RepoEvidenceGap] = []
    languages: set[str] = set()
    manifests: list[str] = []
    ci_workflows: list[str] = []
    tests: list[str] = []
    docs: list[str] = []
    source_files: list[str] = []

    for relative_path in visible_files:
        path = root / relative_path
        if is_sensitive_file(relative_path):
            append_evidence(
                evidence_items,
                "sensitive_file",
                relative_path,
                "Sensitive file presence",
                "Sensitive file presence recorded; contents were not read.",
                ("sensitive",),
            )
            continue
        if not is_supported_file(relative_path):
            continue
        _collect_profile_signals(relative_path, languages, manifests, ci_workflows, tests, docs)
        language = language_for_path(relative_path)
        if language != "":
            source_files.append(relative_path)
        if path.stat().st_size > max_file_bytes:
            append_gap(
                evidence_gaps,
                f"File `{relative_path}` exceeded the read-size limit and was not summarized.",
                "warning",
                (relative_path,),
            )
            continue
        summary = _summary_for_file(path)
        append_evidence(
            evidence_items,
            evidence_kind(relative_path),
            relative_path,
            title_for_path(relative_path),
            summary,
            tags_for_path(relative_path),
        )

    commits = _recent_commits(root, max_commits, runner)
    for commit in commits:
        append_evidence(
            evidence_items,
            "commit",
            "git-log",
            commit.commit_hash[:7],
            f"Recent commit subject ({commit.date}): {commit.subject}",
            ("commit",),
        )

    if visible_files == ():
        append_gap(evidence_gaps, "No tracked repository files were found.", "blocker", ())
    append_gap(
        evidence_gaps,
        "Repository contents do not confirm personal contribution, ownership, or impact.",
        "blocker",
        (),
    )

    profile = RepoProfile(
        name=name,
        source=source_label,
        revision=_revision_from_commits(commits, ref),
        remote=_safe_remote(root, remote, runner),
        languages=tuple(sorted(languages)),
        package_manifests=tuple(sorted(set(manifests))),
        ci_workflows=tuple(sorted(set(ci_workflows))),
        test_files=tuple(sorted(set(tests))),
        documentation_files=tuple(sorted(set(docs))),
        warnings=(
            "Repository analysis is static and report-only.",
            "Code presence is not proof of personal contribution or production impact.",
        ),
    )
    candidates = claim_candidates(profile, tuple(sorted(set(source_files))))
    graph = knowledge_graph(profile, tuple(evidence_items), candidates, tuple(evidence_gaps))
    return RepoKnowledgePack(
        profile=profile,
        evidence_items=tuple(evidence_items),
        claim_candidates=candidates,
        evidence_gaps=tuple(evidence_gaps),
        knowledge_graph=graph,
    )


def _tracked_files(root: Path, runner: GitRunner) -> tuple[str, ...]:
    result = runner(GitCommand(args=("git", "-C", str(root), "ls-files", "-z")))
    paths = tuple(path for path in result.stdout.split("\0") if path != "")
    return tuple(sorted(path.replace("\\", "/") for path in paths))


def _recent_commits(root: Path, max_commits: int, runner: GitRunner) -> tuple[RecentCommit, ...]:
    try:
        result = runner(
            GitCommand(
                args=(
                    "git",
                    "-C",
                    str(root),
                    "log",
                    "--format=%H%x09%an%x09%ae%x09%ad%x09%s",
                    "--date=short",
                    "-n",
                    "50",
                ),
            ),
        )
    except RepoSourceError:
        return ()
    commits: list[RecentCommit] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t", 4)
        if len(parts) == GIT_LOG_FIELD_COUNT:
            commits.append(RecentCommit(commit_hash=parts[0], date=parts[3], subject=parts[4]))
    return tuple(commits[:max_commits])


def _collect_profile_signals(
    relative_path: str,
    languages: set[str],
    manifests: list[str],
    ci_workflows: list[str],
    tests: list[str],
    docs: list[str],
) -> None:
    language = language_for_path(relative_path)
    if language != "":
        languages.add(language)
    if is_manifest(relative_path):
        manifests.append(relative_path)
    if is_ci_workflow(relative_path):
        ci_workflows.append(relative_path)
    if is_test_file(relative_path):
        tests.append(relative_path)
    if is_documentation(relative_path):
        docs.append(relative_path)


def _summary_for_file(path: Path) -> str:
    content = path.read_text(encoding="utf-8", errors="replace")
    for line in content.splitlines():
        stripped = line.strip().strip("#").strip()
        if stripped != "":
            return stripped[:MAX_SUMMARY_CHARS]
    return "(empty file)"


def _safe_remote(root: Path, remote: str, runner: GitRunner) -> str:
    if remote != "":
        return sanitize_remote_url(remote)
    try:
        result = runner(GitCommand(args=("git", "-C", str(root), "remote", "get-url", "origin")))
    except RepoSourceError:
        return ""
    return sanitize_remote_url(result.stdout.strip())


def _revision_from_commits(commits: tuple[RecentCommit, ...], ref: str) -> str:
    if commits != ():
        return commits[0].commit_hash[:7]
    if ref != "":
        return ref
    return "unknown"

