from .models import Claim, Suggestion
from .reviewer import summarize_statuses

CATEGORY_GUIDE = {
    "impact": "성과, 범위, 지표 중심 주장입니다.",
    "execution": "실행, 산출물, 역할 중심 주장입니다.",
    "scope": "범위나 맥락 확인이 필요한 주장입니다.",
}


def build_report(
    claims: list[Claim],
    warnings: list[str] | None = None,
    suggestions: list[Suggestion] | None = None,
) -> str:
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

    lines.extend(_suggestion_sections(suggestions or []))

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


def _suggestion_sections(suggestions: list[Suggestion]) -> list[str]:
    career: list[Suggestion] = []
    korean_polish: list[Suggestion] = []
    for suggestion in suggestions:
        match suggestion.kind:
            case "career":
                career.append(suggestion)
            case "korean_polish":
                korean_polish.append(suggestion)

    lines: list[str] = []
    lines.extend(_suggestion_section("Career Review", career))
    lines.extend(_suggestion_section("Korean Polish", korean_polish))
    return lines


def _suggestion_section(title: str, suggestions: list[Suggestion]) -> list[str]:
    if suggestions == []:
        return []

    lines = ["", f"## {title}", ""]
    for suggestion in suggestions:
        lines.extend(
            [
                f"### {suggestion.claim_id}: {suggestion.title}",
                "",
                f"- severity: {suggestion.severity}",
                f"- detail: {suggestion.detail}",
                f"- suggestion: {suggestion.suggested_text}",
                "",
            ],
        )
    return lines
