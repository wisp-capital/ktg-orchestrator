#!/usr/bin/env python3
"""Print the AI-max startup snapshot for ktg-orchestrator."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from tools.startup_worktrees import load_worktree_state
except ModuleNotFoundError:  # Direct execution: python3 tools/startup_snapshot.py
    from startup_worktrees import load_worktree_state

AI_MAX_REMINDERS = Path("/Users/alexcstark/repos/ai-max/scripts/due_reminders.py")


def split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_markdown_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def read_section(lines: list[str], heading: str) -> list[str]:
    wanted = f"## {heading}".lower()
    start = None
    for index, line in enumerate(lines):
        stripped = line.strip().lower()
        if stripped == wanted or stripped.startswith(f"{wanted} "):
            start = index + 1
            break
    if start is None:
        return []

    section: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        section.append(line)
    return section


def parse_table(section_lines: list[str]) -> list[dict[str, str]]:
    rows = [line for line in section_lines if line.strip().startswith("|")]
    if len(rows) < 2:
        return []
    headers = split_markdown_row(rows[0])
    data_rows = rows[2:] if is_table_separator(rows[1]) else rows[1:]

    parsed: list[dict[str, str]] = []
    for row in data_rows:
        values = split_markdown_row(row)
        if len(values) != len(headers):
            continue
        parsed.append(dict(zip(headers, values, strict=True)))
    return parsed


def load_status_lines(root: Path) -> list[str]:
    status = root / "STATUS.md"
    if not status.exists():
        return []
    return status.read_text(encoding="utf-8").splitlines()


def load_status_table(root: Path, heading: str) -> list[dict[str, str]]:
    rows = parse_table(read_section(load_status_lines(root), heading))
    return [row for row in rows if row.get("ID")]


def load_decisions_needed(root: Path) -> list[str]:
    section = read_section(load_status_lines(root), "Decisions needed")
    decisions = [line.strip() for line in section if line.strip().startswith("- ")]
    return [] if decisions == ["- [none]"] else decisions


def parse_field_file(path: Path) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip().lower()] = value.strip()
    return fields


def is_expired(expires: str) -> bool:
    if not expires:
        return False
    try:
        return datetime.fromisoformat(expires) <= datetime.now().astimezone()
    except (TypeError, ValueError):
        return False


def render_lock_dir(lock_dir: Path) -> str | None:
    lock_file = lock_dir / "info.txt"
    if not lock_file.exists():
        lock_file = lock_dir / "LOCK.md"
    if not lock_file.exists():
        return None

    fields = parse_field_file(lock_file)
    expires = fields.get("expires", "")
    if is_expired(expires):
        return None

    parts = [f"agent {fields.get('agent') or fields.get('owner', 'unknown')}"]
    if fields.get("taken"):
        parts.append(f"taken {fields['taken']}")
    if expires:
        parts.append(f"expires {expires}")
    parts.append(f"scope: {fields.get('scope', 'unspecified')}")
    initiative_id = fields.get("initiative", lock_dir.name.removesuffix(".lock"))
    return f"- `{initiative_id}` - {'; '.join(parts)}"


def load_live_locks(root: Path) -> list[str]:
    locks_dir = root / ".initiative-locks"
    if not locks_dir.exists():
        return []

    locks: list[str] = []
    for lock_dir in sorted(locks_dir.glob("*.lock")):
        if lock_dir.is_dir():
            lock = render_lock_dir(lock_dir)
            if lock is not None:
                locks.append(lock)
    return locks


def todo_id(text: str, used_ids: set[str]) -> str:
    words = re.findall(r"[a-z0-9]+", text.lower())
    base = "-".join(words[:4]) or "todo"
    candidate = base
    suffix = 2
    while candidate in used_ids:
        candidate = f"{base}-{suffix}"
        suffix += 1
    used_ids.add(candidate)
    return candidate


def load_session_todos(root: Path) -> list[str]:
    todo_file = root / "SESSION_TODO.md"
    if not todo_file.exists():
        return []

    used_ids: set[str] = set()
    todos: list[str] = []
    for line in todo_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("- [ ] "):
            continue
        text = stripped.removeprefix("- [ ] ").strip()
        if re.match(r"^[a-z0-9][a-z0-9-]*:", text):
            used_ids.add(text.split(":", 1)[0])
            todos.append(stripped)
            continue
        todos.append(f"- [ ] {todo_id(text, used_ids)}: {text}")
    return todos


def run_command(cmd: list[str], cwd: Path) -> str:
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        return f"unavailable ({message})"
    return result.stdout.strip()


def run_due_reminders(root: Path) -> str:
    if not AI_MAX_REMINDERS.exists():
        return ""
    return run_command(["python3", str(AI_MAX_REMINDERS)], root)


def load_git_state(root: Path) -> str:
    return run_command(["git", "status", "--short", "--branch"], root) or "clean"


def append_section(lines: list[str], title: str, rows: list[str]) -> None:
    lines.append(title)
    lines.extend(rows or ["- None"])


def render_program(row: dict[str, str]) -> str:
    return (
        f"- `{row.get('ID', '')}` - {row.get('Name', '')}; "
        f"status {row.get('Status', '')}; maturity {row.get('Maturity', '')}; "
        f"repos {row.get('Linked repos', '')}; child {row.get('Active child', '')}; "
        f"blocked: {row.get('Blocked?', '')}; next: {row.get('Next Action', '')}"
    )


def render_initiative(row: dict[str, str]) -> str:
    depth = row.get("Depth") or row.get("Type") or row.get("Classification", "")
    stage = row.get("Stage") or row.get("Phase", "")
    next_action = row.get("Next action") or row.get("Next Action", "")
    parts = [
        f"`{row.get('ID', '')}` - {row.get('Name', '')}",
        f"depth {depth}" if depth else "",
        f"stage {stage}" if stage else "",
        f"maturity {row.get('Maturity', '')}",
        f"repos {row.get('Linked repos', '')}" if row.get("Linked repos") else "",
        f"blocked: {row.get('Blocked?', '')}" if row.get("Blocked?") else "",
        f"next: {next_action}" if next_action else "",
    ]
    return "- " + "; ".join(part for part in parts if part)


def render_snapshot(root: Path, reminder_text: str | None = None) -> str:
    reminders = (
        run_due_reminders(root) if reminder_text is None else reminder_text.strip()
    )
    programs = load_status_table(root, "Active programs")
    active = load_status_table(root, "Active initiatives")
    queued = load_status_table(root, "Queued initiatives")
    scheduled = load_status_table(root, "Scheduled initiatives")
    decisions = load_decisions_needed(root)
    locks = load_live_locks(root)
    todos = load_session_todos(root)

    lines = ["**Startup Snapshot**"]
    append_section(lines, "**Due Reminders**", [reminders] if reminders else [])
    append_section(lines, "**Active Programs**", [render_program(row) for row in programs])
    append_section(lines, "**Active Initiatives**", [render_initiative(row) for row in active])
    append_section(lines, "**Queued Initiatives**", [render_initiative(row) for row in queued])
    append_section(
        lines,
        "**Scheduled Initiatives**",
        [render_initiative(row) for row in scheduled],
    )
    append_section(lines, "**Decisions Needed**", decisions)
    append_section(lines, "**Live Locks**", locks)
    append_section(lines, "**Session Todos**", todos)

    lines.extend(["**Git State**", "```text", load_git_state(root), "```"])
    lines.extend(["**Worktrees**", "```text", load_worktree_state(root), "```"])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="state repo root")
    parser.add_argument("--write", type=Path, help="also write the snapshot to this file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = args.root.expanduser().resolve()
    snapshot = render_snapshot(root)
    if args.write:
        args.write.expanduser().write_text(snapshot, encoding="utf-8")
    sys.stdout.write(snapshot)


if __name__ == "__main__":
    main()
