from pathlib import Path
from typing import Final

from .repo_models import RepoEvidenceKind

MAX_SUMMARY_CHARS: Final[int] = 160
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


def is_supported_file(path: str) -> bool:
    name = Path(path).name
    suffix = Path(path).suffix.lower()
    return name in SUPPORTED_NAMES or suffix in SUPPORTED_SUFFIXES


def is_excluded(path: str) -> bool:
    return any(part in EXCLUDED_PARTS for part in Path(path).parts)


def is_sensitive_file(path: str) -> bool:
    lower_name = Path(path).name.lower()
    return (
        lower_name == ".env"
        or lower_name.startswith((".env.", "secrets."))
        or lower_name in ("id_rsa", "id_dsa", "credentials")
        or lower_name.endswith((".pem", ".key"))
    )


def is_manifest(path: str) -> bool:
    return Path(path).name in MANIFEST_NAMES


def is_ci_workflow(path: str) -> bool:
    return path.startswith(".github/workflows/") and Path(path).suffix.lower() in (
        ".yml",
        ".yaml",
    )


def is_test_file(path: str) -> bool:
    name = Path(path).name
    return (
        path.startswith("tests/")
        or "/tests/" in path
        or name.startswith("test_")
        or name.endswith(("_test.py", ".test.ts", ".spec.ts"))
    )


def is_documentation(path: str) -> bool:
    name = Path(path).name.lower()
    return (
        path.startswith("docs/")
        or name.startswith("readme")
        or Path(path).suffix.lower() == ".md"
    )


def language_for_path(path: str) -> str:
    name = Path(path).name
    if name == "Dockerfile":
        return "Docker"
    if name == "Makefile":
        return "Make"
    return LANGUAGE_BY_SUFFIX.get(Path(path).suffix.lower(), "")


def evidence_kind(path: str) -> RepoEvidenceKind:
    if Path(path).name.lower().startswith("readme"):
        return "readme"
    if is_manifest(path):
        return "manifest"
    if is_ci_workflow(path):
        return "ci_workflow"
    if is_test_file(path):
        return "test"
    if is_documentation(path):
        return "documentation"
    return "source_file"


def title_for_path(path: str) -> str:
    return Path(path).name


def tags_for_path(path: str) -> tuple[str, ...]:
    return tuple(tag for tag in (evidence_kind(path), language_for_path(path)) if tag != "")
