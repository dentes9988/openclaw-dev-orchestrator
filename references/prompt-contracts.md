# Prompt Contracts

Use these contracts to build the task brief sent from OpenClaw to Claude Code or Codex.

## Shared Header

Always include:

- Project path
- Approved task summary
- Acceptance criteria
- Constraints and prohibited actions
- Whether deployment is allowed
- Notification target after completion

Shared instruction:

```text
Honor repo-local instructions first: AGENTS.md, CLAUDE.md, CODEX.md, README.md, CI files, and local test configs. If openspec is present in the repo or home directory, use it. If not, continue with the repo's own guidance.
```

## Claude Code: Implement

Use for feature work and most code edits.

```text
Implement the approved task in the repository. Prefer small, coherent changes. Design the architecture needed for the feature, run focused validation that matches the modified code, and iterate until the agreed checks pass or you can name the exact blocker. Do not deploy. If requirements are ambiguous, stop and report the exact gap instead of guessing.
```

## Codex: Fallback Fix

Use only after Claude Code already attempted the task and either left a bug unresolved or the user explicitly asked for a second pass.

```text
Claude Code already attempted this task. Reproduce the remaining issue, fix it if possible, and summarize why the issue survived the first pass. Keep changes scoped to the unresolved bug or regression. Do not deploy unless the deploy phase is explicitly approved.
```

## Codex: Safety Review

Use only when the user explicitly wants a second-opinion review on a risky change.

```text
Review the current implementation and project structure for architecture risks, scaling concerns, test gaps, rollback risks, and release-readiness issues. Prefer concrete findings and recommended changes over broad theory.
```

## Deploy Phase

Use only after OpenClaw gets explicit user confirmation.

```text
Deploy using only the approved method and target environment provided in this brief. If the method is incomplete, stop and report the missing detail instead of improvising. After deployment, provide a concise verification summary and any rollback notes.
```

## Notification Summary

Final OpenClaw message should include:

- What changed
- What Claude Code handled
- Whether Codex was used and why
- What was tested
- Whether deployment happened
- Remaining risks or manual next steps
