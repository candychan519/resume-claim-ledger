import json
from typing import Final, TypedDict

from .models import (
    ClaimStatus,
    CoordinateAction,
    CoordinateItem,
    RequirementMatch,
    SubmissionPlan,
    submission_plan_to_dict,
)

ACTION_ORDER: Final[tuple[CoordinateAction, ...]] = (
    "ready",
    "needs_evidence",
    "soften_wording",
    "jd_gap",
    "submission_blocker",
)


class ActionCounts(TypedDict):
    ready: int
    needs_evidence: int
    soften_wording: int
    jd_gap: int
    submission_blocker: int


class CoordinateSummaryItemDict(TypedDict):
    claim_id: str
    action: CoordinateAction
    evidence_status: ClaimStatus
    requirement_match: RequirementMatch
    matched_requirements: list[str]
    matched_evidence: list[str]
    next_step: str


class CoordinateSummaryDict(TypedDict):
    schema_version: int
    counts: ActionCounts
    warnings: list[str]
    non_ready: list[CoordinateSummaryItemDict]


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


def build_coordinate_summary_json(plan: SubmissionPlan) -> str:
    payload: CoordinateSummaryDict = {
        "schema_version": plan.schema_version,
        "counts": _summary_counts(plan),
        "warnings": list(plan.warnings),
        "non_ready": [
            _summary_item_to_dict(item) for item in plan.items if item.action != "ready"
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _summary_counts(plan: SubmissionPlan) -> ActionCounts:
    return {
        "ready": _count_action(plan, "ready"),
        "needs_evidence": _count_action(plan, "needs_evidence"),
        "soften_wording": _count_action(plan, "soften_wording"),
        "jd_gap": _count_action(plan, "jd_gap"),
        "submission_blocker": _count_action(plan, "submission_blocker"),
    }


def _summary_item_to_dict(item: CoordinateItem) -> CoordinateSummaryItemDict:
    return {
        "claim_id": item.claim_id,
        "action": item.action,
        "evidence_status": item.evidence_status,
        "requirement_match": item.requirement_match,
        "matched_requirements": list(item.matched_requirements),
        "matched_evidence": list(item.matched_evidence),
        "next_step": item.next_step,
    }


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
