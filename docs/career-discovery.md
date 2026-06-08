# Career Discovery

Career discovery is the starting point when the user feels stuck before writing
a resume. It turns repositories, project folders, documents, notes, and
interview answers into evidence-bound project stories and claim candidates.

## When To Use

Use this workflow before resume, portfolio, cover letter, or interview drafting
when the user says their experience is scattered or hard to summarize.

## Outputs

| File | Purpose |
| --- | --- |
| `source-inventory.md` | Inputs the agent inspected or still needs. |
| `project-story-cards.yml` | Project-level stories with role, actions, evidence, and risks. |
| `interview-questions.md` | Smallest next questions needed to fill missing facts. |
| `claim-backlog.yml` | Report-only resume or portfolio claim candidates. |
| `evidence-gaps.md` | Missing proof, unclear scope, and unconfirmed contribution notes. |
| `agent-brief.md` | Recommended read order and handoff rules for future agents. |

## Story Card Contract

Each project story card should contain:

```yaml
project_id:
project_name:
one_line_summary:
problem_context:
user_role:
key_actions:
tech_stack:
evidence_files:
claim_candidates:
missing_confirmations:
interview_questions:
risk_notes:
```

## Safe Interpretation

- Repository files prove repository content exists, not personal authorship.
- Docs and notes can suggest a project story, but they do not prove metrics,
  dates, production usage, ownership, or business impact.
- Interview answers can confirm memory, but strong claims still need usable proof
  before submission.
- Secret-like files should be named only by relative path; never ask for or copy
  secret values.

## Recommended Flow

1. Build a source inventory.
2. Run repository intake for each relevant codebase:

   ```bash
   resume-ledger repo intake SOURCE --out knowledge/repos/NAME --name NAME
   ```

3. Create project story cards before resume bullets.
4. Ask interview questions for missing role, scope, date, metric, and impact facts.
5. Keep uncertain items in `claim-backlog.yml` until confirmed.
6. Hand confirmed items to the normal claim ledger and doctor workflow.
