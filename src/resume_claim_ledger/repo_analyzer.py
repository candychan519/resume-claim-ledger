from dataclasses import dataclass
from pathlib import Path
from typing import Final

from .repo_models import (
    RepoClaimCandidate,
    RepoEvidenceGap,
    RepoEvidenceItem,
    RepoEvidenceKind,
    RepoGapSeverity,
    RepoKnowledgeGraph,
    RepoKnowledgeGraphEdge,
    RepoKnowledgeGraphNode,
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
MAX_SUMMARY_CHARS: Final[int] = 160
GIT_LOG_FIELD_COUNT: Final[int] = 5
MAX_FILES_EXCEEDED_MESSAGE = "Repository file count exceeds --max-files."

SUPPORTED_SUFFIXES: Final[tuple[str, ...]] = (
    ".md",
    ".txt",
    ".py",
    ".toml",
    ".json",
    ".yml",
    ".yaml",
    ".js",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".sh",
    ".ps1",
    ".sql",
    ".dockerfile",
)
SUPPORTED_NAMES: Final[tuple[str, ...]] = ("Dockerfile", "Makefile")
EXCLUDED_PARTS: Final[tuple[str, ...]] = (
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    ".mypy_cache",
    ".tox",
    ".idea",
    ".vscode",
    "vendor",
)
MANIFEST_NAMES: Final[tuple[str, ...]] = (
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "requirements.txt",
    "uv.lock",
    "pnpm-lock.yaml",
)
LANGUAGE_BY_SUFFIX: Final[dict[str, str]] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".sh": "Shell",
    ".ps1": "PowerShell",
    ".sql": "SQL",
    ".dockerfile": "Docker",
}

