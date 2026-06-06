from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal, override

from .ledger_io import LedgerReadResult
from .reviewer import summarize_statuses

PolicyBlocker = Literal["malformed_ledger", "needs_evidence", "too_broad", "rewrite_needed"]
ForbiddenClaimChange = Literal["add_metric", "add_employer", "add_date", "strengthen_scope"]
PolicyListKey = Literal["block_on", "forbidden_claim_changes"]

ROOT_KEY: Final = "submission_policy:"


@dataclass(frozen=True, slots=True)
class SubmissionPolicy:
    allow_auto_edit_resume: bool
    require_doctor_pass: bool
    block_on: tuple[PolicyBlocker, ...]
    forbidden_claim_changes: tuple[ForbiddenClaimChange, ...]


@dataclass(frozen=True, slots=True)
class PolicyParseError(Exception):
    path: Path
    message: str

    @override
    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


@dataclass(slots=True)
class PolicyDraft:
    allow_auto_edit_resume: bool | None = None
    require_doctor_pass: bool | None = None
    block_on: list[PolicyBlocker] = field(default_factory=list)
    forbidden_claim_changes: list[ForbiddenClaimChange] = field(default_factory=list)
    active_list: PolicyListKey | None = None
    saw_root: bool = False


def read_submission_policy(path: Path) -> SubmissionPolicy:
    return _parse_submission_policy(path, path.read_text(encoding="utf-8"))


def doctor_policy_violations(
    result: LedgerReadResult,
    policy: SubmissionPolicy,
) -> tuple[str, ...]:
    counts = summarize_statuses(result.claims)
    violations: list[str] = []
    for blocker in policy.block_on:
        match blocker:
            case "malformed_ledger":
                violations.extend(f"malformed_ledger: {warning}" for warning in result.warnings)
            case "needs_evidence":
                _append_count_violation(violations, blocker, counts[blocker])
            case "too_broad":
                _append_count_violation(violations, blocker, counts[blocker])
            case "rewrite_needed":
                _append_count_violation(violations, blocker, counts[blocker])
    return tuple(violations)


def _parse_submission_policy(path: Path, content: str) -> SubmissionPolicy:
    draft = PolicyDraft()
    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        stripped = raw_line.partition("#")[0].strip()
        if stripped != "":
            _parse_policy_line(path, line_number, stripped, draft)

    return _policy_from_draft(path, draft)


def _parse_policy_line(
    path: Path,
    line_number: int,
    stripped: str,
    draft: PolicyDraft,
) -> None:
    if stripped == ROOT_KEY:
        draft.saw_root = True
        draft.active_list = None
        return
    if not draft.saw_root:
        raise _parse_error(path, line_number, f"expected {ROOT_KEY}")
    if stripped.startswith("- "):
        _append_policy_list_item(path, line_number, stripped[2:].strip(), draft)
        return

    key, separator, value = stripped.partition(":")
    if separator == "":
        raise _parse_error(path, line_number, "expected key: value")
    _set_policy_key(path, line_number, key, value, draft)


def _set_policy_key(
    path: Path,
    line_number: int,
    key: str,
    value: str,
    draft: PolicyDraft,
) -> None:
    draft.active_list = None
    match key:
        case "allow_auto_edit_resume":
            draft.allow_auto_edit_resume = _parse_bool(path, line_number, value.strip())
        case "require_doctor_pass":
            draft.require_doctor_pass = _parse_bool(path, line_number, value.strip())
        case "block_on":
            _reject_inline_list_value(path, line_number, value)
            draft.active_list = "block_on"
        case "forbidden_claim_changes":
            _reject_inline_list_value(path, line_number, value)
            draft.active_list = "forbidden_claim_changes"
        case _:
            raise _parse_error(path, line_number, f"unknown policy key: {key}")


def _policy_from_draft(path: Path, draft: PolicyDraft) -> SubmissionPolicy:
    if not draft.saw_root:
        raise PolicyParseError(path=path, message=f"missing {ROOT_KEY}")
    if draft.allow_auto_edit_resume is None:
        raise PolicyParseError(path=path, message="missing allow_auto_edit_resume")
    if draft.require_doctor_pass is None:
        raise PolicyParseError(path=path, message="missing require_doctor_pass")

    return SubmissionPolicy(
        allow_auto_edit_resume=draft.allow_auto_edit_resume,
        require_doctor_pass=draft.require_doctor_pass,
        block_on=tuple(draft.block_on),
        forbidden_claim_changes=tuple(draft.forbidden_claim_changes),
    )


def _append_policy_list_item(
    path: Path,
    line_number: int,
    item: str,
    draft: PolicyDraft,
) -> None:
    if draft.active_list is None:
        raise _parse_error(path, line_number, "list item without a list key")
    match draft.active_list:
        case "block_on":
            draft.block_on.append(_parse_blocker(path, line_number, item))
        case "forbidden_claim_changes":
            draft.forbidden_claim_changes.append(_parse_forbidden_change(path, line_number, item))


def _parse_bool(path: Path, line_number: int, value: str) -> bool:
    match value:
        case "true":
            return True
        case "false":
            return False
        case _:
            raise _parse_error(path, line_number, f"expected true or false, got {value}")


def _parse_blocker(path: Path, line_number: int, item: str) -> PolicyBlocker:
    match item:
        case "malformed_ledger":
            return "malformed_ledger"
        case "needs_evidence":
            return "needs_evidence"
        case "too_broad":
            return "too_broad"
        case "rewrite_needed":
            return "rewrite_needed"
        case _:
            raise _parse_error(path, line_number, f"unknown policy blocker: {item}")


def _parse_forbidden_change(path: Path, line_number: int, item: str) -> ForbiddenClaimChange:
    match item:
        case "add_metric":
            return "add_metric"
        case "add_employer":
            return "add_employer"
        case "add_date":
            return "add_date"
        case "strengthen_scope":
            return "strengthen_scope"
        case _:
            raise _parse_error(path, line_number, f"unknown forbidden claim change: {item}")


def _reject_inline_list_value(path: Path, line_number: int, value: str) -> None:
    if value.strip() != "":
        raise _parse_error(path, line_number, "list values must use indented - items")


def _append_count_violation(violations: list[str], blocker: PolicyBlocker, count: int) -> None:
    if count > 0:
        violations.append(f"{blocker}: {count}")


def _parse_error(path: Path, line_number: int, message: str) -> PolicyParseError:
    return PolicyParseError(path=path, message=f"line {line_number}: {message}")
