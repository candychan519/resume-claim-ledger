FFFF                                                                     [100%]
================================== FAILURES ===================================
______________ test_readme_documents_python_and_uv_prerequisites ______________

    def test_readme_documents_python_and_uv_prerequisites() -> None:
        # Given: the project README.
        content = Path("README.md").read_text(encoding="utf-8")
    
        # When: the install section is inspected.
        # Then: first-time users can see the runtime and tool prerequisites.
>       assert "Python 3.13" in content
E       assert 'Python 3.13' in '# Resume Claim Ledger\n\nTrack and verify resume claims, then suggest safer wording before submission.\n\n## Install\...   category: execution\n    status: verified\n    evidence_note: "release checklist"\n    suggested_rewrite: ""\n```\n'

tests\test_readme_contract.py:71: AssertionError
__________________ test_readme_links_schema_and_release_docs __________________

    def test_readme_links_schema_and_release_docs() -> None:
        # Given: the project README.
        content = Path("README.md").read_text(encoding="utf-8")
    
        # When: public documentation links are inspected.
        # Then: users can find schema and publishing details without duplicated policy text.
>       assert "docs/ledger-schema.md" in content
E       assert 'docs/ledger-schema.md' in '# Resume Claim Ledger\n\nTrack and verify resume claims, then suggest safer wording before submission.\n\n## Install\...   category: execution\n    status: verified\n    evidence_note: "release checklist"\n    suggested_rewrite: ""\n```\n'

tests\test_readme_contract.py:81: AssertionError
_________ test_readme_documents_strict_and_malformed_ledger_behavior __________

    def test_readme_documents_strict_and_malformed_ledger_behavior() -> None:
        # Given: the project README.
        content = Path("README.md").read_text(encoding="utf-8")
    
        # When: submission-gate and invalid-ledger guidance is inspected.
        # Then: users can anticipate strict failures and malformed-ledger warnings.
        assert "--strict" in content
>       assert "submission gate" in content
E       assert 'submission gate' in '# Resume Claim Ledger\n\nTrack and verify resume claims, then suggest safer wording before submission.\n\n## Install\...   category: execution\n    status: verified\n    evidence_note: "release checklist"\n    suggested_rewrite: ""\n```\n'

tests\test_readme_contract.py:92: AssertionError
_________ test_readme_documents_advice_json_schema_or_schema_doc_link _________

    def test_readme_documents_advice_json_schema_or_schema_doc_link() -> None:
        # Given: the project README.
        content = Path("README.md").read_text(encoding="utf-8")
    
        # When: JSON advice output guidance is inspected.
        # Then: users can find the stable Advice JSON contract.
        assert "--format json" in content
>       assert "Advice JSON" in content
E       assert 'Advice JSON' in '# Resume Claim Ledger\n\nTrack and verify resume claims, then suggest safer wording before submission.\n\n## Install\...   category: execution\n    status: verified\n    evidence_note: "release checklist"\n    suggested_rewrite: ""\n```\n'

tests\test_readme_contract.py:103: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_readme_contract.py::test_readme_documents_python_and_uv_prerequisites
FAILED tests/test_readme_contract.py::test_readme_links_schema_and_release_docs
FAILED tests/test_readme_contract.py::test_readme_documents_strict_and_malformed_ledger_behavior
FAILED tests/test_readme_contract.py::test_readme_documents_advice_json_schema_or_schema_doc_link
