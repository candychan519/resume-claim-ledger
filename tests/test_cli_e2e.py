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
