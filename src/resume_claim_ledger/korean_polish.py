from typing import Final, NamedTuple

from .models import Claim, Suggestion


class PolishRule(NamedTuple):
    pattern: str
    replacement: str
    title: str
    detail: str


POLISH_RULES: Final[tuple[PolishRule, ...]] = (
    PolishRule(
        pattern="를 통해",
        replacement="로",
        title="번역투 표현입니다.",
        detail="'를 통해' 표현이 반복되면 AI 문체처럼 읽힐 수 있습니다.",
    ),
    PolishRule(
        pattern="을 통해",
        replacement="으로",
        title="번역투 표현입니다.",
        detail="'을 통해' 표현이 반복되면 AI 문체처럼 읽힐 수 있습니다.",
    ),
    PolishRule(
        pattern="에 있어서",
        replacement="에서",
        title="번역투 표현입니다.",
        detail="'에 있어서'는 이력서 문장에서 무겁고 번역투처럼 읽힐 수 있습니다.",
    ),
    PolishRule(
        pattern="성장했습니다",
        replacement="배웠습니다",
        title="범용 성장 표현입니다.",
        detail="'성장했습니다'는 구체 행동 없이 쓰이면 흔한 자기소개서 표현처럼 보입니다.",
    ),
    PolishRule(
        pattern="탁월한",
        replacement="",
        title="강한 수식어입니다.",
        detail="'탁월한'은 근거 없이 쓰이면 과장으로 읽힐 수 있습니다.",
    ),
    PolishRule(
        pattern="뛰어난",
        replacement="",
        title="강한 수식어입니다.",
        detail="'뛰어난'은 근거 없이 쓰이면 과장으로 읽힐 수 있습니다.",
    ),
    PolishRule(
        pattern="결론적으로",
        replacement="",
        title="AI 문체 신호입니다.",
        detail="'결론적으로'는 짧은 이력서 문장에서는 불필요한 결산 표현입니다.",
    ),
    PolishRule(
        pattern="시사하는 바",
        replacement="의미",
        title="AI 문체 신호입니다.",
        detail="'시사하는 바'는 보고서식 표현이라 이력서 문장에는 무겁게 보일 수 있습니다.",
    ),
)


def advise_korean_polish(claims: list[Claim]) -> list[Suggestion]:
    suggestions: list[Suggestion] = []
    for claim in claims:
        rule = _first_matching_rule(claim.text)
        if rule is None:
            continue
        suggestions.append(
            Suggestion(
                claim_id=claim.claim_id,
                kind="korean_polish",
                severity="info",
                title=rule.title,
                detail=rule.detail,
                suggested_text=_apply_rule(claim.text, rule),
            ),
        )
    return suggestions


def _first_matching_rule(text: str) -> PolishRule | None:
    for rule in POLISH_RULES:
        if rule.pattern in text:
            return rule
    return None


def _apply_rule(text: str, rule: PolishRule) -> str:
    return text.replace(rule.pattern, rule.replacement).replace("  ", " ").strip()