CONTRIBUTION_CONFIRMATION = (
    "Confirm personal contribution, role, ownership, dates, usage scope, and impact before use."
)


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
    visible_files = tuple(path for path in tracked_files if not _is_excluded(path))
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
        if _is_sensitive_file(relative_path):
            _append_evidence(
                evidence_items,
                "sensitive_file",
                relative_path,
                "Sensitive file presence",
                "Sensitive file presence recorded; contents were not read.",
                ("sensitive",),
            )
            continue
        if not _is_supported_file(relative_path):
            continue
        _collect_profile_signals(relative_path, languages, manifests, ci_workflows, tests, docs)
        language = _language_for_path(relative_path)
        if language != "":
            source_files.append(relative_path)
        if path.stat().st_size > max_file_bytes:
            _append_gap(
                evidence_gaps,
                f"File `{relative_path}` exceeded the read-size limit and was not summarized.",
                "warning",
                (relative_path,),
            )
            continue
        summary = _summary_for_file(path)
        _append_evidence(
            evidence_items,
            _evidence_kind(relative_path),
            relative_path,
            _title_for_path(relative_path),
            summary,
            _tags_for_path(relative_path),
        )

    commits = _recent_commits(root, max_commits, runner)
    for commit in commits:
        _append_evidence(
            evidence_items,
            "commit",
            "git-log",
            commit.commit_hash[:7],
            f"Recent commit subject ({commit.date}): {commit.subject}",
            ("commit",),
        )

    if visible_files == ():
        _append_gap(evidence_gaps, "No tracked repository files were found.", "blocker", ())
    _append_gap(
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
    claim_candidates = _claim_candidates(profile, tuple(sorted(set(source_files))))
    graph = _knowledge_graph(profile, tuple(evidence_items), claim_candidates, tuple(evidence_gaps))
    return RepoKnowledgePack(
        profile=profile,
        evidence_items=tuple(evidence_items),
        claim_candidates=claim_candidates,
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
    language = _language_for_path(relative_path)
    if language != "":
        languages.add(language)
    if _is_manifest(relative_path):
        manifests.append(relative_path)
    if _is_ci_workflow(relative_path):
        ci_workflows.append(relative_path)
    if _is_test_file(relative_path):
        tests.append(relative_path)
    if _is_documentation(relative_path):
        docs.append(relative_path)


def _claim_candidates(
    profile: RepoProfile,
    source_files: tuple[str, ...],
) -> tuple[RepoClaimCandidate, ...]:
    candidates: list[RepoClaimCandidate] = []
    if profile.languages != ():
        supporting = profile.package_manifests + source_files[:3]
        candidates.append(
            RepoClaimCandidate(
                claim_id=_claim_id(len(candidates)),
                text=f"Repository contains a {', '.join(profile.languages)} codebase.",
                confidence="medium" if profile.package_manifests != () else "low",
                supporting_files=supporting,
                missing_confirmation=CONTRIBUTION_CONFIRMATION,
            ),
        )
    if profile.ci_workflows != ():
        candidates.append(
            RepoClaimCandidate(
                claim_id=_claim_id(len(candidates)),
                text="Repository includes CI workflow configuration.",
                confidence="low",
                supporting_files=profile.ci_workflows,
                missing_confirmation=CONTRIBUTION_CONFIRMATION,
            ),
        )
    if profile.test_files != ():
        candidates.append(
            RepoClaimCandidate(
                claim_id=_claim_id(len(candidates)),
                text="Repository includes automated test files.",
                confidence="low",
                supporting_files=profile.test_files,
                missing_confirmation=CONTRIBUTION_CONFIRMATION,
            ),
        )
    return tuple(candidates)


def _knowledge_graph(
    profile: RepoProfile,
    evidence_items: tuple[RepoEvidenceItem, ...],
    candidates: tuple[RepoClaimCandidate, ...],
    gaps: tuple[RepoEvidenceGap, ...],
) -> RepoKnowledgeGraph:
    project_id = f"project:{profile.name}"
    nodes = [RepoKnowledgeGraphNode(project_id, "Project", profile.name)]
    edges: list[RepoKnowledgeGraphEdge] = []
    for language in profile.languages:
        tech_id = f"tech:{language}"
        nodes.append(RepoKnowledgeGraphNode(tech_id, "TechStack", language))
        edges.append(RepoKnowledgeGraphEdge(project_id, tech_id, "uses"))
    for item in evidence_items:
        evidence_id = f"evidence:{item.evidence_id}"
        nodes.append(RepoKnowledgeGraphNode(evidence_id, "Evidence", item.title))
        edges.append(RepoKnowledgeGraphEdge(project_id, evidence_id, "has_evidence"))
    for candidate in candidates:
        claim_id = f"claim:{candidate.claim_id}"
        nodes.append(RepoKnowledgeGraphNode(claim_id, "ClaimCandidate", candidate.text))
        edges.append(RepoKnowledgeGraphEdge(project_id, claim_id, "has_claim_candidate"))
    for gap in gaps:
        gap_id = f"gap:{gap.gap_id}"
        nodes.append(RepoKnowledgeGraphNode(gap_id, "EvidenceGap", gap.text))
        edges.append(RepoKnowledgeGraphEdge(project_id, gap_id, "has_gap"))
    return RepoKnowledgeGraph(nodes=tuple(nodes), edges=tuple(edges))


def _append_evidence(
    items: list[RepoEvidenceItem],
    kind: RepoEvidenceKind,
    path: str,
    title: str,
    summary: str,
    tags: tuple[str, ...],
) -> None:
    items.append(
        RepoEvidenceItem(
            evidence_id=_evidence_id(len(items)),
            kind=kind,
            path=path,
            title=title,
            summary=summary,
            tags=tags,
        ),
    )


def _append_gap(
    gaps: list[RepoEvidenceGap],
    text: str,
    severity: RepoGapSeverity,
    related_files: tuple[str, ...],
) -> None:
    gaps.append(
        RepoEvidenceGap(
            gap_id=_gap_id(len(gaps)),
            text=text,
            severity=severity,
            related_files=related_files,
        ),
    )


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


def _is_supported_file(path: str) -> bool:
    name = Path(path).name
    suffix = Path(path).suffix.lower()
    return name in SUPPORTED_NAMES or suffix in SUPPORTED_SUFFIXES


def _is_excluded(path: str) -> bool:
    return any(part in EXCLUDED_PARTS for part in Path(path).parts)


def _is_sensitive_file(path: str) -> bool:
    name = Path(path).name
    lower_name = name.lower()
    return (
        lower_name == ".env"
        or lower_name.startswith((".env.", "secrets."))
        or lower_name in ("id_rsa", "id_dsa", "credentials")
        or lower_name.endswith((".pem", ".key"))
    )


def _is_manifest(path: str) -> bool:
    return Path(path).name in MANIFEST_NAMES


def _is_ci_workflow(path: str) -> bool:
    return path.startswith(".github/workflows/") and Path(path).suffix.lower() in (
        ".yml",
        ".yaml",
    )


def _is_test_file(path: str) -> bool:
    name = Path(path).name
    return (
        path.startswith("tests/")
        or "/tests/" in path
        or name.startswith("test_")
        or name.endswith(("_test.py", ".test.ts", ".spec.ts"))
    )


def _is_documentation(path: str) -> bool:
    name = Path(path).name.lower()
    return (
        path.startswith("docs/")
        or name.startswith("readme")
        or Path(path).suffix.lower() == ".md"
    )


def _language_for_path(path: str) -> str:
    name = Path(path).name
    if name == "Dockerfile":
        return "Docker"
    if name == "Makefile":
        return "Make"
    return LANGUAGE_BY_SUFFIX.get(Path(path).suffix.lower(), "")


def _evidence_kind(path: str) -> RepoEvidenceKind:
    if Path(path).name.lower().startswith("readme"):
        return "readme"
    if _is_manifest(path):
        return "manifest"
    if _is_ci_workflow(path):
        return "ci_workflow"
    if _is_test_file(path):
        return "test"
    if _is_documentation(path):
        return "documentation"
    return "source_file"


def _title_for_path(path: str) -> str:
    return Path(path).name


def _tags_for_path(path: str) -> tuple[str, ...]:
    return tuple(tag for tag in (_evidence_kind(path), _language_for_path(path)) if tag != "")


def _evidence_id(index: int) -> str:
    return f"REPO-EVD-{index + 1:03d}"


def _claim_id(index: int) -> str:
    return f"REPO-CLM-{index + 1:03d}"


def _gap_id(index: int) -> str:
    return f"REPO-GAP-{index + 1:03d}"
