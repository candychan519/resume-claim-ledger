from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .ledger_io import read_ledger, write_ledger
from .reporter import build_report
from .reviewer import summarize_statuses
from .scanner import extract_claims

app = typer.Typer(help="Track and review resume claims against evidence.")
console = Console()


@app.command()
def scan(
    resume: Annotated[Path, typer.Argument(help="Markdown resume file to scan.")],
    out: Annotated[Path, typer.Option("--out", "-o", help="YAML ledger output path.")],
) -> None:
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
) -> None:
    claims = read_ledger(ledger)
    _ = out.write_text(build_report(claims), encoding="utf-8")
    console.print(f"Wrote report to {out}")
