from pathlib import Path
from typing import Final

from .models import EvidenceItem

SUPPORTED_SUFFIXES: Final = frozenset({".md", ".txt"})


def load_evidence_catalog(path: Path) -> list[EvidenceItem]:
    if not path.exists():
        raise FileNotFoundError(path)
    if not path.is_dir():
        raise NotADirectoryError(path)

    items: list[EvidenceItem] = []
    for evidence_file in _evidence_files(path):
        item_number = len(items) + 1
        items.append(
            EvidenceItem(
                evidence_id=f"EVD-{item_number:03}",
                display_name=evidence_file.name,
                summary=_summary_for_file(evidence_file),
            ),
        )
    return items


def _evidence_files(path: Path) -> list[Path]:
    return sorted(
        (
            child
            for child in path.iterdir()
            if child.is_file() and child.suffix.casefold() in SUPPORTED_SUFFIXES
        ),
        key=lambda child: child.name.casefold(),
    )


def _summary_for_file(path: Path) -> str:
    first_non_empty = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line == "":
            continue
        if line.startswith("#"):
            return _clean_heading(line)
        if first_non_empty == "":
            first_non_empty = line
    return first_non_empty


def _clean_heading(line: str) -> str:
    if not line.startswith("#"):
        return line
    return line.lstrip("#").strip()
