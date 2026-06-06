import json
from pathlib import Path
from typing import Annotated, Literal, TypedDict

import typer
from rich.console import Console
from rich.table import Table

from .career_advisor import advise_career
from .coordinate_reporter import (
    build_coordinate_json,
    build_coordinate_markdown,
    build_coordinate_summary_markdown,
)
from .coordinator import coordinate_submission
from .evidence_catalog import load_evidence_catalog
from .job_parser import extract_job_requirements
from .korean_polish import advise_korean_polish
from .ledger_io import read_ledger, read_ledger_result, write_ledger
from .models import Claim, ClaimStatus, Suggestion, SuggestionDict, suggestion_to_dict
from .reporter import build_report
from .reviewer import summarize_statuses
from .scanner import extract_claims

AdviceFormat = Literal["markdown", "json"]
CoordinateFormat = Literal["markdown", "json"]
UNRESOLVED_STATUSES: tuple[ClaimStatus, ...] = (
    "needs_evidence",
    "too_broad",
    "rewrite_needed",
)


class AdvicePayload(TypedDict):
    schema_version: int
    suggestions: list[SuggestionDict]


app = typer.Typer(help="Track and review resume claims against evidence.")
console = Console()
error_console = Console(stderr=True)


@app.command()
def scan(
    resume: Annotated[Path, typer.Argument(help="Markdown resume file to scan.")],
    out: Annotated[Path, typer.Option("--out", "-o", help="YAML ledger output path.")],
) -> None:
    if not resume.exists():
        error_console.print(f"Resume file does not exist: {resume}")
        raise typer.Exit(1)
    claims = extract_claims(resume.read_text(encoding="utf-8"))
    write_ledger(out, claims)
    console.print(f"Wrote {len(claims)} claims to {out}")


@app.command()
def review(
    ledger: Annotated[Path, typer.Argument(help="Claim ledger YAML file.")],
) -> None:
    claims = read_ledger(ledger)
    counts = summarize_statuses(claims)
    table = Table(title="Claim Review")
    table.add_column("Status")
    table.add_column("Count", justify="right")
    for status, count in counts.items():
        table.add_row(status, str(count))
    console.print(table)


@app.command()
def doctor(
    ledger: Annotated[Path, typer.Argument(help="Claim ledger YAML file.")],
) -> None:
    if not ledger.exists():
        error_console.print(f"Ledger file does not exist: {ledger}")
        raise typer.Exit(1)

    result = read_ledger_result(ledger)
    counts = summarize_statuses(result.claims)
    table = Table(title="Submission Doctor")
    table.add_column("Check")
    table.add_column("Result", justify="right")
    table.add_row("warnings", str(len(result.warnings)))
    for status, count in counts.items():
        table.add_row(status, str(count))
    console.print(table)

    unresolved = [status for status in UNRESOLVED_STATUSES if counts[status] > 0]
    if result.warnings != []:
        error_console.print(f"Doctor found ledger warnings: {', '.join(result.warnings)}")
    if unresolved != []:
        error_console.print(f"Doctor found unresolved claims: {', '.join(unresolved)}")
    if result.warnings != [] or unresolved != []:
        raise typer.Exit(1)

    console.print("Ready for submission.")


@app.command()
def report(
    ledger: Annotated[Path, typer.Argument(help="Claim ledger YAML file.")],
    out: Annotated[Path, typer.Option("--out", "-o", help="Markdown report output path.")],
    *,
    strict: Annotated[
        bool,
        typer.Option("--strict", help="Fail when unresolved claims remain."),
    ] = False,
) -> None:
    result = read_ledger_result(ledger)
    _ = out.write_text(build_report(result.claims, warnings=result.warnings), encoding="utf-8")
    console.print(f"Wrote report to {out}")
    unresolved = [
        claim.status
        for claim in result.claims
        if claim.status in ("needs_evidence", "too_broad", "rewrite_needed")
    ]
    if strict and unresolved != []:
        error_console.print(
            f"Strict mode blocked unresolved claim statuses: {', '.join(sorted(set(unresolved)))}",
        )
        raise typer.Exit(1)


