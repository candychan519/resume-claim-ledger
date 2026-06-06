from resume_claim_ledger.models import (
    CoordinateItem,
    SubmissionPlan,
    coordinate_item_to_dict,
    submission_plan_to_dict,
)


def test_submission_plan_to_dict_exposes_stable_coordinate_json_contract() -> None:
    # Given: a submission plan with one coordinate action.
    item = CoordinateItem(
        claim_id="CLM-001",
        source_text="Python MLOps 배포 체크리스트를 정리했습니다.",
        action="ready",
        evidence_status="verified",
        requirement_match="direct_keyword_match",
        matched_requirements=("REQ-001",),
        matched_evidence=("EVD-001",),
        next_step="제출 가능 상태입니다.",
    )
    plan = SubmissionPlan(schema_version=1, items=(item,), warnings=("Malformed ledger",))

    # When: the plan is converted for JSON output.
    result = submission_plan_to_dict(plan)

    # Then: the public Coordinate JSON contract is stable and list based.
    assert result == {
        "schema_version": 1,
        "items": [
            {
                "claim_id": "CLM-001",
                "source_text": "Python MLOps 배포 체크리스트를 정리했습니다.",
                "action": "ready",
                "evidence_status": "verified",
                "requirement_match": "direct_keyword_match",
                "matched_requirements": ["REQ-001"],
                "matched_evidence": ["EVD-001"],
                "next_step": "제출 가능 상태입니다.",
            },
        ],
        "warnings": ["Malformed ledger"],
    }


def test_coordinate_item_preserves_source_claim_reference() -> None:
    # Given: a coordinate item produced from a claim.
    item = CoordinateItem(
        claim_id="CLM-002",
        source_text="장애 대응 문서를 정리했습니다.",
        action="needs_evidence",
        evidence_status="needs_evidence",
        requirement_match="not_evaluated",
        matched_requirements=(),
        matched_evidence=(),
        next_step="증거 파일을 연결하세요.",
    )

    # When: callers inspect and serialize the item.
    result = coordinate_item_to_dict(item)

    # Then: the source claim reference and text are preserved.
    assert item.claim_id == "CLM-002"
    assert result["claim_id"] == "CLM-002"
    assert result["source_text"] == "장애 대응 문서를 정리했습니다."
