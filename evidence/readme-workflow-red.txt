   Building resume-claim-ledger @ file:///C:/Users/wjfeo/dev/career/.codex-tmp/resume-claim-ledger
      Built resume-claim-ledger @ file:///C:/Users/wjfeo/dev/career/.codex-tmp/resume-claim-ledger
Uninstalled 1 package in 1ms
Installed 1 package in 62ms
F                                                                        [100%]
================================== FAILURES ===================================
____________ test_readme_documents_recommended_submission_workflow ____________

    def test_readme_documents_recommended_submission_workflow() -> None:
        content = Path("README.md").read_text(encoding="utf-8")
    
        required = [
            "## Recommended Workflow",
            "resume-ledger scan resume.md --out claims.yml",
            "resume-ledger coordinate claims.yml --summary --out submission-summary.md",
            (
                "resume-ledger coordinate claims.yml --job jd.md --evidence-dir evidence "
                "--out submission-plan.md"
            ),
            "resume-ledger coordinate claims.yml --format json --out submission-plan.json",
            "resume-ledger doctor claims.yml",
            "Start with `--summary`",
            "Use the full submission plan",
        ]
        for phrase in required:
>           assert phrase in content
E           AssertionError: assert '## Recommended Workflow' in '# Resume Claim Ledger\n\nTrack and verify resume claims, then suggest safer wording before submission.\n\n## Install\...n\nFor the full ledger, Advice JSON, and Coordinate JSON schema, see [docs/ledger-schema.md](docs/ledger-schema.md).\n'

tests\test_readme_contract.py:163: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_readme_contract.py::test_readme_documents_recommended_submission_workflow
