#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_SKILLS_DIR="${ROOT_DIR}/skills"
SHARED_SKILLS_ROOT="${SHARED_SKILLS_ROOT:-${HOME}/.agents/skills}"
CLAUDE_SKILLS_ROOT="${CLAUDE_SKILLS_ROOT:-${HOME}/.claude/skills}"
CODEX_SKILLS_ROOT="${CODEX_SKILLS_ROOT:-${HOME}/.codex/skills}"
FORCE=0

if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
fi

resolve_path() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys

print(Path(sys.argv[1]).resolve())
PY
}

ensure_link() {
  local target="$1"
  local link_path="$2"

  if [[ -L "$link_path" ]]; then
    local current_target desired_target
    current_target="$(resolve_path "$link_path")"
    desired_target="$(resolve_path "$target")"
    if [[ "$current_target" == "$desired_target" ]]; then
      printf 'ok    %s -> %s\n' "$link_path" "$target"
      return 0
    fi
    rm "$link_path"
  elif [[ -e "$link_path" ]]; then
    if [[ "$FORCE" -eq 1 ]]; then
      rm -rf "$link_path"
    else
      printf 'skip  %s exists and is not a symlink\n' "$link_path" >&2
      return 1
    fi
  fi

  ln -s "$target" "$link_path"
  printf 'link  %s -> %s\n' "$link_path" "$target"
}

mkdir -p "$SHARED_SKILLS_ROOT" "$CLAUDE_SKILLS_ROOT" "$CODEX_SKILLS_ROOT"

for skill_dir in "$REPO_SKILLS_DIR"/*; do
  [[ -d "$skill_dir" ]] || continue

  skill_name="$(basename "$skill_dir")"
  shared_link="${SHARED_SKILLS_ROOT}/${skill_name}"
  claude_link="${CLAUDE_SKILLS_ROOT}/${skill_name}"
  codex_link="${CODEX_SKILLS_ROOT}/${skill_name}"

  ensure_link "$skill_dir" "$shared_link" || true
  ensure_link "$shared_link" "$claude_link" || true
  ensure_link "$shared_link" "$codex_link" || true
done
