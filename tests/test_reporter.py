from resume_claim_ledger.models import Claim
from resume_claim_ledger.reporter import build_report


def test_build_report_when_claims_have_mixed_statuses() -> None:
    # Given: a ledger with one broad claim and one verified claim.
    claims = [
        Claim(
            claim_id="CLM-001",
            text="대규모 사용자를 대상으로 안정적인 시스템을 구축했습니다.",
            category="impact",
            status="too_broad",
            evidence_note="범위나 판단 기준을 뒷받침할 근거가 필요합니다.",
            suggested_rewrite="시스템 구축 작업에 참여했습니다.",
        ),
        Claim(
            claim_id="CLM-002",
            text="배포 체크리스트를 도입했습니다.",
            category="execution",
            status="verified",
            evidence_note="release checklist",
            suggested_rewrite="",
        ),
    ]

    # When: a markdown report is built.
    report = build_report(claims)

    # Then: the report contains summary counts and actionable details.
    assert "too_broad: 1" in report
    assert "verified: 1" in report
    assert "CLM-001" in report
    assert "범위나 판단 기준" in report
    assert "시스템 구축 작업에 참여했습니다." in report
