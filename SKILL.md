---
name: openclaw-dev-orchestrator
description: >
  Orchestrate software delivery tasks from OpenClaw by confirming requirements
  with the user, dispatching implementation, testing, and architecture design
  work to the local Claude Code CLI, optionally escalating only unresolved bugs
  or second-opinion safety checks to the local Codex CLI, coordinating
  deployment approval, and sending completion notifications. Use when the user
  asks OpenClaw to build a feature, modify code, create a coding task, hand
  work to Claude Code first, request a Codex backup pass, escalate a stubborn
  bug to Codex, or deploy after confirmation. Triggers: "帮我开发", "开始编码",
  "交给 Claude Code", "Claude 先做", "Codex 兜底", "难 bug 交给 Codex",
  "部署这个服务", "需求确认后开始开发".
---

# OpenClaw Dev Orchestrator

Coordinate a coding task across OpenClaw, Claude Code, and Codex. Keep user-facing clarification, approval, deployment confirmation, and final notifications inside OpenClaw. Use Claude Code as the primary engineer for implementation, testing, and architecture design. Use Codex only as a backup reviewer or for bugs Claude Code could not close.

## Workflow

1. Confirm the task in OpenClaw.
2. Dispatch implementation, testing, and architecture design to Claude Code.
3. Ask Claude Code to finish with passing checks or a precise blocker report.
4. Dispatch to Codex only if the user asks for a second-opinion pass or Claude Code cannot close a bug.
5. Ask the user to confirm deployment method and environment in OpenClaw before any deploy action.
6. Send the completion summary to the requested user or group channel after the work is done.

## Phase Split

Use this split unless the user explicitly requests a different arrangement.

- `Claude Code`
  - New feature implementation
  - Most code generation and refactors
  - Test execution and iterative fixes during implementation
  - Architecture design and implementation planning
  - Following `openspec` or repo-local specs during build work
- `Codex`
  - Second-opinion review when the user wants extra assurance
  - Hard bug-fix escalation after Claude Code already tried and reported the blocker
  - Optional release-risk review on explicitly risky changes

## Before Dispatch

Do not dispatch work until the OpenClaw conversation has enough information to execute safely.

Collect or confirm:

- Repository or workspace path
- Goal and acceptance criteria
- Constraints: stack, branch policy, coding rules, deadlines
- Whether deployment is in scope
- Deployment target and method if deployment is requested
- Notification target: user DM, Telegram group, Lark/Feishu chat, or another approved channel

If deployment or platform installation is involved, read [references/platform-notes.md](./references/platform-notes.md) before acting.

## Required Execution Rules

- Keep requirement clarification, deployment confirmation, and user approval in OpenClaw.
- Do not let Claude Code or Codex choose a deployment target without explicit user confirmation in OpenClaw.
- Prefer repo-local instructions first: `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `README.md`, local test configs, and CI files.
- If `openspec` exists in the repo or user home, instruct Claude Code and Codex to use it. If not found, continue with repo-local guidance.
- When dispatching to Claude Code or Codex, pass a complete task brief instead of a vague one-line prompt.
- Store temporary orchestration artifacts under `/tmp/openclaw-dev-orchestrator/`, not in the agent workspace.
- Default to Claude Code first. Do not send routine implementation or first-pass testing to Codex unless the user explicitly asks.

## How to Dispatch

Run the environment check first:

```bash
SKILL_DIR=/path/to/openclaw-dev-orchestrator
bash "$SKILL_DIR/scripts/doctor.sh"
```

Then dispatch a phase with the helper script:

```bash
SKILL_DIR=/path/to/openclaw-dev-orchestrator
python3 "$SKILL_DIR/scripts/dispatch_task.py" \
  --executor claude \
  --phase implement \
  --workspace /abs/path/to/repo \
  --task-text "Implement the approved feature. Follow openspec if present."
```

```bash
SKILL_DIR=/path/to/openclaw-dev-orchestrator
python3 "$SKILL_DIR/scripts/dispatch_task.py" \
  --executor codex \
  --phase fallback-fix \
  --workspace /abs/path/to/repo \
  --task-text "Claude Code already attempted this bug. Reproduce it, fix it if possible, and summarize what blocked the first pass."
```

Use `--dry-run` first if the task packaging is complex or risky.

## Task Brief Contract

Every dispatch brief should include:

- User-approved objective
- Repository path
- Acceptance criteria
- Out-of-scope items
- Whether deployment is allowed
- Notification target after completion
- Request to honor `openspec` and local repo guidance if found

Use [references/prompt-contracts.md](./references/prompt-contracts.md) when you need detailed prompt wording for each phase.

## Deployment

Deployment is a separate phase, not part of implementation by default.

Before deployment:

- Ask the user to confirm the environment and method in OpenClaw
- Confirm secrets, credentials, and permissions are already available
- If the destination is Lark/Feishu app installation, validate permissions and tenant approval requirements first

Only after that, dispatch a deploy phase with a task brief that includes the exact approved deployment method.

## Notifications

After the work finishes:

- Summarize what Claude Code implemented, tested, and designed
- State whether Codex was used as backup and why
- Summarize what was fixed, reviewed, and deployed
- Include remaining risks or manual follow-ups
- Send the summary to the requested user or notification group through OpenClaw’s messaging flow

If the user requested Lark/Feishu installation or notification, read [references/platform-notes.md](./references/platform-notes.md) first.
