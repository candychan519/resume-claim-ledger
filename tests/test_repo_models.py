from resume_claim_ledger.repo_models import (
    RepoClaimCandidate,
    RepoEvidenceGap,
    RepoEvidenceItem,
    RepoKnowledgeGraph,
    RepoKnowledgeGraphEdge,
    RepoKnowledgeGraphNode,
    RepoKnowledgePack,
    RepoProfile,
    repo_knowledge_pack_to_dict,
)


def test_repo_knowledge_pack_to_dict_exposes_stable_schema() -> None:
    # Given: a repository knowledge pack built from relative, evidence-safe facts.
    pack = RepoKnowledgePack(
        profile=RepoProfile(
            name="demo-repo",
            source="github.com/acme/demo-repo",
            revision="abc1234",
            remote="github.com/acme/demo-repo",
            languages=("Python",),
            package_manifests=("pyproject.toml",),
            ci_workflows=(".github/workflows/ci.yml",),
            test_files=("tests/test_cli.py",),
            documentation_files=("README.md",),
            warnings=("Sensitive file presence recorded without reading contents.",),
        ),
        evidence_items=(
            RepoEvidenceItem(
                evidence_id="REPO-EVD-001",
                kind="readme",
                path="README.md",
                title="README",
                summary="Demo repository for deployment checks.",
                tags=("documentation",),
            ),
        ),
        claim_candidates=(
            RepoClaimCandidate(
                claim_id="REPO-CLM-001",
                text="Repository contains a Python CLI project.",
                confidence="medium",
                supporting_files=("pyproject.toml", "src/demo/cli.py"),
                missing_confirmation=(
                    "Confirm personal contribution, role, usage scope, and impact before use."
                ),
            ),
        ),
        evidence_gaps=(
            RepoEvidenceGap(
                gap_id="REPO-GAP-001",
                text="No deployment metric evidence was found.",
                severity="warning",
                related_files=("README.md",),
            ),
        ),
        knowledge_graph=RepoKnowledgeGraph(
            nodes=(
                RepoKnowledgeGraphNode(
                    node_id="project:demo-repo",
                    node_type="Project",
                    label="demo-repo",
                ),
                RepoKnowledgeGraphNode(
                    node_id="evidence:REPO-EVD-001",
                    node_type="Evidence",
                    label="README",
                ),
            ),
            edges=(
                RepoKnowledgeGraphEdge(
                    source="project:demo-repo",
                    target="evidence:REPO-EVD-001",
                    relationship="has_evidence",
                ),
            ),
        ),
    )

    # When: the pack is serialized for JSON/report output.
    payload = repo_knowledge_pack_to_dict(pack)

    # Then: the schema is stable, versioned, and path-safe.
    assert payload == {
        "schema_version": 1,
        "profile": {
            "schema_version": 1,
            "name": "demo-repo",
            "source": "github.com/acme/demo-repo",
            "revision": "abc1234",
            "remote": "github.com/acme/demo-repo",
            "languages": ["Python"],
            "package_manifests": ["pyproject.toml"],
            "ci_workflows": [".github/workflows/ci.yml"],
            "test_files": ["tests/test_cli.py"],
            "documentation_files": ["README.md"],
            "warnings": ["Sensitive file presence recorded without reading contents."],
        },
        "evidence_catalog": [
            {
                "evidence_id": "REPO-EVD-001",
                "kind": "readme",
                "path": "README.md",
                "title": "README",
                "summary": "Demo repository for deployment checks.",
                "tags": ["documentation"],
            },
        ],
        "claim_candidates": [
            {
                "claim_id": "REPO-CLM-001",
                "text": "Repository contains a Python CLI project.",
                "confidence": "medium",
                "supporting_files": ["pyproject.toml", "src/demo/cli.py"],
                "missing_confirmation": (
                    "Confirm personal contribution, role, usage scope, and impact before use."
                ),
            },
        ],
        "evidence_gaps": [
            {
                "gap_id": "REPO-GAP-001",
                "text": "No deployment metric evidence was found.",
                "severity": "warning",
                "related_files": ["README.md"],
            },
        ],
        "knowledge_graph": {
            "nodes": [
                {
                    "id": "project:demo-repo",
                    "type": "Project",
                    "label": "demo-repo",
                },
                {
                    "id": "evidence:REPO-EVD-001",
                    "type": "Evidence",
                    "label": "README",
                },
            ],
            "edges": [
                {
                    "source": "project:demo-repo",
                    "target": "evidence:REPO-EVD-001",
                    "relationship": "has_evidence",
                },
            ],
        },
    }
