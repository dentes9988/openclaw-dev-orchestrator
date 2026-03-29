#!/usr/bin/env bash
set -euo pipefail

echo "== binaries =="
for bin in claude codex python3; do
  if command -v "$bin" >/dev/null 2>&1; then
    printf "%s: %s\n" "$bin" "$(command -v "$bin")"
  else
    printf "%s: MISSING\n" "$bin"
  fi
done

echo
echo "== versions =="
if command -v claude >/dev/null 2>&1; then
  claude --version || true
fi
if command -v codex >/dev/null 2>&1; then
  codex --version || true
fi

echo
echo "== optional context =="
for dir in "$HOME/.claude/skills" "$HOME/.codex/skills"; do
  if [ -d "$dir" ]; then
    printf "%s: present\n" "$dir"
  else
    printf "%s: missing\n" "$dir"
  fi
done

for path in "$HOME/.openspec" "$HOME/openspec"; do
  if [ -e "$path" ]; then
    printf "%s: present\n" "$path"
  fi
done
