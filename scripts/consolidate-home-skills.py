#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


TOOL_ROOTS = {
    "claude": Path("~/.claude/skills").expanduser(),
    "codex": Path("~/.codex/skills").expanduser(),
}
SHARED_ROOT = Path("~/.agents/skills").expanduser()
EXCLUDED_NAMES = {".DS_Store", ".system", "learned"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Consolidate Claude/Codex skill directories into ~/.agents/skills and link both tools back to the shared path."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show planned actions without changing the filesystem.",
    )
    parser.add_argument(
        "--backup-root",
        default=str(Path("~/.agents/skill-migration-backups").expanduser()),
        help="Directory used to store backed-up duplicate skill directories.",
    )
    return parser.parse_args()


def is_skill_dir(path: Path) -> bool:
    return path.exists() and path.is_dir() and (path / "SKILL.md").exists()


def same_target(path: Path, target: Path) -> bool:
    return path.is_symlink() and path.resolve() == target.resolve()


def log(message: str) -> None:
    print(message)


def backup_path(root: Path, tool: str, name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return root / timestamp / tool / name


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    else:
        shutil.rmtree(path)


def ensure_symlink(link_path: Path, target: Path, dry_run: bool) -> None:
    if same_target(link_path, target):
        log(f"ok    {link_path} -> {target}")
        return

    if link_path.exists() or link_path.is_symlink():
        if dry_run:
            log(f"rm    {link_path}")
        else:
            remove_path(link_path)

    if dry_run:
        log(f"link  {link_path} -> {target}")
        return

    link_path.parent.mkdir(parents=True, exist_ok=True)
    link_path.symlink_to(target)
    log(f"link  {link_path} -> {target}")


def move_dir(src: Path, dst: Path, dry_run: bool) -> None:
    if dry_run:
        log(f"move  {src} -> {dst}")
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    log(f"move  {src} -> {dst}")


def backup_dir(src: Path, dst: Path, dry_run: bool) -> None:
    if dry_run:
        log(f"backup {src} -> {dst}")
        return

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    log(f"backup {src} -> {dst}")


def discover_shared_names() -> set[str]:
    names: set[str] = set()
    if not SHARED_ROOT.exists():
        return names
    for entry in SHARED_ROOT.iterdir():
        if entry.name in EXCLUDED_NAMES or entry.name.startswith("."):
            continue
        if is_skill_dir(entry):
            names.add(entry.name)
    return names


def discover_tool_names() -> set[str]:
    names: set[str] = set()
    for root in TOOL_ROOTS.values():
        if not root.exists():
            continue
        for entry in root.iterdir():
            if entry.name in EXCLUDED_NAMES or entry.name.startswith("."):
                continue
            if is_skill_dir(entry):
                names.add(entry.name)
    return names


def main() -> int:
    args = parse_args()
    backup_root = Path(args.backup_root).expanduser()
    SHARED_ROOT.mkdir(parents=True, exist_ok=True)
    for root in TOOL_ROOTS.values():
        root.mkdir(parents=True, exist_ok=True)

    skill_names = sorted(discover_shared_names() | discover_tool_names())
    if not skill_names:
        log("No consolidatable skills found.")
        return 0

    for name in skill_names:
        shared_path = SHARED_ROOT / name
        locations = {tool: root / name for tool, root in TOOL_ROOTS.items()}

        if not is_skill_dir(shared_path):
            chosen_tool = None
            for tool in ("codex", "claude"):
                candidate = locations[tool]
                if is_skill_dir(candidate) and not candidate.is_symlink():
                    chosen_tool = tool
                    move_dir(candidate, shared_path, args.dry_run)
                    break
            if chosen_tool is None:
                continue

        if not is_skill_dir(shared_path):
            continue

        for tool, location in locations.items():
            if same_target(location, shared_path):
                log(f"ok    {location} -> {shared_path}")
                continue

            if is_skill_dir(location) and not location.is_symlink():
                backup_dir(location, backup_path(backup_root, tool, name), args.dry_run)

            ensure_symlink(location, shared_path, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
