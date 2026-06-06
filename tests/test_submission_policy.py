from pathlib import Path

import pytest

from resume_claim_ledger.ledger_io import LedgerReadResult
from resume_claim_ledger.models import Claim
from resume_claim_ledger.submission_policy import (
    PolicyParseError,
    doctor_policy_violations,
    read_submission_policy,
)


def joined_lines(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def test_read_submission_policy_parses_agent_guardrail_file(tmp_path: Path) -> None:
    policy_path = tmp_path / "submission-policy.yml"
    _ = policy_path.write_text(
        joined_lines(
            [
                "submission_policy:",
                "  allow_auto_edit_resume: false",
                "  require_doctor_pass: true",
                "  block_on:",
                "    - malformed_ledger",
                "    - needs_evidence",
                "    - too_broad",
                "  forbidden_claim_changes:",
                "    - add_metric",
                "    - add_employer",
                "    - add_date",
                "    - strengthen_scope",
            ],
        ),
        encoding="utf-8",
    )

    policy = read_submission_policy(policy_path)

    assert policy.allow_auto_edit_resume is False
    assert policy.require_doctor_pass is True
    assert policy.block_on == ("malformed_ledger", "needs_evidence", "too_broad")
    assert policy.forbidden_claim_changes == (
        "add_metric",
        "add_employer",
        "add_date",
        "strengthen_scope",
    )


def test_read_submission_policy_rejects_unknown_blocker(tmp_path: Path) -> None:
    policy_path = tmp_path / "submission-policy.yml"
    _ = policy_path.write_text(
        joined_lines(
            [
                "submission_policy:",
                "  allow_auto_edit_resume: false",
                "  require_doctor_pass: true",
                "  block_on:",
                "    - invented_metric",
                "  forbidden_claim_changes:",
                "    - add_metric",
            ],
        ),
        encoding="utf-8",
    )

    with pytest.raises(PolicyParseError, match="invented_metric"):
        _ = read_submission_policy(policy_path)


def test_doctor_policy_violations_names_blocked_statuses(tmp_path: Path) -> None:
    policy_path = tmp_path / "submission-policy.yml"
    _ = policy_path.write_text(
        joined_lines(
            [
                "submission_policy:",
                "  allow_auto_edit_resume: false",
                "  require_doctor_pass: true",
                "  block_on:",
                "    - malformed_ledger",
                "    - needs_evidence",
                "  forbidden_claim_changes:",
                "    - add_metric",
            ],
        ),
        encoding="utf-8",
    )
    claim = Claim(
        claim_id="CLM-001",
        text="장애 대응 문서를 정리했습니다.",
        category="execution",
        status="needs_evidence",
        evidence_note="문서 링크 필요",
        suggested_rewrite="",
    )
    result = LedgerReadResult(
        claims=[claim],
        warnings=["Malformed ledger shape: expected claims list."],
    )

    violations = doctor_policy_violations(result, read_submission_policy(policy_path))

    assert violations == (
        "malformed_ledger: Malformed ledger shape: expected claims list.",
        "needs_evidence: 1",
    )
