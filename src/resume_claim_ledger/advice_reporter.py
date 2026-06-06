import json
from typing import Literal, TypedDict

from .career_advisor import advise_career
from .korean_polish import advise_korean_polish
from .models import Claim, Suggestion, SuggestionDict, suggestion_to_dict
from .reporter import build_report

AdviceFormat = Literal["markdown", "json"]


class AdvicePayload(TypedDict):
    schema_version: int
    suggestions: list[SuggestionDict]


def collect_suggestions(
    claims: list[Claim],
    *,
    career: bool,
    polish_ko: bool,
) -> list[Suggestion]:
    suggestions: list[Suggestion] = []
    if career:
        suggestions.extend(advise_career(claims))
    if polish_ko:
        suggestions.extend(advise_korean_polish(claims))
    return suggestions


def build_advice_output(
    claims: list[Claim],
    warnings: list[str],
    suggestions: list[Suggestion],
    output_format: AdviceFormat,
) -> str:
    match output_format:
        case "markdown":
            return build_advice_markdown(claims, warnings, suggestions)
        case "json":
            return build_advice_json(suggestions)


def build_advice_markdown(
    claims: list[Claim],
    warnings: list[str],
    suggestions: list[Suggestion],
) -> str:
    if suggestions == []:
        lines = ["# Claim Advice", "", "No career or Korean polish suggestions found."]
        if warnings != []:
            lines.extend(["", "## Warnings", "", *[f"- {warning}" for warning in warnings]])
        return "\n".join(lines) + "\n"
    return build_report(claims, warnings=warnings, suggestions=suggestions)


def build_advice_json(suggestions: list[Suggestion]) -> str:
    payload: AdvicePayload = {
        "schema_version": 1,
        "suggestions": [suggestion_to_dict(suggestion) for suggestion in suggestions],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
