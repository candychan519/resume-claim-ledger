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


def test_coordinate_writes_markdown_submission_plan_with_job_and_evidence(
    tmp_path: Path,
) -> None:
    # Given: a claim ledger, job description, and evidence directory.
    ledger = tmp_path / "claims.yml"
    job = tmp_path / "jd.md"
    evidence_dir = tmp_path / "evidence"
    out = tmp_path / "submission-plan.md"
    evidence_dir.mkdir()
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "Python MLOps 배포 체크리스트를 정리했습니다."',
                "    category: execution",
                "    status: verified",
                '    evidence_note: "release checklist"',
                '    suggested_rewrite: ""',
            ],
        ),
        encoding="utf-8",
    )
    _ = job.write_text("## 필수\n- Python MLOps 운영\n", encoding="utf-8")
    _ = (evidence_dir / "release.md").write_text("# release checklist\n", encoding="utf-8")

    # When: coordinate runs through the CLI.
    result = run_cli(
        [
            "run",
            "resume-ledger",
            "coordinate",
            str(ledger),
            "--job",
            str(job),
            "--evidence-dir",
            str(evidence_dir),
            "--out",
            str(out),
        ],
    )

    # Then: a Markdown submission plan is written.
    content = out.read_text(encoding="utf-8")
    assert result.returncode == 0
    assert "Wrote submission plan" in result.stdout
    assert "# Submission Plan" in content
    assert "### CLM-001" in content
    assert "- action: ready" in content
    assert "- jd_match: direct_keyword_match" in content
    assert "- evidence: EVD-001" in content


def test_coordinate_json_outputs_stable_contract(tmp_path: Path) -> None:
    # Given: a ledger with an unresolved claim.
    ledger = tmp_path / "claims.yml"
    out = tmp_path / "submission-plan.json"
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

    # When: coordinate writes JSON through the CLI.
    result = run_cli(
        [
            "run",
            "resume-ledger",
            "coordinate",
            str(ledger),
            "--format",
            "json",
            "--out",
            str(out),
        ],
    )

    # Then: the Coordinate JSON contract is visible.
    content = out.read_text(encoding="utf-8")
    assert result.returncode == 0
    assert '"schema_version": 1' in content
    assert '"items": [' in content
    assert '"claim_id": "CLM-001"' in content
    assert '"action": "needs_evidence"' in content


def test_coordinate_when_job_is_omitted_still_writes_evidence_plan(tmp_path: Path) -> None:
    # Given: a claim ledger and evidence directory without a job description.
    ledger = tmp_path / "claims.yml"
    evidence_dir = tmp_path / "evidence"
    out = tmp_path / "submission-plan.md"
    evidence_dir.mkdir()
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "장애 대응 문서를 정리했습니다."',
                "    category: execution",
                "    status: needs_evidence",
                '    evidence_note: "incident note"',
                '    suggested_rewrite: ""',
            ],
        ),
        encoding="utf-8",
    )
    _ = (evidence_dir / "incident.md").write_text("# incident note\n", encoding="utf-8")

    # When: coordinate runs without --job.
    result = run_cli(
        [
            "run",
            "resume-ledger",
            "coordinate",
            str(ledger),
            "--evidence-dir",
            str(evidence_dir),
            "--out",
            str(out),
        ],
    )

    # Then: JD matching is explicitly not evaluated.
    content = out.read_text(encoding="utf-8")
    assert result.returncode == 0
    assert "- jd_match: not_evaluated" in content
    assert "- evidence: EVD-001" in content


def test_coordinate_when_explicit_evidence_dir_is_missing_exits_nonzero(
    tmp_path: Path,
) -> None:
    # Given: a valid ledger and a missing explicit evidence directory.
    ledger = tmp_path / "claims.yml"
    out = tmp_path / "submission-plan.md"
    missing = tmp_path / "missing-evidence"
    _ = ledger.write_text("schema_version: 1\nclaims:\n", encoding="utf-8")

    # When: coordinate runs with the missing evidence directory.
    result = run_cli(
        [
            "run",
            "resume-ledger",
            "coordinate",
            str(ledger),
            "--evidence-dir",
            str(missing),
            "--out",
            str(out),
        ],
    )

    # Then: it fails before writing a misleading plan.
    assert result.returncode != 0
    assert "Evidence directory does not exist" in result.stderr
    assert not out.exists()


def test_coordinate_strict_blocks_malformed_ledger_after_writing_plan(
    tmp_path: Path,
) -> None:
    # Given: a malformed ledger.
    ledger = tmp_path / "malformed.yml"
    out = tmp_path / "submission-plan.md"
    _ = ledger.write_text("not_claims:\n  - broken\n", encoding="utf-8")

    # When: strict coordinate runs.
    result = run_cli(
        [
            "run",
            "resume-ledger",
            "coordinate",
            str(ledger),
            "--out",
            str(out),
            "--strict",
        ],
    )

    # Then: it writes the warning plan and exits non-zero.
    content = out.read_text(encoding="utf-8")
    assert result.returncode != 0
    assert "Strict mode blocked coordinate submission plan." in result.stderr
    assert "Malformed ledger" in content


def test_existing_advise_command_still_writes_report(tmp_path: Path) -> None:
    # Given: a ledger that exercises the existing advise command.
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

    # When: advise runs after coordinate has been added.
    result = run_cli(["run", "resume-ledger", "advise", str(ledger), "--out", str(advice)])

    # Then: the existing advice surface still works.
    content = advice.read_text(encoding="utf-8")
    assert result.returncode == 0
    assert "## Career Review" in content
    assert "## Korean Polish" in content


def test_coordinate_summary_writes_compact_markdown_report(tmp_path: Path) -> None:
    # Given: a ledger with one ready claim and one claim that needs evidence.
    ledger = tmp_path / "claims.yml"
    out = tmp_path / "submission-summary.md"
    _ = ledger.write_text(
        joined_lines(
            [
                "schema_version: 1",
                "claims:",
                "  - claim_id: CLM-001",
                '    text: "Python MLOps 배포 체크리스트를 정리했습니다."',
                "    category: execution",
                "    status: verified",
                '    evidence_note: "release checklist"',
                '    suggested_rewrite: ""',
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

    # When: coordinate runs in summary mode.
    result = run_cli(
        [
            "run",
            "resume-ledger",
            "coordinate",
            str(ledger),
            "--summary",
            "--out",
            str(out),
        ],
    )

    # Then: a compact Markdown summary is written.
    content = out.read_text(encoding="utf-8")
    assert result.returncode == 0
    assert "# Submission Summary" in content
    assert "- ready: 1" in content
    assert "- needs_evidence: 1" in content
    assert "### CLM-002" in content
    assert "### CLM-001" not in content
