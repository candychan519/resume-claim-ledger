from .models import Claim
from .reviewer import summarize_statuses


def build_report(claims: list[Claim]) -> str:
    counts = summarize_statuses(claims)
    lines = [
        "# Claim Review",
        "",
        "## Summary",
        "",
        f"- verified: {counts['verified']}",
        f"- needs_evidence: {counts['needs_evidence']}",
        f"- too_broad: {counts['too_broad']}",
        f"- rewrite_needed: {counts['rewrite_needed']}",
        "",
        "## Claims",
        "",
    ]

    for claim in claims:
        lines.extend(_claim_lines(claim))

    return "\n".join(lines).rstrip() + "\n"


def _claim_lines(claim: Claim) -> list[str]:
    lines = [
        f"### {claim.claim_id}",
        "",
        f"- text: {claim.text}",
        f"- status: {claim.status}",
        f"- evidence: {claim.evidence_note}",
    ]
    if claim.suggested_rewrite != "":
        lines.append(f"- safer rewrite: {claim.suggested_rewrite}")
    lines.append("")
    return lines
