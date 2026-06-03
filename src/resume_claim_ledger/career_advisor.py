from collections.abc import Sequence
from typing import Final

from .models import Claim, Suggestion

BROAD_HR_TERMS: Final[tuple[str, ...]] = (
    "대규모",
    "안정적인",
    "최적화",
    "개선했습니다",
    "향상",
)


def advise_career(claims: list[Claim]) -> list[Suggestion]:
    suggestions: list[Suggestion] = []
    for claim in claims:
        if claim.status == "verified":
            continue
        has_broad_signal = (
            claim.category == "impact"
            or claim.status == "too_broad"
            or _has_term(claim.text, BROAD_HR_TERMS)
        )
        if has_broad_signal:
            suggestions.append(_impact_warning(claim))
            continue
        suggestions.append(_role_clarity_info(claim))
    return suggestions


def _impact_warning(claim: Claim) -> Suggestion:
    return Suggestion(
        claim_id=claim.claim_id,
        kind="career",
        severity="warning",
        title="성과 범위가 넓습니다.",
        detail="근거가 약한 성과 주장은 채용 담당자에게 과장으로 읽힐 수 있습니다.",
        suggested_text=_suggested_text(claim),
    )


def _role_clarity_info(claim: Claim) -> Suggestion:
    return Suggestion(
        claim_id=claim.claim_id,
        kind="career",
        severity="info",
        title="본인 역할을 더 분명히 쓰세요.",
        detail="역할, 행동, 산출물을 분리하면 검토자가 기여 범위를 빠르게 이해할 수 있습니다.",
        suggested_text=_suggested_text(claim),
    )


def _suggested_text(claim: Claim) -> str:
    if claim.suggested_rewrite != "":
        return claim.suggested_rewrite
    return claim.text


def _has_term(text: str, terms: Sequence[str]) -> bool:
    lowered = text.casefold()
    return any(term.casefold() in lowered for term in terms)
