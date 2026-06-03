FF                                                                       [100%]
================================== FAILURES ===================================
________ test_readme_describes_report_only_advice_not_source_rewriting ________

    def test_readme_describes_report_only_advice_not_source_rewriting() -> None:
        # Given: the project README.
        content = Path("README.md").read_text(encoding="utf-8")
    
        # When: the product promise is inspected.
        # Then: it avoids implying that the tool rewrites source resumes automatically.
>       assert "rewrite resume claims" not in content
E       AssertionError: assert 'rewrite resume claims' not in '# Resume Cl...klist\n```\n'
E         
E         'rewrite resume claims' is contained here:
E           # Resume Claim Ledger
E           
E           Track, verify, and rewrite resume claims with evidence before submission.
E         ?                    +++++++++++++++++++++
E           ...
E         
E         ...Full output truncated (80 lines hidden), use '-vv' to show

tests\test_readme_contract.py:49: AssertionError
_____________ test_readme_sample_matches_versioned_ledger_schema ______________

    def test_readme_sample_matches_versioned_ledger_schema() -> None:
        # Given: the project README.
        content = Path("README.md").read_text(encoding="utf-8")
    
        # When: the sample ledger output is inspected.
        # Then: it shows the current versioned ledger fields.
>       assert "schema_version: 1" in content
E       AssertionError: assert 'schema_version: 1' in '# Resume Claim Ledger\n\nTrack, verify, and rewrite resume claims with evidence before submission.\n\n## Install\n\n`...: 범위나 판단 기준을 뒷받침할 근거가 필요합니다.\n  - claim_id: CLM-002\n    status: verified\n    evidence_note: release checklist\n```\n'

tests\test_readme_contract.py:60: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_readme_contract.py::test_readme_describes_report_only_advice_not_source_rewriting
FAILED tests/test_readme_contract.py::test_readme_sample_matches_versioned_ledger_schema
