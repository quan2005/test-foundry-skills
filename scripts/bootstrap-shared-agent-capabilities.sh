#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"${ROOT_DIR}/scripts/link-shared-skills.sh"
python3 "${ROOT_DIR}/scripts/sync-codex-mcp.py" --mcp-file "${ROOT_DIR}/.mcp.json"
