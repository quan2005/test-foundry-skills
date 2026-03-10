#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


BEGIN_MARKER = "# BEGIN shared-mcp managed by sync-codex-mcp.py"
END_MARKER = "# END shared-mcp managed by sync-codex-mcp.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync project .mcp.json entries into ~/.codex/config.toml."
    )
    parser.add_argument(
        "--mcp-file",
        default=".mcp.json",
        help="Path to the shared .mcp.json source file.",
    )
    parser.add_argument(
        "--config-path",
        default="~/.codex/config.toml",
        help="Path to the Codex config.toml file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the managed TOML block without writing config.toml.",
    )
    return parser.parse_args()


def load_servers(mcp_file: Path) -> dict[str, dict]:
    data = json.loads(mcp_file.read_text())
    servers = data.get("mcpServers", data)
    if not isinstance(servers, dict):
        raise ValueError(f"{mcp_file} does not contain an MCP server map")
    return servers


def validate_server(name: str, server: dict) -> None:
    server_type = server.get("type", "stdio")

    if server_type == "stdio":
        if not server.get("command"):
            raise ValueError(f"{name}: stdio server requires 'command'")
        if "args" in server and not isinstance(server["args"], list):
            raise ValueError(f"{name}: stdio server 'args' must be an array")
        if "env" in server and not isinstance(server["env"], dict):
            raise ValueError(f"{name}: stdio server 'env' must be an object")
        if "headers" in server:
            raise ValueError(f"{name}: Codex sync does not support HTTP headers on stdio servers")
        return

    if server_type == "http":
        if not server.get("url"):
            raise ValueError(f"{name}: http server requires 'url'")
        if "headers" in server:
            raise ValueError(
                f"{name}: Codex sync does not support arbitrary HTTP headers from .mcp.json yet"
            )
        return

    raise ValueError(
        f"{name}: unsupported MCP type '{server_type}' for Codex sync; supported types are stdio and http"
    )


def toml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def render_servers(servers: dict[str, dict], source_path: Path) -> str:
    lines: list[str] = [
        BEGIN_MARKER,
        f"# Source: {source_path}",
    ]

    for name in sorted(servers):
        server = servers[name]
        server_type = server.get("type", "stdio")
        lines.append(f"[mcp_servers.{name}]")

        if server_type == "stdio":
            lines.append(f"command = {toml_quote(server['command'])}")
            args = server.get("args", [])
            lines.append(
                "args = [" + ", ".join(toml_quote(str(item)) for item in args) + "]"
            )
            cwd = server.get("cwd")
            if cwd:
                lines.append(f"cwd = {toml_quote(str(cwd))}")
            env = server.get("env", {})
            if env:
                lines.append(f"[mcp_servers.{name}.env]")
                for key in sorted(env):
                    lines.append(f"{key} = {toml_quote(str(env[key]))}")
        elif server_type == "http":
            lines.append(f"url = {toml_quote(server['url'])}")
            bearer = server.get("bearer_token_env_var") or server.get("bearerTokenEnvVar")
            if bearer:
                lines.append(f"bearer_token_env_var = {toml_quote(str(bearer))}")

        lines.append("")

    lines.append(END_MARKER)
    return "\n".join(lines).rstrip() + "\n"


def strip_managed_entries(text: str, names: set[str]) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0

    while index < len(lines):
        current = lines[index].rstrip("\n")

        if current == BEGIN_MARKER:
            index += 1
            while index < len(lines) and lines[index].rstrip("\n") != END_MARKER:
                index += 1
            if index < len(lines):
                index += 1
            while index < len(lines) and lines[index].strip() == "":
                index += 1
            continue

        matched_name = next(
            (
                name
                for name in names
                if current == f"[mcp_servers.{name}]"
            ),
            None,
        )
        if matched_name:
            index += 1
            same_prefix = f"[mcp_servers.{matched_name}"
            while index < len(lines):
                next_line = lines[index].rstrip("\n")
                if next_line.startswith("[") and next_line.endswith("]") and not next_line.startswith(same_prefix):
                    break
                index += 1
            while index < len(lines) and lines[index].strip() == "":
                index += 1
            continue

        output.append(lines[index])
        index += 1

    cleaned = "".join(output).rstrip() + "\n"
    if "[mcp_servers]" not in cleaned:
        cleaned += "\n[mcp_servers]\n"
    return cleaned


def main() -> int:
    args = parse_args()
    mcp_file = Path(args.mcp_file).expanduser().resolve()
    config_path = Path(args.config_path).expanduser()

    if not mcp_file.exists():
        raise FileNotFoundError(f"Shared MCP file not found: {mcp_file}")
    if not config_path.exists():
        raise FileNotFoundError(f"Codex config not found: {config_path}")

    servers = load_servers(mcp_file)
    for name, server in servers.items():
        if not isinstance(server, dict):
            raise ValueError(f"{name}: MCP config must be an object")
        validate_server(name, server)

    managed_block = render_servers(servers, mcp_file)
    if args.dry_run:
        sys.stdout.write(managed_block)
        return 0

    original = config_path.read_text()
    updated = strip_managed_entries(original, set(servers))
    if not updated.endswith("\n"):
        updated += "\n"
    updated = updated.rstrip() + "\n\n" + managed_block

    if updated == original:
        print(f"No change needed for {config_path}")
        return 0

    backup_path = config_path.with_name(
        f"{config_path.name}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    )
    shutil.copy2(config_path, backup_path)
    config_path.write_text(updated)
    print(f"Updated {config_path}")
    print(f"Backup written to {backup_path}")
    print("Managed servers: " + ", ".join(sorted(servers)))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
