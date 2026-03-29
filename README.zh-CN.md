# OpenClaw Dev Orchestrator

一个给 OpenClaw 使用的编程编排技能。

它的默认工作方式是：

- OpenClaw 负责需求确认、用户审批、部署确认、最终通知
- Claude Code 负责实现、测试、架构设计
- Codex 只作为兜底或第二意见使用

## 这个技能做什么

这个技能让 OpenClaw 可以充当软件开发任务的调度层：

- 用户先在 OpenClaw 里提出需求
- OpenClaw 先确认范围、约束、验收标准
- OpenClaw 把实现任务下发给 Claude Code
- Claude Code 完成编码、测试和设计工作
- 如果还有顽固 bug，或者用户明确要求双保险，再交给 Codex
- 部署前仍然由 OpenClaw 和用户确认部署方式与目标环境
- 完成后由 OpenClaw 把结果发送给指定用户或通知群

## 默认职责分工

### Claude Code

- 新功能开发
- 主要代码修改和重构
- 开发过程中的测试执行与修复
- 架构设计和实现方案落地
- 按 `openspec` 或仓库本地规范工作

### Codex

- Claude Code 已尝试但仍未解决的 bug 修复
- 用户明确要求的第二意见审查
- 高风险改动的安全复核

## 仓库内容

- `SKILL.md`
  技能本体说明，供 OpenClaw 触发和使用
- `scripts/doctor.sh`
  检查本机是否已安装 `claude`、`codex`、`python3`
- `scripts/dispatch_task.py`
  负责把任务简报打包并下发给 Claude Code 或 Codex
- `references/prompt-contracts.md`
  各阶段的任务提示词契约
- `references/platform-notes.md`
  Lark/Feishu、Telegram 等平台接入和审批注意事项

## 安装方式

把技能目录复制到 OpenClaw 能发现的位置，例如：

```bash
cp -R openclaw-dev-orchestrator ~/.agents/skills/
```

然后把技能名加入目标 agent 的 `skills` 列表中，比如 `master-controller`。

## 运行前提

- OpenClaw
- Claude Code CLI，且已完成登录
- Codex CLI，且已完成登录
- Python 3

可选但推荐：

- 仓库或用户目录里有 `openspec`
- Claude Code 和 Codex 本地已有额外技能目录

## 基本用法

### 1. 检查环境

```bash
SKILL_DIR=/path/to/openclaw-dev-orchestrator
bash "$SKILL_DIR/scripts/doctor.sh"
```

### 2. 下发实现任务给 Claude Code

```bash
SKILL_DIR=/path/to/openclaw-dev-orchestrator
python3 "$SKILL_DIR/scripts/dispatch_task.py" \
  --executor claude \
  --phase implement \
  --workspace /abs/path/to/repo \
  --task-text "Implement the approved feature. Follow openspec if present."
```

### 3. 把残留 bug 升级给 Codex

```bash
SKILL_DIR=/path/to/openclaw-dev-orchestrator
python3 "$SKILL_DIR/scripts/dispatch_task.py" \
  --executor codex \
  --phase fallback-fix \
  --workspace /abs/path/to/repo \
  --task-text "Claude Code already attempted this bug. Reproduce it, fix it if possible, and summarize what blocked the first pass."
```

### 4. 先 dry-run 看任务包

```bash
python3 "$SKILL_DIR/scripts/dispatch_task.py" \
  --executor codex \
  --phase safety-review \
  --workspace /abs/path/to/repo \
  --task-text "Review this risky change for release readiness." \
  --dry-run
```

## 推荐工作模式

- 默认总是先交给 Claude Code
- 不要把普通的一线实现直接交给 Codex
- Codex 主要承担：
  - 难 bug 兜底
  - 风险变更复核
  - 用户明确要求的第二意见
- 部署确认始终放在 OpenClaw
- 面向用户的需求确认始终放在 OpenClaw

## 安全说明

这个公开仓库已经做过脱敏处理：

- 不包含本地 OpenClaw 配置
- 不包含 token
- 不包含个人绝对路径
- 不包含会话历史

公开出去的只有技能本身需要的可复用文件。

## 仓库地址

- [dentes9988/openclaw-dev-orchestrator](https://github.com/dentes9988/openclaw-dev-orchestrator)
