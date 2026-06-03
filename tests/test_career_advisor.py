from resume_claim_ledger.career_advisor import advise_career
from resume_claim_ledger.models import Claim


def test_career_advice_flags_broad_unproven_impact_claim() -> None:
    # Given: a broad impact claim without sufficient evidence.
    claims = [
        Claim(
            claim_id="CLM-001",
            text="대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다.",
            category="impact",
            status="too_broad",
            evidence_note="근거 필요",
            suggested_rewrite="MLOps 시스템 구축 작업에 참여했습니다.",
        ),
    ]

    # When: career advice is generated.
    suggestions = advise_career(claims)

    # Then: the claim receives an HR-facing overclaim warning.
    assert len(suggestions) == 1
    assert suggestions[0].claim_id == "CLM-001"
    assert suggestions[0].kind == "career"
    assert suggestions[0].severity == "warning"
    assert "성과 범위" in suggestions[0].title
    assert suggestions[0].suggested_text == "MLOps 시스템 구축 작업에 참여했습니다."


def test_career_advice_does_not_warn_verified_execution_claim() -> None:
    # Given: a verified execution claim with concrete evidence.
    claims = [
        Claim(
            claim_id="CLM-002",
            text="배포 체크리스트를 도입했습니다.",
            category="execution",
            status="verified",
            evidence_note="release checklist",
            suggested_rewrite="",
        ),
    ]

    # When: career advice is generated.
    suggestions = advise_career(claims)

    # Then: evidence-safe verified claims remain quiet.
    assert suggestions == []


def test_career_advice_redacts_sensitive_evidence_details() -> None:
    # Given: an unresolved claim whose evidence note contains an internal URL.
    claims = [
        Claim(
            claim_id="CLM-003",
            text="장애 대응 문서를 정리했습니다.",
            category="execution",
            status="needs_evidence",
            evidence_note="internal: https://corp.example.local/ticket/SEC-123",
            suggested_rewrite="",
        ),
    ]

    # When: career advice is generated.
    suggestions = advise_career(claims)

    # Then: advice does not expose sensitive evidence details.
    rendered = "\n".join(
        f"{suggestion.title}\n{suggestion.detail}\n{suggestion.suggested_text}"
        for suggestion in suggestions
    )
    assert "corp.example" not in rendered
    assert "SEC-123" not in rendered
    assert suggestions[0].severity == "info"
