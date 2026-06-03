from resume_claim_ledger.career_advisor import advise_career
from resume_claim_ledger.models import Claim

claims = [
    Claim(
        claim_id="CLM-001",
        text="대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다.",
        category="impact",
        status="too_broad",
        evidence_note="근거 필요",
        suggested_rewrite="",
    ),
]
print(advise_career(claims)[0].title)
