# Repository Guidelines

## Project Structure & Module Organization

This repository ships reusable testing skills, not an application build. Put contributor-facing changes in the existing layout:

- `skills/<skill-name>/`: one skill per directory, with `SKILL.md` as the source of truth.
- `skills/<skill-name>/assets/`: output templates such as Hurl, k6, or Markdown skeletons.
- `skills/<skill-name>/references/`: supporting guidance used by the skill workflow.
- `skills/<skill-name>/agents/openai.yaml`: optional Codex UI metadata.
- `scripts/`: shared maintenance helpers for linking skills and syncing MCP config.
- `assets/`: repository images for README and catalog use.
- `.mcp.json`: shared MCP source consumed directly by Claude Code and mapped into Codex config.

## Build, Test, and Development Commands

There is no compiled build. Use the helper scripts directly:

- `./scripts/bootstrap-shared-agent-capabilities.sh`: links repo skills into shared agent directories and syncs `.mcp.json` into Codex.
- `./scripts/link-shared-skills.sh`: refreshes skill symlinks under `~/.agents/skills`, `~/.claude/skills`, and `~/.codex/skills`.
- `python3 ./scripts/sync-codex-mcp.py --mcp-file ./.mcp.json --dry-run`: preview Codex MCP changes before writing `~/.codex/config.toml`.
- `python3 ./scripts/consolidate-home-skills.py --dry-run`: inspect home-directory skill consolidation without modifying files.
- `python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/test-case-creator`: validate a changed skill; rerun for each touched skill directory.

## Coding Style & Naming Conventions

Use Python 3 with 4-space indentation, type hints, and `pathlib` for filesystem work. Shell scripts should remain POSIX-friendly Bash with `set -euo pipefail`. Keep Markdown concise and operational. Name skill directories in kebab-case, and keep template/reference filenames lowercase with hyphens. Follow existing output naming such as `tests/{yyMMdd}_{requirement_slug}/`.

## Testing Guidelines

No coverage gate is checked in, so contributors must validate what they change. Run `quick_validate.py` for every edited skill. For Python helpers, prefer `--dry-run` smoke checks where supported before real writes. Do not commit generated test outputs, local cache directories, or home-directory backups.

## Commit & Pull Request Guidelines

Recent history favors short imperative subjects, usually Conventional Commit style: `docs: ...`, `refactor: ...`, `chore: ...`. Keep commits focused on one skill or maintenance task. PRs should state which skill or script changed, note any dependency on `playwright-interactive` or shared MCP setup, and include example prompts or output paths when behavior changes. Attach screenshots only when updating repository imagery or UI-facing assets.

## Security & Configuration Tips

Treat `~/.agents/skills` as the shared source of truth and keep mirrors symlinked. Never commit secrets, private MCP endpoints, or generated artifacts from local home directories. When editing `.mcp.json`, stay within the supported shared subset (`stdio` with `command/args/env/cwd`, or `http` with `url`).
