import json
from typing import Final

from .models import CoordinateAction, CoordinateItem, SubmissionPlan, submission_plan_to_dict

ACTION_ORDER: Final[tuple[CoordinateAction, ...]] = (
    "ready",
    "needs_evidence",
    "soften_wording",
    "jd_gap",
    "submission_blocker",
)


def build_coordinate_markdown(plan: SubmissionPlan) -> str:
    lines = [
        "# Submission Plan",
        "",
        "## Summary",
        "",
        *_summary_lines(plan),
        "",
    ]
    if plan.warnings != ():
        lines.extend(["## Warnings", "", *[f"- {warning}" for warning in plan.warnings], ""])
    lines.extend(["## Actions", ""])
    for item in plan.items:
        lines.extend(_item_lines(item))
    return "\n".join(lines).rstrip() + "\n"


def build_coordinate_summary_markdown(plan: SubmissionPlan) -> str:
    lines = [
        "# Submission Summary",
        "",
        "## Counts",
        "",
        *_summary_lines(plan),
        "",
    ]
    if plan.warnings != ():
        lines.extend(["## Warnings", "", *[f"- {warning}" for warning in plan.warnings], ""])

    non_ready = tuple(item for item in plan.items if item.action != "ready")
    lines.extend(["## Needs Attention", ""])
    if non_ready == ():
        lines.extend(["No non-ready claims."])
    else:
        for item in non_ready:
            lines.extend(_summary_item_lines(item))
    return "\n".join(lines).rstrip() + "\n"


def build_coordinate_json(plan: SubmissionPlan) -> str:
    return json.dumps(submission_plan_to_dict(plan), ensure_ascii=False, indent=2) + "\n"


def _summary_lines(plan: SubmissionPlan) -> list[str]:
    return [f"- {action}: {_count_action(plan, action)}" for action in ACTION_ORDER]


def _count_action(plan: SubmissionPlan, action: CoordinateAction) -> int:
    return sum(1 for item in plan.items if item.action == action)


def _item_lines(item: CoordinateItem) -> list[str]:
    return [
        f"### {item.claim_id}",
        "",
        f"- source: {item.source_text}",
        f"- action: {item.action}",
        f"- evidence_status: {item.evidence_status}",
        f"- jd_match: {item.requirement_match}",
        f"- requirements: {_format_ids(item.matched_requirements)}",
        f"- evidence: {_format_ids(item.matched_evidence)}",
        f"- next_step: {item.next_step}",
        "",
    ]


def _summary_item_lines(item: CoordinateItem) -> list[str]:
    return [
        f"### {item.claim_id}",
        "",
        f"- action: {item.action}",
        f"- jd_match: {item.requirement_match}",
        f"- requirements: {_format_ids(item.matched_requirements)}",
        f"- evidence: {_format_ids(item.matched_evidence)}",
        f"- next_step: {item.next_step}",
        "",
    ]


def _format_ids(values: tuple[str, ...]) -> str:
    if values == ():
        return "(none)"
    return ", ".join(values)
