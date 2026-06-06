from resume_claim_ledger.coordinate_reporter import (
    build_coordinate_json,
    build_coordinate_markdown,
    build_coordinate_summary_markdown,
)
from resume_claim_ledger.models import CoordinateItem, SubmissionPlan


def test_build_coordinate_markdown_groups_summary_warnings_and_actions() -> None:
    # Given: a submission plan with a warning and one action item.
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

    # When: Markdown is rendered.
    markdown = build_coordinate_markdown(plan)

    # Then: summary, warning, and action sections are visible.
    assert "# Submission Plan" in markdown
    assert "## Summary" in markdown
    assert "- ready: 1" in markdown
    assert "## Warnings" in markdown
    assert "- Malformed ledger" in markdown
    assert "### CLM-001" in markdown
    assert "- jd_match: direct_keyword_match" in markdown


def test_build_coordinate_json_outputs_stable_schema_without_absolute_paths() -> None:
    # Given: a submission plan with evidence IDs only.
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
    plan = SubmissionPlan(schema_version=1, items=(item,), warnings=())

    # When: JSON is rendered.
    content = build_coordinate_json(plan)

    # Then: the public schema is stable and does not expose local paths.
    assert '"schema_version": 1' in content
    assert '"claim_id": "CLM-001"' in content
    assert '"matched_evidence": [' in content
    assert '"EVD-001"' in content
    assert "C:/" not in content
    assert content.endswith("\n")


def test_build_coordinate_markdown_omits_warnings_when_none_exist() -> None:
    # Given: a submission plan without warnings.
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
    plan = SubmissionPlan(schema_version=1, items=(item,), warnings=())

    # When: Markdown is rendered.
    markdown = build_coordinate_markdown(plan)

    # Then: empty warning sections are omitted.
    assert "## Warnings" not in markdown
    assert "### CLM-002" in markdown


def test_build_coordinate_summary_markdown_lists_counts_and_non_ready_items_only() -> None:
    # Given: a mixed submission plan with ready and non-ready items.
    ready = CoordinateItem(
        claim_id="CLM-001",
        source_text="Python MLOps 배포 체크리스트를 정리했습니다.",
        action="ready",
        evidence_status="verified",
        requirement_match="direct_keyword_match",
        matched_requirements=("REQ-001",),
        matched_evidence=("EVD-001",),
        next_step="제출 가능 상태입니다.",
    )
    blocker = CoordinateItem(
        claim_id="CLM-002",
        source_text="대규모 사용자를 대상으로 안정적인 시스템을 구축했습니다.",
        action="submission_blocker",
        evidence_status="too_broad",
        requirement_match="direct_keyword_match",
        matched_requirements=("REQ-002",),
        matched_evidence=(),
        next_step="근거를 추가하거나 제출 전 표현을 완화하세요.",
    )
    plan = SubmissionPlan(schema_version=1, items=(ready, blocker), warnings=("Malformed ledger",))

    # When: summary Markdown is rendered.
    markdown = build_coordinate_summary_markdown(plan)

    # Then: counts and non-ready items are visible without full ready-claim detail.
    assert "# Submission Summary" in markdown
    assert "- ready: 1" in markdown
    assert "- submission_blocker: 1" in markdown
    assert "## Warnings" in markdown
    assert "### CLM-002" in markdown
    assert "### CLM-001" not in markdown
    assert "C:/" not in markdown
