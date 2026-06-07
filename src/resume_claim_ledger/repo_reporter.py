import json
import re
from typing import Final, Literal

from .repo_models import (
    RepoClaimCandidate,
    RepoEvidenceCatalogDict,
    RepoEvidenceGap,
    RepoEvidenceItem,
    RepoKnowledgeGraphDict,
    RepoKnowledgePack,
    RepoProfileDict,
    repo_evidence_catalog_to_dict,
    repo_knowledge_graph_to_dict,
    repo_profile_to_dict,
)

RepoOutputFile = Literal[
    "repo-profile.md",
    "repo-profile.json",
    "evidence-catalog.json",
    "claim-candidates.yml",
    "evidence-gaps.md",
    "agent-brief.md",
    "knowledge-graph.json",
]
RepoJsonPayload = RepoProfileDict | RepoEvidenceCatalogDict | RepoKnowledgeGraphDict

LOCAL_PATH_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(^|[\s\"'(:])([A-Za-z]:[\\/]|\\\\Users\\\\|/Users/|/home/|/tmp/|/var/folders/)",
)
LOCAL_PATH_OUTPUT_MESSAGE = "repository knowledge pack output contains a local absolute path"


def build_repo_knowledge_pack_outputs(pack: RepoKnowledgePack) -> dict[RepoOutputFile, str]:
    outputs: dict[RepoOutputFile, str] = {
        "repo-profile.md": build_repo_profile_markdown(pack),
        "repo-profile.json": _json(repo_profile_to_dict(pack.profile)),
        "evidence-catalog.json": _json(repo_evidence_catalog_to_dict(pack)),
        "claim-candidates.yml": build_claim_candidates_yml(pack.claim_candidates),
        "evidence-gaps.md": build_evidence_gaps_markdown(pack.evidence_gaps),
        "agent-brief.md": build_agent_brief_markdown(pack),
        "knowledge-graph.json": _json(repo_knowledge_graph_to_dict(pack.knowledge_graph)),
    }
    for content in outputs.values():
        _raise_for_local_path(content)
    return outputs


def build_repo_profile_markdown(pack: RepoKnowledgePack) -> str:
    profile = pack.profile
    lines = [
        "# Repository Profile",
        "",
        f"- name: {profile.name}",
        f"- source: {profile.source}",
        f"- revision: {profile.revision}",
        f"- remote: {_format_optional(profile.remote)}",
        "",
        "## Signals",
        "",
        f"- languages: {_format_values(profile.languages)}",
        f"- package_manifests: {_format_values(profile.package_manifests)}",
        f"- ci_workflows: {_format_values(profile.ci_workflows)}",
        f"- test_files: {_format_values(profile.test_files)}",
        f"- documentation_files: {_format_values(profile.documentation_files)}",
        "",
        "## Evidence Items",
        "",
    ]
    if pack.evidence_items == ():
        lines.append("No repository evidence items were detected.")
    else:
        for item in pack.evidence_items:
            lines.extend(_evidence_item_lines(item))
    if profile.warnings != ():
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in profile.warnings)
    return "\n".join(lines).rstrip() + "\n"


def build_claim_candidates_yml(candidates: tuple[RepoClaimCandidate, ...]) -> str:
    lines = ["schema_version: 1", "claim_candidates:"]
    if candidates == ():
        lines.append("  []")
    for candidate in candidates:
        lines.extend(
            [
                f"  - claim_id: {_quote(candidate.claim_id)}",
                f"    text: {_quote(candidate.text)}",
                f"    confidence: {_quote(candidate.confidence)}",
                "    supporting_files:",
                *_indented_values(candidate.supporting_files, 6),
                f"    missing_confirmation: {_quote(candidate.missing_confirmation)}",
            ],
        )
    return "\n".join(lines).rstrip() + "\n"


def build_evidence_gaps_markdown(gaps: tuple[RepoEvidenceGap, ...]) -> str:
    lines = ["# Evidence Gaps", ""]
    if gaps == ():
        lines.append("No repository evidence gaps were detected.")
    else:
        for gap in gaps:
            lines.extend(
                [
                    f"## {gap.gap_id}",
                    "",
                    f"- severity: {gap.severity}",
                    f"- gap: {gap.text}",
                    f"- related_files: {_format_values(gap.related_files)}",
                    "",
                ],
            )
    return "\n".join(lines).rstrip() + "\n"


def build_agent_brief_markdown(pack: RepoKnowledgePack) -> str:
    lines = [
        "# Agent Brief",
        "",
        f"Review `repo-profile.md` first for {pack.profile.name}.",
        "Use `evidence-catalog.json` for source-backed facts.",
        "Use `claim-candidates.yml` only as report-only draft material.",
        "Do not treat repository contents as proof of personal ownership or impact.",
        "",
        "## Read Order",
        "",
        "- repo-profile.md",
        "- evidence-catalog.json",
        "- claim-candidates.yml",
        "- evidence-gaps.md",
        "- knowledge-graph.json",
        "",
        "## Stop Rules",
        "",
        "- Ask for user confirmation before using a repo-derived claim in a resume.",
        "- Never copy secret contents or private remote URLs into career materials.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _json(payload: RepoJsonPayload) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def _evidence_item_lines(item: RepoEvidenceItem) -> list[str]:
    return [
        f"### {item.evidence_id}",
        "",
        f"- kind: {item.kind}",
        f"- path: {item.path}",
        f"- title: {item.title}",
        f"- summary: {item.summary}",
        f"- tags: {_format_values(item.tags)}",
        "",
    ]


def _format_values(values: tuple[str, ...]) -> str:
    if values == ():
        return "(none)"
    return ", ".join(values)


def _format_optional(value: str) -> str:
    if value == "":
        return "(none)"
    return value


def _indented_values(values: tuple[str, ...], spaces: int) -> list[str]:
    prefix = " " * spaces
    if values == ():
        return [f"{prefix}[]"]
    return [f"{prefix}- {_quote(value)}" for value in values]


def _quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _raise_for_local_path(content: str) -> None:
    if LOCAL_PATH_PATTERN.search(content) is not None:
        raise ValueError(LOCAL_PATH_OUTPUT_MESSAGE)
