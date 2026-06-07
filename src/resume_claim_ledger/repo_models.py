from dataclasses import dataclass
from typing import Literal, TypedDict

REPO_INTAKE_SCHEMA_VERSION = 1

RepoEvidenceKind = Literal[
    "readme",
    "documentation",
    "manifest",
    "ci_workflow",
    "test",
    "source_file",
    "commit",
    "remote",
    "sensitive_file",
    "limit",
    "summary",
]
RepoClaimConfidence = Literal["low", "medium", "high"]
RepoGapSeverity = Literal["info", "warning", "blocker"]
RepoGraphNodeType = Literal[
    "Project",
    "TechStack",
    "Evidence",
    "ClaimCandidate",
    "EvidenceGap",
]


class RepoProfileDict(TypedDict):
    schema_version: int
    name: str
    source: str
    revision: str
    remote: str
    languages: list[str]
    package_manifests: list[str]
    ci_workflows: list[str]
    test_files: list[str]
    documentation_files: list[str]
    warnings: list[str]


class RepoEvidenceItemDict(TypedDict):
    evidence_id: str
    kind: RepoEvidenceKind
    path: str
    title: str
    summary: str
    tags: list[str]


class RepoClaimCandidateDict(TypedDict):
    claim_id: str
    text: str
    confidence: RepoClaimConfidence
    supporting_files: list[str]
    missing_confirmation: str


class RepoEvidenceGapDict(TypedDict):
    gap_id: str
    text: str
    severity: RepoGapSeverity
    related_files: list[str]


class RepoKnowledgeGraphNodeDict(TypedDict):
    id: str
    type: RepoGraphNodeType
    label: str


class RepoKnowledgeGraphEdgeDict(TypedDict):
    source: str
    target: str
    relationship: str


class RepoKnowledgeGraphDict(TypedDict):
    nodes: list[RepoKnowledgeGraphNodeDict]
    edges: list[RepoKnowledgeGraphEdgeDict]


class RepoKnowledgePackDict(TypedDict):
    schema_version: int
    profile: RepoProfileDict
    evidence_catalog: list[RepoEvidenceItemDict]
    claim_candidates: list[RepoClaimCandidateDict]
    evidence_gaps: list[RepoEvidenceGapDict]
    knowledge_graph: RepoKnowledgeGraphDict


class RepoEvidenceCatalogDict(TypedDict):
    schema_version: int
    items: list[RepoEvidenceItemDict]


@dataclass(frozen=True, slots=True)
class RepoProfile:
    name: str
    source: str
    revision: str
    remote: str
    languages: tuple[str, ...]
    package_manifests: tuple[str, ...]
    ci_workflows: tuple[str, ...]
    test_files: tuple[str, ...]
    documentation_files: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RepoEvidenceItem:
    evidence_id: str
    kind: RepoEvidenceKind
    path: str
    title: str
    summary: str
    tags: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RepoClaimCandidate:
    claim_id: str
    text: str
    confidence: RepoClaimConfidence
    supporting_files: tuple[str, ...]
    missing_confirmation: str


@dataclass(frozen=True, slots=True)
class RepoEvidenceGap:
    gap_id: str
    text: str
    severity: RepoGapSeverity
    related_files: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RepoKnowledgeGraphNode:
    node_id: str
    node_type: RepoGraphNodeType
    label: str


@dataclass(frozen=True, slots=True)
class RepoKnowledgeGraphEdge:
    source: str
    target: str
    relationship: str


@dataclass(frozen=True, slots=True)
class RepoKnowledgeGraph:
    nodes: tuple[RepoKnowledgeGraphNode, ...]
    edges: tuple[RepoKnowledgeGraphEdge, ...]


@dataclass(frozen=True, slots=True)
class RepoKnowledgePack:
    profile: RepoProfile
    evidence_items: tuple[RepoEvidenceItem, ...]
    claim_candidates: tuple[RepoClaimCandidate, ...]
    evidence_gaps: tuple[RepoEvidenceGap, ...]
    knowledge_graph: RepoKnowledgeGraph


def repo_profile_to_dict(profile: RepoProfile) -> RepoProfileDict:
    return {
        "schema_version": REPO_INTAKE_SCHEMA_VERSION,
        "name": profile.name,
        "source": profile.source,
        "revision": profile.revision,
        "remote": profile.remote,
        "languages": list(profile.languages),
        "package_manifests": list(profile.package_manifests),
        "ci_workflows": list(profile.ci_workflows),
        "test_files": list(profile.test_files),
        "documentation_files": list(profile.documentation_files),
        "warnings": list(profile.warnings),
    }


def repo_evidence_item_to_dict(item: RepoEvidenceItem) -> RepoEvidenceItemDict:
    return {
        "evidence_id": item.evidence_id,
        "kind": item.kind,
        "path": item.path,
        "title": item.title,
        "summary": item.summary,
        "tags": list(item.tags),
    }


def repo_claim_candidate_to_dict(candidate: RepoClaimCandidate) -> RepoClaimCandidateDict:
    return {
        "claim_id": candidate.claim_id,
        "text": candidate.text,
        "confidence": candidate.confidence,
        "supporting_files": list(candidate.supporting_files),
        "missing_confirmation": candidate.missing_confirmation,
    }


def repo_evidence_gap_to_dict(gap: RepoEvidenceGap) -> RepoEvidenceGapDict:
    return {
        "gap_id": gap.gap_id,
        "text": gap.text,
        "severity": gap.severity,
        "related_files": list(gap.related_files),
    }


def repo_knowledge_graph_node_to_dict(
    node: RepoKnowledgeGraphNode,
) -> RepoKnowledgeGraphNodeDict:
    return {"id": node.node_id, "type": node.node_type, "label": node.label}


def repo_knowledge_graph_edge_to_dict(
    edge: RepoKnowledgeGraphEdge,
) -> RepoKnowledgeGraphEdgeDict:
    return {
        "source": edge.source,
        "target": edge.target,
        "relationship": edge.relationship,
    }


def repo_knowledge_graph_to_dict(graph: RepoKnowledgeGraph) -> RepoKnowledgeGraphDict:
    return {
        "nodes": [repo_knowledge_graph_node_to_dict(node) for node in graph.nodes],
        "edges": [repo_knowledge_graph_edge_to_dict(edge) for edge in graph.edges],
    }


def repo_evidence_catalog_to_dict(pack: RepoKnowledgePack) -> RepoEvidenceCatalogDict:
    return {
        "schema_version": REPO_INTAKE_SCHEMA_VERSION,
        "items": [repo_evidence_item_to_dict(item) for item in pack.evidence_items],
    }


def repo_knowledge_pack_to_dict(pack: RepoKnowledgePack) -> RepoKnowledgePackDict:
    return {
        "schema_version": REPO_INTAKE_SCHEMA_VERSION,
        "profile": repo_profile_to_dict(pack.profile),
        "evidence_catalog": [
            repo_evidence_item_to_dict(item) for item in pack.evidence_items
        ],
        "claim_candidates": [
            repo_claim_candidate_to_dict(candidate) for candidate in pack.claim_candidates
        ],
        "evidence_gaps": [repo_evidence_gap_to_dict(gap) for gap in pack.evidence_gaps],
        "knowledge_graph": repo_knowledge_graph_to_dict(pack.knowledge_graph),
    }
