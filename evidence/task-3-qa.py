from resume_claim_ledger.korean_polish import advise_korean_polish
from resume_claim_ledger.models import Claim

claims = [
    Claim(
        claim_id="CLM-001",
        text="배포 자동화를 통해 처리 시간을 30% 개선했습니다.",
        category="impact",
        status="needs_evidence",
        evidence_note="근거 필요",
        suggested_rewrite="",
    ),
]
suggestion = advise_korean_polish(claims)[0]
print(suggestion.detail)
print(suggestion.suggested_text)
