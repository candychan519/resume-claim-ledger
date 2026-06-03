from dataclasses import dataclass
from typing import Literal

ClaimStatus = Literal["verified", "needs_evidence", "too_broad", "rewrite_needed"]
ClaimCategory = Literal["impact", "execution", "scope"]


@dataclass(frozen=True, slots=True)
class Claim:
    claim_id: str
    text: str
    category: ClaimCategory
    status: ClaimStatus
    evidence_note: str
    suggested_rewrite: str
