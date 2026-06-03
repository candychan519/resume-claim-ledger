import re
from collections.abc import Sequence
from typing import Final

from .models import Claim

EVIDENCE_PATTERN: Final = re.compile(r"\[evidence:\s*(?P<note>[^\]]+)\]", re.IGNORECASE)
BROAD_TERMS: Final[tuple[str, ...]] = (
    "대규모",
    "안정적인",
    "최적화",
    "개선했습니다",
    "향상",
    "large-scale",
    "stable",
    "improved",
    "optimized",
)


def extract_claims(markdown: str) -> list[Claim]:
    bullet_texts = [_clean_bullet(line) for line in markdown.splitlines()]
    claims: list[Claim] = []

    for text in [text for text in bullet_texts if text != ""]:
        claim_number = len(claims) + 1
        claims.append(_classify_claim(f"CLM-{claim_number:03}", text))

    return claims


def _clean_bullet(line: str) -> str:
    stripped = line.strip()
    if not stripped.startswith(("- ", "* ")):
        return ""
    return stripped[2:].strip()


def _classify_claim(claim_id: str, text: str) -> Claim:
    evidence_match = EVIDENCE_PATTERN.search(text)
    if evidence_match is not None:
        evidence_note = evidence_match.group("note").strip()
        clean_text = EVIDENCE_PATTERN.sub("", text).strip()
        return Claim(
            claim_id=claim_id,
            text=clean_text,
            category="execution",
            status="verified",
            evidence_note=evidence_note,
            suggested_rewrite="",
        )

    if _has_broad_term(text, BROAD_TERMS):
        return Claim(
            claim_id=claim_id,
            text=text,
            category="impact",
            status="too_broad",
            evidence_note="범위나 판단 기준을 뒷받침할 근거가 필요합니다.",
            suggested_rewrite=_safer_rewrite(text),
        )

    return Claim(
        claim_id=claim_id,
        text=text,
        category="execution",
        status="needs_evidence",
        evidence_note="구체적인 근거, 지표, 산출물 링크 중 하나가 필요합니다.",
        suggested_rewrite="",
    )


def _has_broad_term(text: str, terms: Sequence[str]) -> bool:
    lowered = text.casefold()
    return any(term.casefold() in lowered for term in terms)


def _safer_rewrite(text: str) -> str:
    rewritten = text
    replacements: Final[tuple[tuple[str, str], ...]] = (
        ("대규모 사용자를 대상으로 ", ""),
        ("안정적인 ", ""),
        ("구축했습니다", "구축 작업에 참여했습니다"),
        ("시스템을 구축 작업", "시스템 구축 작업"),
        ("개선했습니다", "개선 작업에 참여했습니다"),
        ("improved", "contributed to improving"),
        ("optimized", "worked on optimizing"),
    )
    for source, target in replacements:
        rewritten = rewritten.replace(source, target)
    return rewritten
