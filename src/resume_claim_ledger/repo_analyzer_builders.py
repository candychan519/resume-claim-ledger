from .repo_models import (
    RepoClaimCandidate,
    RepoEvidenceGap,
    RepoEvidenceItem,
    RepoEvidenceKind,
    RepoGapSeverity,
    RepoKnowledgeGraph,
    RepoKnowledgeGraphEdge,
    RepoKnowledgeGraphNode,
    RepoProfile,
)

CONTRIBUTION_CONFIRMATION = (
    "Confirm personal contribution, role, ownership, dates, usage scope, and impact before use."
)


def claim_candidates(
    profile: RepoProfile,
    source_files: tuple[str, ...],
) -> tuple[RepoClaimCandidate, ...]:
    candidates: list[RepoClaimCandidate] = []
    if profile.languages != ():
        supporting = profile.package_manifests + source_files[:3]
        candidates.append(
            RepoClaimCandidate(
                claim_id=claim_id(len(candidates)),
                text=f"Repository contains a {', '.join(profile.languages)} codebase.",
                confidence="medium" if profile.package_manifests != () else "low",
                supporting_files=supporting,
                missing_confirmation=CONTRIBUTION_CONFIRMATION,
            ),
        )
    if profile.ci_workflows != ():
        candidates.append(
            RepoClaimCandidate(
                claim_id=claim_id(len(candidates)),
                text="Repository includes CI workflow configuration.",
                confidence="low",
                supporting_files=profile.ci_workflows,
                missing_confirmation=CONTRIBUTION_CONFIRMATION,
            ),
        )
    if profile.test_files != ():
        candidates.append(
            RepoClaimCandidate(
                claim_id=claim_id(len(candidates)),
                text="Repository includes automated test files.",
                confidence="low",
                supporting_files=profile.test_files,
                missing_confirmation=CONTRIBUTION_CONFIRMATION,
            ),
        )
    return tuple(candidates)


def knowledge_graph(
    profile: RepoProfile,
    evidence_items: tuple[RepoEvidenceItem, ...],
    candidates: tuple[RepoClaimCandidate, ...],
    gaps: tuple[RepoEvidenceGap, ...],
) -> RepoKnowledgeGraph:
    project_id = f"project:{profile.name}"
    nodes = [RepoKnowledgeGraphNode(project_id, "Project", profile.name)]
    edges: list[RepoKnowledgeGraphEdge] = []
    for language in profile.languages:
        tech_id = f"tech:{language}"
        nodes.append(RepoKnowledgeGraphNode(tech_id, "TechStack", language))
        edges.append(RepoKnowledgeGraphEdge(project_id, tech_id, "uses"))
    for item in evidence_items:
        evidence_node_id = f"evidence:{item.evidence_id}"
        nodes.append(RepoKnowledgeGraphNode(evidence_node_id, "Evidence", item.title))
        edges.append(RepoKnowledgeGraphEdge(project_id, evidence_node_id, "has_evidence"))
    for candidate in candidates:
        claim_node_id = f"claim:{candidate.claim_id}"
        nodes.append(RepoKnowledgeGraphNode(claim_node_id, "ClaimCandidate", candidate.text))
        edges.append(RepoKnowledgeGraphEdge(project_id, claim_node_id, "has_claim_candidate"))
    for gap in gaps:
        gap_node_id = f"gap:{gap.gap_id}"
        nodes.append(RepoKnowledgeGraphNode(gap_node_id, "EvidenceGap", gap.text))
        edges.append(RepoKnowledgeGraphEdge(project_id, gap_node_id, "has_gap"))
    return RepoKnowledgeGraph(nodes=tuple(nodes), edges=tuple(edges))


def append_evidence(
    items: list[RepoEvidenceItem],
    kind: RepoEvidenceKind,
    path: str,
    title: str,
    summary: str,
    tags: tuple[str, ...],
) -> None:
    items.append(
        RepoEvidenceItem(
            evidence_id=evidence_id(len(items)),
            kind=kind,
            path=path,
            title=title,
            summary=summary,
            tags=tags,
        ),
    )


def append_gap(
    gaps: list[RepoEvidenceGap],
    text: str,
    severity: RepoGapSeverity,
    related_files: tuple[str, ...],
) -> None:
    gaps.append(
        RepoEvidenceGap(
            gap_id=gap_id(len(gaps)),
            text=text,
            severity=severity,
            related_files=related_files,
        ),
    )


def evidence_id(index: int) -> str:
    return f"REPO-EVD-{index + 1:03d}"


def claim_id(index: int) -> str:
    return f"REPO-CLM-{index + 1:03d}"


def gap_id(index: int) -> str:
    return f"REPO-GAP-{index + 1:03d}"
