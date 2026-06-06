from dataclasses import dataclass
from typing import Literal, TypedDict

ClaimStatus = Literal["verified", "needs_evidence", "too_broad", "rewrite_needed"]
ClaimCategory = Literal["impact", "execution", "scope"]
SuggestionKind = Literal["career", "korean_polish"]
SuggestionSeverity = Literal["info", "warning", "critical"]
CoordinateAction = Literal[
    "ready",
    "needs_evidence",
    "soften_wording",
    "jd_gap",
    "submission_blocker",
]
RequirementMatch = Literal[
    "direct_keyword_match",
    "weak_keyword_match",
    "no_match",
    "not_evaluated",
]


class SuggestionDict(TypedDict):
    claim_id: str
    kind: SuggestionKind
    severity: SuggestionSeverity
    title: str
    detail: str
    suggested_text: str


class CoordinateItemDict(TypedDict):
    claim_id: str
    source_text: str
    action: CoordinateAction
    evidence_status: ClaimStatus
    requirement_match: RequirementMatch
    matched_requirements: list[str]
    matched_evidence: list[str]
    next_step: str


class SubmissionPlanDict(TypedDict):
    schema_version: int
    items: list[CoordinateItemDict]
    warnings: list[str]


@dataclass(frozen=True, slots=True)
class Claim:
    claim_id: str
    text: str
    category: ClaimCategory
    status: ClaimStatus
    evidence_note: str
    suggested_rewrite: str


@dataclass(frozen=True, slots=True)
class Suggestion:
    claim_id: str
    kind: SuggestionKind
    severity: SuggestionSeverity
    title: str
    detail: str
    suggested_text: str


@dataclass(frozen=True, slots=True)
class JobRequirement:
    requirement_id: str
    text: str
    keywords: tuple[str, ...]
    required: bool


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    evidence_id: str
    display_name: str
    summary: str


@dataclass(frozen=True, slots=True)
class CoordinateItem:
    claim_id: str
    source_text: str
    action: CoordinateAction
    evidence_status: ClaimStatus
    requirement_match: RequirementMatch
    matched_requirements: tuple[str, ...]
    matched_evidence: tuple[str, ...]
    next_step: str


@dataclass(frozen=True, slots=True)
class SubmissionPlan:
    schema_version: int
    items: tuple[CoordinateItem, ...]
    warnings: tuple[str, ...]


def suggestion_to_dict(suggestion: Suggestion) -> SuggestionDict:
    return {
        "claim_id": suggestion.claim_id,
        "kind": suggestion.kind,
        "severity": suggestion.severity,
        "title": suggestion.title,
        "detail": suggestion.detail,
        "suggested_text": suggestion.suggested_text,
    }


def coordinate_item_to_dict(item: CoordinateItem) -> CoordinateItemDict:
    return {
        "claim_id": item.claim_id,
        "source_text": item.source_text,
        "action": item.action,
        "evidence_status": item.evidence_status,
        "requirement_match": item.requirement_match,
        "matched_requirements": list(item.matched_requirements),
        "matched_evidence": list(item.matched_evidence),
        "next_step": item.next_step,
    }


def submission_plan_to_dict(plan: SubmissionPlan) -> SubmissionPlanDict:
    return {
        "schema_version": plan.schema_version,
        "items": [coordinate_item_to_dict(item) for item in plan.items],
        "warnings": list(plan.warnings),
    }
