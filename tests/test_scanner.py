from resume_claim_ledger.scanner import extract_claims


def test_extract_claims_when_resume_has_markdown_bullets() -> None:
    # Given: a resume section with headings, bullets, blank lines, and prose.
    markdown = """
# Resume

Summary paragraph should not become a claim.

## Projects
- 대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다.
- 배포 체크리스트를 도입해 릴리스 누락을 줄였습니다. [evidence: release checklist]
"""

    # When: claims are extracted from the markdown.
    claims = extract_claims(markdown)

    # Then: only bullet claims are captured and classified.
    assert [claim.claim_id for claim in claims] == ["CLM-001", "CLM-002"]
    assert claims[0].text == "대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다."
    assert claims[0].status == "too_broad"
    assert claims[0].evidence_note == "범위나 판단 기준을 뒷받침할 근거가 필요합니다."
    assert claims[0].suggested_rewrite == "MLOps 시스템 구축 작업에 참여했습니다."
    assert claims[1].status == "verified"
    assert claims[1].evidence_note == "release checklist"