@app.command()
def coordinate(  # noqa: PLR0913
    ledger: Annotated[Path, typer.Argument(help="Claim ledger YAML file.")],
    out: Annotated[Path, typer.Option("--out", "-o", help="Submission plan output path.")],
    *,
    job: Annotated[
        Path | None,
        typer.Option("--job", help="Optional job description file."),
    ] = None,
    evidence_dir: Annotated[
        Path | None,
        typer.Option("--evidence-dir", help="Optional evidence directory."),
    ] = None,
    output_format: Annotated[
        CoordinateFormat,
        typer.Option("--format", help="Coordinate output format."),
    ] = "markdown",
    strict: Annotated[
        bool,
        typer.Option("--strict", help="Fail when submission blockers remain."),
    ] = False,
    summary: Annotated[
        bool,
        typer.Option("--summary", help="Write compact Markdown summary output."),
    ] = False,
) -> None:
    if not ledger.exists():
        error_console.print(f"Ledger file does not exist: {ledger}")
        raise typer.Exit(1)
    if job is not None and not job.exists():
        error_console.print(f"Job file does not exist: {job}")
        raise typer.Exit(1)
    if evidence_dir is not None and not evidence_dir.exists():
        error_console.print(f"Evidence directory does not exist: {evidence_dir}")
        raise typer.Exit(1)

    result = read_ledger_result(ledger)
    requirements = (
        extract_job_requirements(job.read_text(encoding="utf-8")) if job is not None else []
    )
    evidence = load_evidence_catalog(evidence_dir) if evidence_dir is not None else []
    plan = coordinate_submission(result.claims, requirements, evidence, result.warnings)

    match output_format:
        case "markdown":
            content = (
                build_coordinate_summary_markdown(plan)
                if summary
                else build_coordinate_markdown(plan)
            )
        case "json":
            content = build_coordinate_json(plan)

    _ = out.write_text(content, encoding="utf-8")
    console.print(f"Wrote submission plan to {out}")

    has_blockers = any(item.action == "submission_blocker" for item in plan.items)
    if strict and (plan.warnings != () or has_blockers):
        error_console.print("Strict mode blocked coordinate submission plan.")
        raise typer.Exit(1)


@app.command()
def advise(  # noqa: PLR0913
    ledger: Annotated[Path, typer.Argument(help="Claim ledger YAML file.")],
    out: Annotated[Path, typer.Option("--out", "-o", help="Advice output path.")],
    *,
    career: Annotated[
        bool,
        typer.Option("--career/--no-career", help="Include career and HR review suggestions."),
    ] = True,
    polish_ko: Annotated[
        bool,
        typer.Option("--polish-ko/--no-polish-ko", help="Include Korean polish suggestions."),
    ] = True,
    output_format: Annotated[
        AdviceFormat,
        typer.Option("--format", help="Advice output format."),
    ] = "markdown",
    strict: Annotated[
        bool,
        typer.Option("--strict", help="Fail when critical suggestions remain."),
    ] = False,
) -> None:
    result = read_ledger_result(ledger)
    suggestions = _collect_suggestions(result.claims, career=career, polish_ko=polish_ko)
    match output_format:
        case "markdown":
            content = _build_advice_markdown(result.claims, result.warnings, suggestions)
        case "json":
            content = _build_advice_json(suggestions)

    _ = out.write_text(content, encoding="utf-8")
    console.print(f"Wrote advice to {out}")

    critical = [suggestion for suggestion in suggestions if suggestion.severity == "critical"]
    if strict and critical != []:
        error_console.print("Strict mode blocked critical career advice suggestions.")
        raise typer.Exit(1)


def _collect_suggestions(
    claims: list[Claim],
    *,
    career: bool,
    polish_ko: bool,
) -> list[Suggestion]:
    suggestions: list[Suggestion] = []
    if career:
        suggestions.extend(advise_career(claims))
    if polish_ko:
        suggestions.extend(advise_korean_polish(claims))
    return suggestions


def _build_advice_markdown(
    claims: list[Claim],
    warnings: list[str],
    suggestions: list[Suggestion],
) -> str:
    if suggestions == []:
        lines = ["# Claim Advice", "", "No career or Korean polish suggestions found."]
        if warnings != []:
            lines.extend(["", "## Warnings", "", *[f"- {warning}" for warning in warnings]])
        return "\n".join(lines) + "\n"
    return build_report(claims, warnings=warnings, suggestions=suggestions)


def _build_advice_json(suggestions: list[Suggestion]) -> str:
    payload: AdvicePayload = {
        "schema_version": 1,
        "suggestions": [suggestion_to_dict(suggestion) for suggestion in suggestions],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
