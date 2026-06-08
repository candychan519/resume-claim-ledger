from pathlib import Path


def read_readme() -> str:
    return Path("README.md").read_text(encoding="utf-8")


def test_readme_opens_with_clear_product_positioning() -> None:
    # Given: the public README.
    content = read_readme()

    # When: the opening positioning and core sections are inspected.
    required = [
        "# Resume Claim Ledger",
        (
            "Evidence-bound resume submission coordinator for tracking claims, proof, "
            "JD fit, and submission readiness."
        ),
        "## Why This Exists",
        "AI-assisted resume writing can quietly inflate scope, impact, and metrics.",
        "## What It Does",
        "## What It Does Not Do",
    ]

    # Then: new users see the product purpose before implementation details.
    for phrase in required:
        assert phrase in content


def test_readme_prioritizes_explanation_and_quickstart_before_install() -> None:
    # Given: the public README.
    content = read_readme()

    # When: the section order is inspected.
    why_index = content.index("## Why This Exists")
    quickstart_index = content.index("## Quickstart")
    install_index = content.index("## Install")

    # Then: the README leads with purpose and workflow, not raw command dumps.
    assert why_index < quickstart_index
    assert quickstart_index < install_index
    assert "## Usage" not in content
    assert "## Recommended Workflow" not in content


def test_readme_documents_quickstart_as_submission_flow() -> None:
    # Given: the public README.
    content = read_readme()

    # When: the quickstart guidance is inspected.
    required = [
        "resume-ledger scan resume.md --out claims.yml",
        "resume-ledger coordinate claims.yml --summary --out submission-summary.md",
        (
            "resume-ledger coordinate claims.yml --job jd.md --evidence-dir evidence "
            "--out submission-plan.md"
        ),
        "resume-ledger doctor claims.yml --policy policy/submission-policy.yml",
        "Status: Blocked",
        "Status: Ready",
    ]

    # Then: the first successful path ends in a submission gate decision.
    for phrase in required:
        assert phrase in content


def test_readme_collects_cli_commands_in_a_table() -> None:
    # Given: the public README.
    content = read_readme()

    # When: the command reference is inspected.
    required = [
        "## Commands",
        "| Command | Use when |",
        "| `scan` | Create a claim ledger from resume bullets. |",
        "| `review` | Count claim statuses in a ledger. |",
        "| `report` | Write a Markdown claim review. |",
        "| `advise` | Produce report-only career and Korean polish suggestions. |",
        "| `coordinate` | Build a submission plan from claims, JD, and evidence. |",
        "| `doctor` | Fail the final gate when unsafe claims remain. |",
    ]

    # Then: every public CLI command has a compact purpose statement.
    for phrase in required:
        assert phrase in content


def test_readme_documents_repo_intake_workflow() -> None:
    # Given: the public README.
    content = read_readme()

    # When: repository intake guidance is inspected.
    required = [
        (
            "resume-ledger repo intake https://github.com/acme/demo "
            "--out knowledge/repos/demo --name demo"
        ),
        "repo-profile.md",
        "claim-candidates.yml",
        "knowledge-graph.json",
        "| `repo intake` | Build a static repository evidence knowledge pack. |",
        (
            "| [docs/repo-intake.md](docs/repo-intake.md) | Repository evidence "
            "intake workflow and schemas. |"
        ),
    ]

    # Then: users can discover the command, outputs, and long-form docs.
    for phrase in required:
        assert phrase in content


def test_readme_keeps_safety_model_together() -> None:
    # Given: the public README.
    content = read_readme()

    # When: the safety model is inspected.
    required = [
        "Does not rewrite your source resume automatically.",
        (
            "Does not invent metrics, employers, dates, links, certifications, "
            "or scope."
        ),
        "Does not use AI scoring for JD matching.",
        "Report-only means outputs are suggestions and gates, not source-file edits.",
        "policy/submission-policy.yml",
        "docs/agent-guardrails.md",
    ]

    # Then: the README states what the tool refuses to do.
    for phrase in required:
        assert phrase in content


def test_readme_documents_agent_workflow_and_skills() -> None:
    # Given: the public README.
    content = read_readme()

    # When: the agent workflow section is inspected.
    required = [
        "## Agent Workflow",
        "resume-ledger coordinate claims.yml --summary --format json",
        "resume-ledger doctor claims.yml --policy policy/submission-policy.yml",
        "[$career-discovery-coordinator](skills/career-discovery-coordinator/SKILL.md)",
        "[$resume-submission-coordinator](skills/resume-submission-coordinator/SKILL.md)",
        "[$evidence-triage](skills/evidence-triage/SKILL.md)",
        "Never call a resume submission-ready when the policy doctor fails.",
    ]

    # Then: agents get a safe machine-readable path and explicit stop rule.
    for phrase in required:
        assert phrase in content


def test_readme_keeps_install_and_development_paths() -> None:
    # Given: the public README.
    content = read_readme()

    # When: setup guidance is inspected.
    required = [
        "## Install",
        "Python 3.13+",
        "uv tool install git+https://github.com/candychan519/resume-claim-ledger",
        "uv tool install resume-claim-ledger",
        "## Local Development",
        "uv sync --dev",
        "uv run pytest -q",
        "uv run ruff check .",
        "uv run basedpyright",
        "uv build",
    ]

    # Then: first-time users and maintainers can still install and validate locally.
    for phrase in required:
        assert phrase in content


