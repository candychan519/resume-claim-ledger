from resume_claim_ledger.korean_polish import advise_korean_polish
from resume_claim_ledger.models import Claim


def test_polish_flags_through_phrase_without_changing_numbers() -> None:
    # Given: a Korean claim with an AI-sounding through phrase and a metric.
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

    # When: Korean polish advice is generated.
    suggestions = advise_korean_polish(claims)

    # Then: the suggestion explains the pattern and preserves the metric.
    assert len(suggestions) == 1
    assert suggestions[0].claim_id == "CLM-001"
    assert suggestions[0].kind == "korean_polish"
    assert "를 통해" in suggestions[0].detail
    assert "30%" in suggestions[0].suggested_text


def test_polish_returns_no_suggestion_for_plain_specific_sentence() -> None:
    # Given: a specific Korean claim without configured polish patterns.
    claims = [
        Claim(
            claim_id="CLM-002",
            text="배포 체크리스트를 정리하고 팀에 공유했습니다.",
            category="execution",
            status="verified",
            evidence_note="release checklist",
            suggested_rewrite="",
        ),
    ]

    # When: Korean polish advice is generated.
    suggestions = advise_korean_polish(claims)

    # Then: specific plain wording stays quiet.
    assert suggestions == []


def test_polish_preserves_quoted_phrases() -> None:
    # Given: a claim with a quoted proper phrase.
    claims = [
        Claim(
            claim_id="CLM-003",
            text='"릴리스 안정성" 개선을 통해 장애 대응 시간을 줄였습니다.',
            category="impact",
            status="needs_evidence",
            evidence_note="근거 필요",
            suggested_rewrite="",
        ),
    ]

    # When: Korean polish advice is generated.
    suggestions = advise_korean_polish(claims)

    # Then: the quoted phrase is preserved in the safer suggestion.
    assert len(suggestions) == 1
    assert '"릴리스 안정성"' in suggestions[0].suggested_text
