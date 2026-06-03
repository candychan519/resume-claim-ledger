# README Check UltraQA Notes

| Class | Result |
| --- | --- |
| Malformed input | Probed with `ulw-qa-readme-malformed`; report transcript includes `Malformed ledger` and `malformed_PASS`. |
| Prompt injection | Not applicable: README check does not accept prompt text or call an LLM. |
| Cancel/resume | Not applicable to the CLI behavior under test; no resumable job is created. |
| Stale state | Probed by starting from `main...origin/main`, then creating `codex/readme-check-execution`; final status is checked before commit. |
| Dirty worktree | Probed with `git status --short --branch` before edits and final diff review before commit. |
| Hung or long commands | Probed during tmux QA; an initial command wrapping attempt timed out, sessions were checked and corrected with PowerShell tmux transcripts. |
| Flaky tests | Probed with targeted RED/GREEN and full `pytest` gate. |
| Misleading success output | Probed by checking generated files and transcript PASS markers, not CLI success messages alone. |
| Repeated interruptions | One tmux timeout recovery occurred; the corrected run produced all six PASS transcripts and cleanup receipt. |
