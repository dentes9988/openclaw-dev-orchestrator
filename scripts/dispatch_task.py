#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from datetime import datetime
from pathlib import Path


TMP_ROOT = Path("/tmp/openclaw-dev-orchestrator")


PHASE_INSTRUCTIONS = {
    "implement": (
        "Use Claude Code for implementation work. Modify the repository to satisfy the "
        "approved requirements, perform the needed architecture design, follow openspec if "
        "found, and run focused validation for the changed code. Do not deploy."
    ),
    "fallback-fix": (
        "Use Codex only as a fallback after Claude Code already attempted the work. "
        "Reproduce the unresolved issue, fix it if possible, and explain what blocked the "
        "first pass. Do not deploy."
    ),
    "safety-review": (
        "Use Codex as a second-opinion safety pass. Review the implementation and project "
        "structure for concrete risks, missing tests, scaling concerns, and release-readiness issues."
    ),
    "deploy": (
        "Deploy only with the exact user-approved method and target environment provided in "
        "this brief. If anything is missing, stop and report the gap."
    ),
}


def detect_candidates(workspace: Path) -> dict[str, list[str]]:
    candidates = {"openspec": [], "claude_skills": [], "codex_skills": []}

    for root in [workspace, Path.home()]:
        if not root.exists():
            continue
        for name in [".openspec", "openspec", "OPENSPEC.md", "openspec.md"]:
            candidate = root / name
            if candidate.exists():
                candidates["openspec"].append(str(candidate))

    for path in [Path.home() / ".claude" / "skills", Path.home() / ".codex" / "skills"]:
        if path.exists():
            key = "claude_skills" if ".claude" in str(path) else "codex_skills"
            candidates[key].append(str(path))

    return candidates


def build_prompt(args: argparse.Namespace, candidates: dict[str, list[str]]) -> str:
    task_text = args.task_text
    if args.task_file:
        task_text = Path(args.task_file).read_text()

    candidate_lines = []
    if candidates["openspec"]:
        candidate_lines.append("openspec candidates:\n- " + "\n- ".join(candidates["openspec"]))
    if candidates["claude_skills"]:
        candidate_lines.append("Claude skills path:\n- " + "\n- ".join(candidates["claude_skills"]))
    if candidates["codex_skills"]:
        candidate_lines.append("Codex skills path:\n- " + "\n- ".join(candidates["codex_skills"]))

    extras = "\n".join(candidate_lines) if candidate_lines else "No openspec or skill directory candidates were auto-detected."
    add_dirs = ", ".join(args.add_dir) if args.add_dir else "(none)"

    return textwrap.dedent(
        f"""\
        OpenClaw dispatched this task.

        Executor: {args.executor}
        Phase: {args.phase}
        Repository: {args.workspace}
        Extra writable dirs: {add_dirs}
        Notification target: {args.notify_target or "(not specified)"}
        Deployment allowed: {"yes" if args.allow_deploy else "no"}

        Phase instructions:
        {PHASE_INSTRUCTIONS[args.phase]}

        Tooling and spec context:
        {extras}

        Shared requirements:
        - Honor repo-local instructions first: AGENTS.md, CLAUDE.md, CODEX.md, README.md, CI files, and test configs.
        - If openspec exists, use it. Otherwise continue with repo-local guidance.
        - Stop and report exact blockers instead of guessing missing product or deployment details.
        - Keep the final response concise and action-oriented.

        Approved task brief:
        {task_text.strip()}
        """
    ).strip()


def build_command(args: argparse.Namespace, prompt: str) -> list[str]:
    if args.executor == "claude":
        command = [
            "claude",
            "-p",
            "--permission-mode",
            "auto",
            "--add-dir",
            args.workspace,
        ]
        for add_dir in args.add_dir:
            command.extend(["--add-dir", add_dir])
        command.append(prompt)
        return command

    command = [
        "codex",
        "exec",
        "-C",
        args.workspace,
        "-a",
        "never",
        "-s",
        "workspace-write",
        prompt,
    ]
    for add_dir in args.add_dir:
        command.extend(["--add-dir", add_dir])
    return command


def ensure_binary(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required binary: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dispatch a coding phase to Claude Code or Codex.")
    parser.add_argument("--executor", choices=["claude", "codex"], required=True)
    parser.add_argument("--phase", choices=["implement", "fallback-fix", "safety-review", "deploy"], required=True)
    parser.add_argument("--workspace", required=True, help="Absolute repo/workspace path")
    parser.add_argument("--task-text", help="Inline task brief")
    parser.add_argument("--task-file", help="Path to a file containing the task brief")
    parser.add_argument("--notify-target", help="OpenClaw notification target after completion")
    parser.add_argument("--allow-deploy", action="store_true", help="Mark deploy as explicitly approved")
    parser.add_argument("--add-dir", action="append", default=[], help="Additional writable dirs")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.task_text and not args.task_file:
        raise SystemExit("Provide either --task-text or --task-file.")

    workspace = Path(args.workspace).expanduser().resolve()
    if not workspace.exists():
        raise SystemExit(f"Workspace does not exist: {workspace}")
    args.workspace = str(workspace)

    ensure_binary(args.executor)

    candidates = detect_candidates(workspace)
    prompt = build_prompt(args, candidates)
    command = build_command(args, prompt)

    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = Path(tempfile.mkdtemp(prefix=f"{stamp}-{args.executor}-{args.phase}-", dir=TMP_ROOT))
    prompt_path = run_dir / "prompt.txt"
    prompt_path.write_text(prompt)
    log_path = run_dir / "run.log"

    result = {
        "executor": args.executor,
        "phase": args.phase,
        "workspace": args.workspace,
        "prompt_file": str(prompt_path),
        "log_file": str(log_path),
        "command": command,
        "dry_run": args.dry_run,
    }

    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    completed = subprocess.run(
        command,
        cwd=args.workspace,
        text=True,
        capture_output=True,
    )
    log_path.write_text(completed.stdout + ("\n" if completed.stdout and not completed.stdout.endswith("\n") else "") + completed.stderr)

    result.update(
        {
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-2000:],
        }
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(completed.returncode)


if __name__ == "__main__":
    main()
