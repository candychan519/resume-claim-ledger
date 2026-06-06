from resume_claim_ledger.coordinator import coordinate_submission
from resume_claim_ledger.models import Claim, EvidenceItem, JobRequirement


def test_coordinate_submission_marks_verified_claim_ready_when_evidence_and_required_jd_match(
) -> None:
    # Given: a verified claim with matching JD keywords and matching evidence.
    claims = [
        Claim(
            claim_id="CLM-001",
            text="Python MLOps 배포 체크리스트를 정리했습니다.",
            category="execution",
            status="verified",
            evidence_note="release checklist",
            suggested_rewrite="",
        ),
    ]
    requirements = [
        JobRequirement("REQ-001", "Python MLOps 운영", ("Python", "MLOps"), required=True),
    ]
    evidence = [EvidenceItem("EVD-001", "release.md", "release checklist")]

    # When: a submission plan is coordinated.
    plan = coordinate_submission(claims, requirements, evidence, [])

    # Then: the claim is ready and cites the matched requirement and evidence IDs.
    assert plan.items[0].action == "ready"
    assert plan.items[0].requirement_match == "direct_keyword_match"
    assert plan.items[0].matched_requirements == ("REQ-001",)
    assert plan.items[0].matched_evidence == ("EVD-001",)


def test_coordinate_submission_marks_unresolved_claim_as_submission_blocker_when_evidence_is_missing(  # noqa: E501
) -> None:
    # Given: a broad unresolved claim without matching evidence.
    claims = [
        Claim(
            claim_id="CLM-002",
            text="대규모 사용자를 대상으로 안정적인 시스템을 구축했습니다.",
            category="impact",
            status="too_broad",
            evidence_note="근거 필요",
            suggested_rewrite="시스템 구축 작업에 참여했습니다.",
        ),
    ]

    # When: a submission plan is coordinated without evidence.
    plan = coordinate_submission(claims, [], [], [])

    # Then: the claim blocks submission instead of being strengthened.
    assert plan.items[0].action == "submission_blocker"
    assert plan.items[0].matched_evidence == ()
    assert "근거" in plan.items[0].next_step


def test_coordinate_submission_when_no_job_requirements_uses_not_evaluated() -> None:
    # Given: a claim and evidence but no job description requirements.
    claims = [
        Claim(
            claim_id="CLM-003",
            text="장애 대응 문서를 정리했습니다.",
            category="execution",
            status="needs_evidence",
            evidence_note="incident note",
            suggested_rewrite="",
        ),
    ]
    evidence = [EvidenceItem("EVD-001", "incident.md", "incident note")]

    # When: a submission plan is coordinated.
    plan = coordinate_submission(claims, [], evidence, [])

    # Then: JD matching is explicitly not evaluated.
    assert plan.items[0].requirement_match == "not_evaluated"
    assert plan.items[0].matched_requirements == ()


def test_coordinate_submission_does_not_expose_absolute_evidence_paths() -> None:
    # Given: evidence with a path-like display name.
    claims = [
        Claim(
            claim_id="CLM-004",
            text="release checklist를 정리했습니다.",
            category="execution",
            status="verified",
            evidence_note="release checklist",
            suggested_rewrite="",
        ),
    ]
    evidence = [EvidenceItem("EVD-001", "C:/secret/release.md", "release checklist")]

    # When: a submission plan is coordinated.
    plan = coordinate_submission(claims, [], evidence, [])

    # Then: only evidence IDs are exposed from the coordinator.
    assert plan.items[0].matched_evidence == ("EVD-001",)
    assert "C:/secret" not in plan.items[0].next_step


def test_coordinate_submission_marks_verified_claim_as_jd_gap_when_only_preferred_matches(
) -> None:
    # Given: a verified claim that matches a preferred requirement but not a required one.
    claims = [
        Claim(
            claim_id="CLM-005",
            text="Kubernetes 운영 자동화를 정리했습니다.",
            category="execution",
            status="verified",
            evidence_note="automation note",
            suggested_rewrite="",
        ),
    ]
    requirements = [
        JobRequirement("REQ-001", "Python MLOps 운영", ("Python", "MLOps"), required=True),
        JobRequirement("REQ-002", "Kubernetes 운영", ("Kubernetes", "운영"), required=False),
    ]
    evidence = [EvidenceItem("EVD-001", "automation.md", "automation note")]

    # When: a submission plan is coordinated.
    plan = coordinate_submission(claims, requirements, evidence, [])

    # Then: preferred-only matching does not satisfy the required JD coverage gate.
    assert plan.items[0].action == "jd_gap"
    assert plan.items[0].requirement_match == "direct_keyword_match"
    assert plan.items[0].matched_requirements == ("REQ-002",)
