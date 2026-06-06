import shutil
import subprocess
from pathlib import Path

UV = shutil.which("uv") or "uv"


def joined_lines(lines: list[str]) -> str:
    return "\n".join(lines) + "\n"


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [UV, *args],
        check=False,
        capture_output=True,
        text=True,
    )


def test_scan_review_report_when_run_through_cli(tmp_path: Path) -> None:
    # Given: a markdown resume file and output paths.
    resume = tmp_path / "resume.md"
    ledger = tmp_path / "claims.yml"
    report = tmp_path / "claim-review.md"
    _ = resume.write_text(
        joined_lines(
            [
                "# Resume",
                "- 대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다.",
                "- 배포 체크리스트를 도입했습니다. [evidence: release checklist]",
                "- 장애 대응 문서를 정리했습니다.",
            ],
        ),
        encoding="utf-8",
    )

    # When: the installed CLI surface is exercised through uv.
    scan = run_cli(["run", "resume-ledger", "scan", str(resume), "--out", str(ledger)])
    review = run_cli(["run", "resume-ledger", "review", str(ledger)])
    report_run = run_cli(["run", "resume-ledger", "report", str(ledger), "--out", str(report)])

    # Then: each command succeeds and writes the user-visible report.
    assert scan.returncode == 0
    assert review.returncode == 0
    assert report_run.returncode == 0
    assert "Wrote 3 claims" in scan.stdout
    assert "too_broad" in review.stdout
    assert "too_broad: 1" in report.read_text(encoding="utf-8")


def test_scan_when_resume_has_no_bullets_writes_empty_ledger(tmp_path: Path) -> None:
    # Given: a resume with no bullet claims.
    resume = tmp_path / "resume.md"
    ledger = tmp_path / "claims.yml"
    _ = resume.write_text("# Resume\nNo bullet claims yet.\n", encoding="utf-8")

    # When: scan runs through the CLI.
    result = run_cli(["run", "resume-ledger", "scan", str(resume), "--out", str(ledger)])

    # Then: it succeeds and writes a versioned empty ledger.
    assert result.returncode == 0
    assert "Wrote 0 claims" in result.stdout
    assert "schema_version: 1" in ledger.read_text(encoding="utf-8")


def test_report_when_ledger_is_malformed_does_not_crash(tmp_path: Path) -> None:
    # Given: a malformed ledger file.
    ledger = tmp_path / "malformed.yml"
    report = tmp_path / "report.md"
    _ = ledger.write_text("not_claims:\n  - broken\n", encoding="utf-8")

    # When: report runs through the CLI.
    result = run_cli(["run", "resume-ledger", "report", str(ledger), "--out", str(report)])

    # Then: it exits cleanly and makes the warning visible.
    assert result.returncode == 0
    assert "Malformed ledger" in report.read_text(encoding="utf-8")


def test_scan_when_resume_file_is_missing_exits_nonzero(tmp_path: Path) -> None:
    # Given: a missing resume path.
    missing = tmp_path / "missing.md"
    ledger = tmp_path / "claims.yml"

    # When: scan runs through the CLI.
    result = run_cli(["run", "resume-ledger", "scan", str(missing), "--out", str(ledger)])

    # Then: it exits non-zero with a user-readable missing-file error.
    assert result.returncode != 0
    assert "does not exist" in result.stderr


def test_report_strict_mode_when_unverified_claims_exist_exits_nonzero(tmp_path: Path) -> None:
    # Given: a ledger with unresolved claims.
    ledger = tmp_path / "claims.yml"
    report = tmp_path / "report.md"
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "장애 대응 문서를 정리했습니다."',
                "    category: execution",
                "    status: needs_evidence",
                '    evidence_note: "구체적인 근거가 필요합니다."',
                '    suggested_rewrite: ""',
            ],
        ),
        encoding="utf-8",
    )

    # When: strict report runs through the CLI.
    result = run_cli(
        ["run", "resume-ledger", "report", str(ledger), "--out", str(report), "--strict"],
    )

    # Then: strict mode blocks unresolved claim statuses.
    assert result.returncode != 0
    assert "needs_evidence" in result.stderr


