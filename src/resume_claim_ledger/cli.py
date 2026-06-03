from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .ledger_io import read_ledger, read_ledger_result, write_ledger
from .reporter import build_report
from .reviewer import summarize_statuses
from .scanner import extract_claims

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
