# OpenClaw Dev Orchestrator

An OpenClaw skill for routing software delivery work through a Claude Code first workflow, with Codex used only as a fallback or second-opinion pass.

## What It Does

This skill helps OpenClaw act as the orchestration layer for coding tasks:

- OpenClaw handles requirement clarification, user approvals, deployment confirmation, and final notifications
- Claude Code handles implementation, testing, and architecture design
- Codex is used only when:
  - you explicitly want a second-opinion review, or
  - Claude Code already tried and a bug still remains

This makes the workflow closer to:

1. User talks to OpenClaw
2. OpenClaw confirms scope and constraints
3. OpenClaw dispatches implementation to Claude Code
4. Claude Code completes code, tests, and design work
5. OpenClaw escalates to Codex only if needed
6. OpenClaw confirms deployment details with the user
7. OpenClaw sends a completion summary to the chosen notification channel

## Included Files

- `SKILL.md`
  The actual OpenClaw skill instructions
- `scripts/doctor.sh`
  Checks whether `claude`, `codex`, and `python3` are available
- `scripts/dispatch_task.py`
  Packages and dispatches a task brief to Claude Code or Codex
- `references/prompt-contracts.md`
  Prompt templates for implementation, fallback fixes, safety review, and deployment
- `references/platform-notes.md`
  Notes for Lark/Feishu, Telegram, and platform approval flows

## Install

Copy the skill into a directory that OpenClaw can discover, for example:

```bash
cp -R openclaw-dev-orchestrator ~/.agents/skills/
```

Then add the skill name to the relevant OpenClaw agent config, for example the `master-controller` agent inside `openclaw.json`.

## Requirements

- OpenClaw
- Claude Code CLI installed and authenticated
- Codex CLI installed and authenticated
- Python 3

Optional but useful:

- `openspec` in the repository or home directory
- local skill directories for Claude Code and Codex

## Usage

### 1. Check the environment

```bash
SKILL_DIR=/path/to/openclaw-dev-orchestrator
bash "$SKILL_DIR/scripts/doctor.sh"
```

### 2. Dispatch implementation to Claude Code

```bash
SKILL_DIR=/path/to/openclaw-dev-orchestrator
python3 "$SKILL_DIR/scripts/dispatch_task.py" \
  --executor claude \
  --phase implement \
  --workspace /abs/path/to/repo \
  --task-text "Implement the approved feature. Follow openspec if present."
```

### 3. Escalate a remaining bug to Codex

```bash
SKILL_DIR=/path/to/openclaw-dev-orchestrator
python3 "$SKILL_DIR/scripts/dispatch_task.py" \
  --executor codex \
  --phase fallback-fix \
  --workspace /abs/path/to/repo \
  --task-text "Claude Code already attempted this bug. Reproduce it, fix it if possible, and summarize what blocked the first pass."
```

### 4. Preview a dispatch without executing

```bash
python3 "$SKILL_DIR/scripts/dispatch_task.py" \
  --executor codex \
  --phase safety-review \
  --workspace /abs/path/to/repo \
  --task-text "Review this risky change for release readiness." \
  --dry-run
```

## Recommended Operating Model

- Use Claude Code first for almost all development tasks
- Keep Codex as:
  - a fallback fixer for unresolved bugs
  - a safety review pass for risky releases
- Keep deployment confirmation inside OpenClaw
- Keep user-facing requirement clarification inside OpenClaw

## Security and Publishing Notes

This public repo is intentionally sanitized:

- no local OpenClaw config
- no tokens
- no personal absolute paths
- no session history

Only the reusable skill assets are included.

## Repository

Public repo:

- [dentes9988/openclaw-dev-orchestrator](https://github.com/dentes9988/openclaw-dev-orchestrator)
