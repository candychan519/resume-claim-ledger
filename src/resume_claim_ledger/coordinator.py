import re
from typing import Final

from .models import (
    Claim,
    CoordinateAction,
    CoordinateItem,
    EvidenceItem,
    JobRequirement,
    RequirementMatch,
    SubmissionPlan,
)

TOKEN_PATTERN: Final = re.compile(r"[A-Za-z][A-Za-z0-9.+#-]*|[가-힣]{2,}")
SUBMISSION_PLAN_SCHEMA_VERSION: Final = 1


def coordinate_submission(
    claims: list[Claim],
    requirements: list[JobRequirement],
    evidence: list[EvidenceItem],
    warnings: list[str],
) -> SubmissionPlan:
    return SubmissionPlan(
        schema_version=SUBMISSION_PLAN_SCHEMA_VERSION,
        items=tuple(_coordinate_claim(claim, requirements, evidence) for claim in claims),
        warnings=tuple(warnings),
    )


def _coordinate_claim(
    claim: Claim,
    requirements: list[JobRequirement],
    evidence: list[EvidenceItem],
) -> CoordinateItem:
    matched_evidence = _matched_evidence_ids(claim, evidence)
    requirement_match, matched_requirements = _match_requirements(
        claim,
        requirements,
        evidence,
        matched_evidence,
    )
    action = _action_for_claim(claim, matched_evidence, matched_requirements, requirements)
    return CoordinateItem(
        claim_id=claim.claim_id,
        source_text=claim.text,
        action=action,
        evidence_status=claim.status,
        requirement_match=requirement_match,
        matched_requirements=matched_requirements,
        matched_evidence=matched_evidence,
        next_step=_next_step_for_action(action),
    )


def _matched_evidence_ids(claim: Claim, evidence: list[EvidenceItem]) -> tuple[str, ...]:
    claim_tokens = _tokens(f"{claim.text} {claim.evidence_note}")
    return tuple(
        item.evidence_id
        for item in evidence
        if claim_tokens.intersection(_tokens(f"{item.display_name} {item.summary}"))
    )


def _match_requirements(
    claim: Claim,
    requirements: list[JobRequirement],
    evidence: list[EvidenceItem],
    matched_evidence: tuple[str, ...],
) -> tuple[RequirementMatch, tuple[str, ...]]:
    if requirements == []:
        return "not_evaluated", ()

    claim_tokens = _tokens(claim.text)
    direct_matches = tuple(
        requirement.requirement_id
        for requirement in requirements
        if _keywords_match(requirement.keywords, claim_tokens)
    )
    if direct_matches != ():
        return "direct_keyword_match", direct_matches

    evidence_tokens = _tokens(" ".join(_matched_evidence_summaries(evidence, matched_evidence)))
    weak_matches = tuple(
        requirement.requirement_id
        for requirement in requirements
        if _keywords_match(requirement.keywords, evidence_tokens)
    )
    if weak_matches != ():
        return "weak_keyword_match", weak_matches

    return "no_match", ()


def _matched_evidence_summaries(
    evidence: list[EvidenceItem],
    matched_evidence: tuple[str, ...],
) -> tuple[str, ...]:
    matched = set(matched_evidence)
    return tuple(item.summary for item in evidence if item.evidence_id in matched)


def _keywords_match(keywords: tuple[str, ...], tokens: set[str]) -> bool:
    return any(keyword.casefold() in tokens for keyword in keywords)


def _action_for_claim(
    claim: Claim,
    matched_evidence: tuple[str, ...],
    matched_requirements: tuple[str, ...],
    requirements: list[JobRequirement],
) -> CoordinateAction:
    match claim.status:
        case "too_broad" | "rewrite_needed":
            if matched_evidence == ():
                return "submission_blocker"
            return "soften_wording"
        case "needs_evidence":
            return "needs_evidence"
        case "verified":
            if requirements != [] and not _has_required_match(requirements, matched_requirements):
                return "jd_gap"
            return "ready"


def _has_required_match(
    requirements: list[JobRequirement],
    matched_requirements: tuple[str, ...],
) -> bool:
    matched = set(matched_requirements)
    return any(
        requirement.required and requirement.requirement_id in matched
        for requirement in requirements
    )


def _next_step_for_action(action: CoordinateAction) -> str:
    match action:
        case "ready":
            return "제출 가능 상태입니다."
        case "needs_evidence":
            return "근거 파일을 연결하세요."
        case "soften_wording":
            return "근거를 확인하고 제안 표현으로 완화하세요."
        case "jd_gap":
            return "JD 요구사항과 연결되는 경험인지 확인하세요."
        case "submission_blocker":
            return "근거를 추가하거나 제출 전 표현을 완화하세요."


def _tokens(text: str) -> set[str]:
    return {match.group(0).casefold() for match in TOKEN_PATTERN.finditer(text)}
