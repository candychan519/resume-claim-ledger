from dataclasses import dataclass
from typing import Literal, TypedDict

ClaimStatus = Literal["verified", "needs_evidence", "too_broad", "rewrite_needed"]
ClaimCategory = Literal["impact", "execution", "scope"]
SuggestionKind = Literal["career", "korean_polish"]
SuggestionSeverity = Literal["info", "warning", "critical"]


class SuggestionDict(TypedDict):
    claim_id: str
    kind: SuggestionKind
    severity: SuggestionSeverity
    title: str
    detail: str
    suggested_text: str


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


def suggestion_to_dict(suggestion: Suggestion) -> SuggestionDict:
    return {
        "claim_id": suggestion.claim_id,
        "kind": suggestion.kind,
        "severity": suggestion.severity,
        "title": suggestion.title,
        "detail": suggestion.detail,
        "suggested_text": suggestion.suggested_text,
    }