def test_doctor_when_ledger_is_submission_ready_exits_zero(tmp_path: Path) -> None:
    # Given: a ledger with only verified claims.
    ledger = tmp_path / "claims.yml"
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "배포 체크리스트를 정리했습니다."',
                "    category: execution",
                "    status: verified",
                '    evidence_note: "release checklist"',
                '    suggested_rewrite: ""',
            ],
        ),
        encoding="utf-8",
    )

    # When: doctor runs through the CLI.
    result = run_cli(["run", "resume-ledger", "doctor", str(ledger)])

    # Then: it passes the submission readiness check.
    assert result.returncode == 0
    assert "Ready for submission" in result.stdout
    assert "verified" in result.stdout


def test_doctor_with_policy_when_ledger_is_ready_exits_zero(tmp_path: Path) -> None:
    # Given: a verified ledger and a policy that requires doctor to pass.
    ledger = tmp_path / "claims.yml"
    policy = tmp_path / "submission-policy.yml"
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "배포 체크리스트를 정리했습니다."',
                "    category: execution",
                "    status: verified",
                '    evidence_note: "release checklist"',
                '    suggested_rewrite: ""',
            ],
        ),
        encoding="utf-8",
    )
    _ = policy.write_text(
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

    # When: doctor runs with the policy gate.
    result = run_cli(["run", "resume-ledger", "doctor", str(ledger), "--policy", str(policy)])

    # Then: both the default doctor and policy gate pass.
    assert result.returncode == 0
    assert "Ready for submission" in result.stdout
    assert "Policy checks passed" in result.stdout


def test_doctor_when_unresolved_claims_exist_exits_nonzero(tmp_path: Path) -> None:
    # Given: a ledger with unresolved claim statuses.
    ledger = tmp_path / "claims.yml"
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "대규모 사용자를 대상으로 시스템을 구축했습니다."',
                "    category: impact",
                "    status: too_broad",
                '    evidence_note: "근거 필요"',
                '    suggested_rewrite: "시스템 구축 작업에 참여했습니다."',
                "  - claim_id: CLM-002",
                '    text: "장애 대응 문서를 정리했습니다."',
                "    category: execution",
                "    status: needs_evidence",
                '    evidence_note: "문서 링크 필요"',
                '    suggested_rewrite: ""',
            ],
        ),
        encoding="utf-8",
    )

    # When: doctor runs through the CLI.
    result = run_cli(["run", "resume-ledger", "doctor", str(ledger)])

    # Then: it blocks submission and names the unresolved statuses.
    assert result.returncode != 0
    assert "Doctor found unresolved claims" in result.stderr
    assert "needs_evidence" in result.stderr
    assert "too_broad" in result.stderr


def test_doctor_with_policy_when_blocked_status_exists_exits_nonzero(tmp_path: Path) -> None:
    # Given: a policy that blocks unresolved evidence gaps.
    ledger = tmp_path / "claims.yml"
    policy = tmp_path / "submission-policy.yml"
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "장애 대응 문서를 정리했습니다."',
                "    category: execution",
                "    status: needs_evidence",
                '    evidence_note: "문서 링크 필요"',
                '    suggested_rewrite: ""',
            ],
        ),
        encoding="utf-8",
    )
    _ = policy.write_text(
        joined_lines(
            [
                "submission_policy:",
                "  allow_auto_edit_resume: false",
                "  require_doctor_pass: true",
                "  block_on:",
                "    - needs_evidence",
                "  forbidden_claim_changes:",
                "    - add_metric",
            ],
        ),
        encoding="utf-8",
    )

    # When: doctor runs with the policy gate.
    result = run_cli(["run", "resume-ledger", "doctor", str(ledger), "--policy", str(policy)])

    # Then: it names the policy violation.
    assert result.returncode != 0
    assert "Policy blocked submission" in result.stderr
    assert "needs_evidence: 1" in result.stderr


