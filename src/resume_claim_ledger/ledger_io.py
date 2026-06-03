from pathlib import Path

from .models import Claim, ClaimCategory, ClaimStatus

MIN_QUOTED_LENGTH = 2


def write_ledger(path: Path, claims: list[Claim]) -> None:
    lines = ["claims:"]
    for claim in claims:
        lines.extend(
            [
                f"  - claim_id: {claim.claim_id}",
                f"    text: {_quote(claim.text)}",
                f"    category: {claim.category}",
                f"    status: {claim.status}",
                f"    evidence_note: {_quote(claim.evidence_note)}",
                f"    suggested_rewrite: {_quote(claim.suggested_rewrite)}",
            ],
        )
    _ = path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_ledger(path: Path) -> list[Claim]:
    items = _parse_generated_yaml(path.read_text(encoding="utf-8"))
    return [_claim_from_fields(fields) for fields in items]


def _quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _unquote(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= MIN_QUOTED_LENGTH and stripped[0] == '"' and stripped[-1] == '"':
        return stripped[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return stripped


def _parse_generated_yaml(content: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    current: dict[str, str] = {}

    for line in content.splitlines():
        stripped = line.strip()
        if stripped in ("", "claims:"):
            continue
        if stripped.startswith("- "):
            if current:
                records.append(current)
            current = _field_from_line(stripped[2:])
            continue
        if current:
            current.update(_field_from_line(stripped))

    if current:
        records.append(current)
    return records


def _field_from_line(line: str) -> dict[str, str]:
    key, separator, value = line.partition(":")
    if separator == "":
        return {}
    return {key.strip(): _unquote(value.strip())}


def _claim_from_fields(fields: dict[str, str]) -> Claim:
    return Claim(
        claim_id=fields.get("claim_id", ""),
        text=fields.get("text", ""),
        category=_parse_category(fields.get("category", "")),
        status=_parse_status(fields.get("status", "")),
        evidence_note=fields.get("evidence_note", ""),
        suggested_rewrite=fields.get("suggested_rewrite", ""),
    )


def _parse_category(value: str) -> ClaimCategory:
    match value:
        case "impact":
            return "impact"
        case "execution":
            return "execution"
        case "scope":
            return "scope"
        case _:
            return "scope"


def _parse_status(value: str) -> ClaimStatus:
    match value:
        case "verified":
            return "verified"
        case "needs_evidence":
            return "needs_evidence"
        case "too_broad":
            return "too_broad"
        case "rewrite_needed":
            return "rewrite_needed"
        case _:
            return "needs_evidence"
