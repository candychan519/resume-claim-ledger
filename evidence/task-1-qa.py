from resume_claim_ledger.models import Suggestion

print(
    Suggestion(
        claim_id="CLM-001",
        kind="career",
        severity="warning",
        title="Role unclear",
        detail="role unclear",
        suggested_text="clarify role",
    )
)
