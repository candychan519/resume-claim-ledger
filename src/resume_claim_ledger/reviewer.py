from collections import Counter

from .models import Claim, ClaimStatus


def summarize_statuses(claims: list[Claim]) -> dict[ClaimStatus, int]:
    counts: Counter[ClaimStatus] = Counter(claim.status for claim in claims)
    return {
        "verified": counts["verified"],
        "needs_evidence": counts["needs_evidence"],
        "too_broad": counts["too_broad"],
        "rewrite_needed": counts["rewrite_needed"],
    }
