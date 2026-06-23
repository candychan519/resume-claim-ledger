from pathlib import Path


def test_agent_guardrails_require_platform_apply_preview_approval_receipt() -> None:
    content = Path("docs/agent-guardrails.md").read_text(encoding="utf-8")

    required = [
        "Produce a report-only before/after preview of the exact field text first.",
        "Apply to an external platform only after the user explicitly approves the exact text.",
        (
            "Record a post-apply receipt with the platform or surface, field, save action, "
            "exact-match verification, and whether final submit was clicked."
        ),
        "Do not copy private platform screenshots, URLs, local paths, or personal resume values",
    ]
    for phrase in required:
        assert phrase in content
