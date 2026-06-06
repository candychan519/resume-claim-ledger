# Agent Guardrails

Use this checklist when an AI agent helps prepare a resume submission from this repository.

## Non-Negotiables

- Never invent metrics, employers, dates, certifications, links, or usage scope.
- Do not edit the source resume directly. Write a report, proposal, or submission plan first.
- Treat `needs_evidence`, `too_broad`, `rewrite_needed`, and malformed ledgers as blockers.
- Stop and ask for evidence when a claim cannot be verified from the ledger or evidence files.

## Safe Workflow

Start with a compact machine-readable triage report:

```bash
resume-ledger coordinate claims.yml --summary --format json --out submission-summary.json
```

Build the full submission plan only after a job description or evidence directory is available:

```bash
resume-ledger coordinate claims.yml --job jd.md --evidence-dir evidence --out submission-plan.md
```

Run the policy-aware submission gate before handoff:

```bash
resume-ledger doctor claims.yml --policy policy/submission-policy.yml
```

If this command exits non-zero, the agent should not call the resume submission-ready.

## Policy Meaning

The default policy in `policy/submission-policy.yml` keeps resume edits conservative:

- `allow_auto_edit_resume: false` means agents should propose changes instead of mutating the source resume.
- `require_doctor_pass: true` means the final handoff must include a passing doctor result.
- `block_on` lists ledger states that block submission.
- `forbidden_claim_changes` names claim strengthening moves that need explicit user evidence first.

## Blocker Handling

- `malformed_ledger`: regenerate or repair the ledger before writing submission copy.
- `needs_evidence`: attach a real source, or remove or soften the claim.
- `too_broad`: narrow the scope to what the evidence proves.
- `rewrite_needed`: use the suggested safer wording or request missing facts from the user.

When in doubt, leave the claim weaker and ask for proof.
