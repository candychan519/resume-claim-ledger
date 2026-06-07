from collections.abc import Mapping
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from .repo_analyzer import (
    DEFAULT_MAX_FILES,
    RepoAnalysisError,
    analyze_repository,
)
from .repo_reporter import RepoOutputFile, build_repo_knowledge_pack_outputs
from .repo_source import RepoSourceError, cleanup_repository_source, resolve_repository_source

repo_app = typer.Typer(help="Build repository evidence knowledge packs.")
console = Console()
error_console = Console(stderr=True)

OUTPUT_NOT_EMPTY_MESSAGE = "Output directory is not empty."
OUTPUT_NOT_DIRECTORY_MESSAGE = "Output path exists and is not a directory."


@repo_app.command()
def intake(
    source: Annotated[str, typer.Argument(help="Git URL or local Git repository path.")],
    out: Annotated[Path, typer.Option("--out", help="Knowledge pack output directory.")],
    *,
    name: Annotated[
        str | None,
        typer.Option("--name", help="Repository display name for the knowledge pack."),
    ] = None,
    ref: Annotated[
        str | None,
        typer.Option("--ref", help="Optional remote ref to fetch and analyze."),
    ] = None,
    max_files: Annotated[
        int,
        typer.Option("--max-files", help="Maximum tracked files to analyze."),
    ] = DEFAULT_MAX_FILES,
) -> None:
    try:
        _check_output_target(out)
        resolved = resolve_repository_source(source, ref=ref)
        try:
            pack = analyze_repository(
                resolved.root,
                name=name or _default_name(source, resolved.source_label),
                source_label=resolved.source_label,
                remote=resolved.remote,
                ref=resolved.ref,
                max_files=max_files,
            )
            outputs = build_repo_knowledge_pack_outputs(pack)
            _write_outputs(out, outputs)
        finally:
            cleanup_repository_source(resolved)
    except (RepoSourceError, RepoAnalysisError, ValueError) as error:
        error_console.print(str(error))
        raise typer.Exit(1) from error

    console.print("Wrote repository knowledge pack.")
    for filename in sorted(outputs):
        console.print(f"- {filename}")


def _check_output_target(out: Path) -> None:
    if not out.exists():
        return
    if not out.is_dir():
        raise ValueError(OUTPUT_NOT_DIRECTORY_MESSAGE)
    if any(out.iterdir()):
        raise ValueError(OUTPUT_NOT_EMPTY_MESSAGE)


def _write_outputs(out: Path, outputs: Mapping[RepoOutputFile, str]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for filename, content in outputs.items():
        _ = (out / filename).write_text(content, encoding="utf-8")


def _default_name(source: str, source_label: str) -> str:
    if source_label not in ("", "local", "remote", "file-remote", "local-remote"):
        candidate = source_label.rstrip("/").split("/")[-1]
        if candidate != "":
            return candidate
    path_name = Path(source).name
    if path_name != "":
        return path_name.removesuffix(".git")
    return "repository"
