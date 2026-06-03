from resume_claim_ledger.models import Suggestion, suggestion_to_dict


def test_suggestion_model_preserves_claim_reference() -> None:
    # Given: a career suggestion linked to a claim.
    suggestion = Suggestion(
        claim_id="CLM-001",
        kind="career",
        severity="warning",
        title="성과 범위가 넓습니다.",
        detail="근거가 약한 성과 주장은 과장으로 읽힐 수 있습니다.",
        suggested_text="MLOps 시스템 구축 작업에 참여했습니다.",
    )

    # When: the suggestion is inspected by callers.
    # Then: the original claim reference and suggestion kind are stable.
    assert suggestion.claim_id == "CLM-001"
    assert suggestion.kind == "career"


def test_suggestion_to_dict_exposes_stable_output_contract() -> None:
    # Given: a Korean polish suggestion.
    suggestion = Suggestion(
        claim_id="CLM-002",
        kind="korean_polish",
        severity="info",
        title="번역투 표현입니다.",
        detail="'를 통해' 표현이 반복되면 AI 문체처럼 읽힐 수 있습니다.",
        suggested_text="배포 자동화로 처리 시간을 30% 개선했습니다.",
    )

    # When: it is converted for JSON output.
    result = suggestion_to_dict(suggestion)

    # Then: every public output field is present with string values.
    assert result == {
        "claim_id": "CLM-002",
        "kind": "korean_polish",
        "severity": "info",
        "title": "번역투 표현입니다.",
        "detail": "'를 통해' 표현이 반복되면 AI 문체처럼 읽힐 수 있습니다.",
        "suggested_text": "배포 자동화로 처리 시간을 30% 개선했습니다.",
    }
