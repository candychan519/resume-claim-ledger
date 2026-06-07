from resume_claim_ledger.repo_models import (
    RepoClaimCandidate,
    RepoEvidenceGap,
    RepoEvidenceItem,
    RepoKnowledgeGraph,
    RepoKnowledgeGraphEdge,
    RepoKnowledgeGraphNode,
    RepoKnowledgePack,
    RepoProfile,
)
from resume_claim_ledger.repo_reporter import build_repo_knowledge_pack_outputs


def test_build_repo_knowledge_pack_outputs_all_files_without_absolute_paths() -> None:
    # Given: a repository pack that contains only relative source paths.
    pack = RepoKnowledgePack(
        profile=RepoProfile(
            name="demo-repo",
            source="github.com/acme/demo-repo",
            revision="abc1234",
            remote="github.com/acme/demo-repo",
            languages=("Python", "TypeScript"),
            package_manifests=("package.json", "pyproject.toml"),
            ci_workflows=(".github/workflows/ci.yml",),
            test_files=("tests/test_cli.py",),
            documentation_files=("README.md", "docs/usage.md"),
            warnings=("Do not treat code presence as personal contribution proof.",),
        ),
        evidence_items=(
            RepoEvidenceItem(
                evidence_id="REPO-EVD-001",
                kind="manifest",
                path="pyproject.toml",
                title="Python package manifest",
                summary="Defines a Python CLI package.",
                tags=("manifest", "Python"),
            ),
        ),
        claim_candidates=(
            RepoClaimCandidate(
                claim_id="REPO-CLM-001",
                text="Repository contains a Python CLI package.",
                confidence="medium",
                supporting_files=("pyproject.toml",),
                missing_confirmation="Confirm ownership, role, usage scope, and impact.",
            ),
        ),
        evidence_gaps=(
            RepoEvidenceGap(
                gap_id="REPO-GAP-001",
                text="No user contribution evidence was found in the repository.",
                severity="blocker",
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
                    node_id="tech:Python",
                    node_type="TechStack",
                    label="Python",
                ),
                RepoKnowledgeGraphNode(
                    node_id="claim:REPO-CLM-001",
                    node_type="ClaimCandidate",
                    label="Repository contains a Python CLI package.",
                ),
            ),
            edges=(
                RepoKnowledgeGraphEdge(
                    source="project:demo-repo",
                    target="tech:Python",
                    relationship="uses",
                ),
            ),
        ),
    )

    # When: the pack is rendered for writing by the CLI.
    outputs = build_repo_knowledge_pack_outputs(pack)

    # Then: every documented file is present and local machine paths stay out.
    assert tuple(sorted(outputs)) == (
        "agent-brief.md",
        "claim-candidates.yml",
        "evidence-catalog.json",
        "evidence-gaps.md",
        "knowledge-graph.json",
        "repo-profile.json",
        "repo-profile.md",
    )
    combined = "\n".join(outputs.values())
    assert "C:/Users/" not in combined
    assert "\\Users\\" not in combined
    assert "/tmp/" not in combined
    assert "repo-profile.md" in outputs["agent-brief.md"]
    assert "REPO-CLM-001" in outputs["claim-candidates.yml"]
    assert '"schema_version": 1' in outputs["repo-profile.json"]
    assert '"type": "TechStack"' in outputs["knowledge-graph.json"]