def test_doctor_with_policy_when_policy_file_is_missing_exits_nonzero(tmp_path: Path) -> None:
    # Given: a verified ledger and a missing policy file.
    ledger = tmp_path / "claims.yml"
    missing_policy = tmp_path / "missing-policy.yml"
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "배포 체크리스트를 정리했습니다."',
                "    category: execution",
                "    status: verified",
                '    evidence_note: "release checklist"',
                '    suggested_rewrite: ""',
            ],
        ),
        encoding="utf-8",
    )

    # When: doctor runs with a missing policy path.
    result = run_cli(
        ["run", "resume-ledger", "doctor", str(ledger), "--policy", str(missing_policy)],
    )

    # Then: it fails before pretending the policy was applied.
    assert result.returncode != 0
    assert "Policy file does not exist" in result.stderr


def test_doctor_when_ledger_is_malformed_exits_nonzero(tmp_path: Path) -> None:
    # Given: a malformed ledger file.
    ledger = tmp_path / "malformed.yml"
    _ = ledger.write_text("not_claims:\n  - broken\n", encoding="utf-8")

    # When: doctor runs through the CLI.
    result = run_cli(["run", "resume-ledger", "doctor", str(ledger)])

    # Then: it blocks submission and surfaces the ledger warning.
    assert result.returncode != 0
    assert "Malformed ledger" in result.stderr


def test_doctor_when_ledger_file_is_missing_exits_nonzero(tmp_path: Path) -> None:
    # Given: a missing ledger path.
    missing = tmp_path / "missing.yml"

    # When: doctor runs through the CLI.
    result = run_cli(["run", "resume-ledger", "doctor", str(missing)])

    # Then: it exits non-zero with a user-readable missing-file error.
    assert result.returncode != 0
    assert "Ledger file does not exist" in result.stderr


def test_advise_writes_career_and_korean_polish_report(tmp_path: Path) -> None:
    # Given: a ledger with an unresolved Korean claim.
    ledger = tmp_path / "claims.yml"
    advice = tmp_path / "advice.md"
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "배포 자동화를 통해 처리 시간을 30% 개선했습니다."',
                "    category: impact",
                "    status: too_broad",
                '    evidence_note: "근거 필요"',
                '    suggested_rewrite: "배포 자동화로 처리 시간을 30% 개선했습니다."',
            ],
        ),
        encoding="utf-8",
    )

    # When: career advice runs through the CLI.
    result = run_cli(["run", "resume-ledger", "advise", str(ledger), "--out", str(advice)])

    # Then: markdown advice contains both advice sections.
    content = advice.read_text(encoding="utf-8")
    assert result.returncode == 0
    assert "## Career Review" in content
    assert "## Korean Polish" in content


def test_advise_when_no_suggestions_writes_calm_report(tmp_path: Path) -> None:
    # Given: a verified plain claim.
    ledger = tmp_path / "claims.yml"
    advice = tmp_path / "advice.md"
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "배포 체크리스트를 정리했습니다."',
                "    category: execution",
                "    status: verified",
                '    evidence_note: "release checklist"',
                '    suggested_rewrite: ""',
            ],
        ),
        encoding="utf-8",
    )

    # When: career advice runs through the CLI.
    result = run_cli(["run", "resume-ledger", "advise", str(ledger), "--out", str(advice)])

    # Then: the report succeeds without noisy empty sections.
    content = advice.read_text(encoding="utf-8")
    assert result.returncode == 0
    assert "No career or Korean polish suggestions found." in content
    assert "## Career Review" not in content


def test_advise_json_outputs_stable_suggestion_contract(tmp_path: Path) -> None:
    # Given: a ledger with an unresolved Korean claim.
    ledger = tmp_path / "claims.yml"
    advice = tmp_path / "advice.json"
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "대규모 사용자를 대상으로 안정적인 MLOps 시스템을 구축했습니다."',
                "    category: impact",
                "    status: too_broad",
                '    evidence_note: "근거 필요"',
                '    suggested_rewrite: "MLOps 시스템 구축 작업에 참여했습니다."',
            ],
        ),
        encoding="utf-8",
    )

    # When: JSON advice runs through the CLI.
    result = run_cli(
        ["run", "resume-ledger", "advise", str(ledger), "--out", str(advice), "--format", "json"],
    )

    # Then: the output exposes the stable machine-readable contract.
    payload = advice.read_text(encoding="utf-8")
    assert result.returncode == 0
    assert '"schema_version": 1' in payload
    assert '"claim_id": "CLM-001"' in payload
    assert '"kind": "career"' in payload