def test_readme_links_supporting_docs_in_one_table() -> None:
    # Given: the public README.
    content = read_readme()

    # When: supporting docs are inspected.
    required = [
        "## Docs",
        "| Document | Purpose |",
        (
            "| [docs/ledger-schema.md](docs/ledger-schema.md) | Ledger, Advice JSON, "
            "and Coordinate JSON schemas. |"
        ),
        (
            "| [docs/agent-guardrails.md](docs/agent-guardrails.md) | Safe behavior "
            "for AI agents. |"
        ),
        (
            "| [docs/career-discovery.md](docs/career-discovery.md) | Career discovery "
            "workflow for turning repositories, documents, and interviews into project stories. |"
        ),
        "| [docs/releasing.md](docs/releasing.md) | Release and publishing process. |",
        (
            "| [docs/maintenance.md](docs/maintenance.md) | Maintainer checks and "
            "deterministic rule guidance. |"
        ),
    ]

    # Then: long-form references are collected in one predictable place.
    for phrase in required:
        assert phrase in content


def test_agent_guardrails_doc_defines_safe_agent_workflow() -> None:
    # Given: the agent guardrails document.
    content = Path("docs/agent-guardrails.md").read_text(encoding="utf-8")

    # When: the safe workflow guidance is inspected.
    required = [
        "Never invent metrics, employers, dates, certifications, links, or usage scope.",
        "Do not edit the source resume directly.",
        "resume-ledger coordinate claims.yml --summary --format json",
        "resume-ledger doctor claims.yml --policy policy/submission-policy.yml",
        "Stop and ask for evidence",
    ]

    # Then: agents are told to produce reports and stop on missing proof.
    for phrase in required:
        assert phrase in content


def test_agent_guardrails_document_repo_intake_safety() -> None:
    # Given: the agent guardrails document.
    content = Path("docs/agent-guardrails.md").read_text(encoding="utf-8")

    # When: repository intake rules are inspected.
    required = [
        "resume-ledger repo intake SOURCE --out knowledge/repos/NAME --name NAME",
        "Do not run target repository code, package managers, tests, builds, scripts, or imports.",
        (
            "Do not infer personal ownership, metrics, dates, employer, production usage, "
            "or scope from code presence."
        ),
        "Repository-derived claim candidates are not verified claims.",
        "Never copy secret contents or private remote URLs into user-facing output.",
    ]

    # Then: agents are constrained to static, report-only repository evidence intake.
    for phrase in required:
        assert phrase in content


def test_readme_documents_career_discovery_starting_point() -> None:
    # Given: the public README.
    content = read_readme()

    # When: the career discovery workflow is inspected.
    required = [
        "When you feel stuck before writing a resume, start with career discovery.",
        "source inventory",
        "project story cards",
        "interview questions",
        "claim backlog",
        "[$career-discovery-coordinator](skills/career-discovery-coordinator/SKILL.md)",
        (
            "| [docs/career-discovery.md](docs/career-discovery.md) | Career discovery "
            "workflow for turning repositories, documents, and interviews into project stories. |"
        ),
    ]

    # Then: the README gives agents a first step for unclear career history.
    for phrase in required:
        assert phrase in content


def test_agent_guardrails_document_career_discovery_safety() -> None:
    # Given: the agent guardrails document.
    content = Path("docs/agent-guardrails.md").read_text(encoding="utf-8")

    # When: career discovery rules are inspected.
    required = [
        "Start with career discovery when the user feels stuck before writing.",
        "Create project story cards before resume bullets.",
        "Do not turn repository presence into personal contribution evidence.",
        "Use interview questions to fill missing role, scope, date, metric, and impact facts.",
        "Keep uncertain items in `claim-backlog.yml` until confirmed.",
    ]

    # Then: agents know how to explore without overclaiming.
    for phrase in required:
        assert phrase in content


def test_default_submission_policy_blocks_unsafe_claim_states() -> None:
    # Given: the default submission policy.
    content = Path("policy/submission-policy.yml").read_text(encoding="utf-8")

    # When: blocker rules are inspected.
    required = [
        "allow_auto_edit_resume: false",
        "require_doctor_pass: true",
        "- malformed_ledger",
        "- needs_evidence",
        "- too_broad",
        "- rewrite_needed",
        "- add_metric",
        "- add_employer",
        "- add_date",
        "- strengthen_scope",
    ]

    # Then: unsafe claim states and strengthening moves stay blocked by default.
    for phrase in required:
        assert phrase in content


def test_maintenance_docs_describe_coordinate_summary_as_report_only() -> None:
    # Given: the maintenance documentation.
    content = Path("docs/maintenance.md").read_text(encoding="utf-8")

    # When: coordinate summary maintenance notes are inspected.
    # Then: summary mode is held to the same report-only contract.
    assert "summary mode" in content
    assert "non-ready claims" in content
    assert "report-only" in content


def test_maintenance_docs_describe_living_rules_and_skills() -> None:
    # Given: the maintenance documentation.
    content = Path("docs/maintenance.md").read_text(encoding="utf-8")

    # When: process maintenance guidance is inspected.
    required = [
        "Living Rules and Skills",
        "working agreements",
        "smallest relevant update",
        "repeated",
        "Do not add automation, evaluation frameworks, or SkillOpt",
    ]

    # Then: evolving rules and skills stay lightweight during the transition stage.
    for phrase in required:
        assert phrase in content


def test_maintenance_docs_keep_release_publishing_deferred() -> None:
    # Given: the maintenance documentation.
    content = Path("docs/maintenance.md").read_text(encoding="utf-8")

    # When: release safety guidance is inspected.
    required = [
        "artifact-only release",
        "Do not publish to TestPyPI or PyPI",
        "package-index publishing is intentionally deferred",
    ]

    # Then: maintenance guidance matches the current release workflow.
    for phrase in required:
        assert phrase in content
