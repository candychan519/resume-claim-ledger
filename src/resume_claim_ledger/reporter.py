from .models import Claim
from .reviewer import summarize_statuses

CATEGORY_GUIDE = {
    "impact": "성과, 범위, 지표 중심 주장입니다.",
    "execution": "실행, 산출물, 역할 중심 주장입니다.",
    "scope": "범위나 맥락 확인이 필요한 주장입니다.",
}


def build_report(claims: list[Claim], warnings: list[str] | None = None) -> str:
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
        "## Category Guide",
        "",
        f"- impact: {CATEGORY_GUIDE['impact']}",
        f"- execution: {CATEGORY_GUIDE['execution']}",
        f"- scope: {CATEGORY_GUIDE['scope']}",
        "",
    ]

    if warnings is not None and warnings != []:
        lines.extend(["## Warnings", "", *[f"- {warning}" for warning in warnings], ""])

    lines.extend(
        [
        "## Claims",
        "",
        ],
    )

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
