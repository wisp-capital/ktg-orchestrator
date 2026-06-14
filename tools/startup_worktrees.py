#!/usr/bin/env python3
"""Worktree status helpers for KTG startup snapshots."""

from __future__ import annotations

import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path

MAX_WORKTREE_LINES = 120


@dataclass(frozen=True)
class WorktreeRow:
    session: str
    repo: str
    base: str
    assembled: str
    branch: str
    dirty: str
    ahead: str
    behind: str


def limit_lines(text: str, max_lines: int) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    hidden = len(lines) - max_lines
    return "\n".join(lines[:max_lines] + [f"... truncated {hidden} more lines"])


def load_manifest(root: Path) -> tuple[str, list[dict[str, str]]]:
    manifest = root / "manifest.toml"
    if not manifest.exists():
        return "stark/", []
    data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    repos = [
        {"name": repo["name"], "trunk": repo.get("trunk", "main")}
        for repo in data.get("repo", [])
        if repo.get("name")
    ]
    return data.get("branch_prefix", "stark/"), repos


def git_output(path: Path, args: list[str]) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(path), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def count_dirty_files(worktree: Path) -> str:
    status = git_output(worktree, ["status", "--porcelain"])
    if status is None:
        return "unknown"
    return str(len(status.splitlines())) if status else "0"


def ahead_behind(worktree: Path, trunk: str) -> tuple[str, str]:
    counts = git_output(
        worktree,
        ["rev-list", "--left-right", "--count", f"origin/{trunk}...HEAD"],
    )
    if counts is None:
        return "unknown", "unknown"
    parts = counts.split()
    if len(parts) != 2:
        return "unknown", "unknown"
    behind, ahead = parts
    return ahead, behind


def branch_session(branch: str, branch_prefix: str) -> str:
    return branch.removeprefix(branch_prefix) if branch.startswith(branch_prefix) else "-"


def build_worktree_state(root: Path) -> str:
    branch_prefix, repos = load_manifest(root)
    rows: list[WorktreeRow] = []
    for repo in repos:
        worktree = root / "workspace" / repo["name"]
        if not worktree.exists():
            rows.append(WorktreeRow("-", repo["name"], repo["trunk"], "no", "-", "-", "-", "-"))
            continue

        branch = git_output(worktree, ["branch", "--show-current"]) or "unknown"
        ahead, behind = ahead_behind(worktree, repo["trunk"])
        rows.append(
            WorktreeRow(
                branch_session(branch, branch_prefix),
                repo["name"],
                repo["trunk"],
                "yes",
                branch,
                count_dirty_files(worktree),
                ahead,
                behind,
            )
        )

    if not rows:
        return "no wrapped repos found in manifest.toml"

    lines = ["SESSION  REPO  BASE  ASSEMBLED  BRANCH  DIRTY  AHEAD  BEHIND"]
    lines.extend(
        f"{row.session}  {row.repo}  {row.base}  {row.assembled}  "
        f"{row.branch}  {row.dirty}  {row.ahead}  {row.behind}"
        for row in rows
    )
    return "\n".join(lines)


def parse_worktree_rows(state: str) -> list[WorktreeRow]:
    lines = [line for line in state.splitlines() if line.strip()]
    if len(lines) < 2 or not lines[0].lstrip().startswith("SESSION"):
        return []

    rows: list[WorktreeRow] = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 8:
            return []
        rows.append(WorktreeRow(*parts[:8]))
    return rows


def has_branch_mismatch(row: WorktreeRow, branch_prefix: str) -> bool:
    return (
        row.assembled == "yes"
        and row.session not in {"", "-"}
        and row.branch != f"{branch_prefix}{row.session}"
    )


def has_worktree_attention(row: WorktreeRow, branch_prefix: str) -> bool:
    return (
        row.assembled != "yes"
        or row.dirty != "0"
        or row.ahead != "0"
        or has_branch_mismatch(row, branch_prefix)
    )


def render_worktree_attention_row(row: WorktreeRow, branch_prefix: str) -> str:
    label = row.repo if row.session in {"", "-"} else f"{row.session}/{row.repo}"
    if row.assembled != "yes":
        return f"- {label}: not assembled"

    parts = [
        f"branch {row.branch}",
        f"dirty {row.dirty}",
        f"ahead {row.ahead}",
        f"behind {row.behind}",
    ]
    if has_branch_mismatch(row, branch_prefix):
        parts.append("branch mismatch")
    return f"- {label}: {'; '.join(parts)}"


def summarize_worktree_state(state: str, branch_prefix: str) -> str:
    rows = parse_worktree_rows(state)
    if not rows:
        return limit_lines(state, MAX_WORKTREE_LINES)

    sessions = {row.session for row in rows if row.session not in {"", "-"}}
    attention_rows = [row for row in rows if has_worktree_attention(row, branch_prefix)]
    behind_only_count = sum(
        1
        for row in rows
        if not has_worktree_attention(row, branch_prefix) and row.behind not in {"0", "-"}
    )

    lines = [f"rows: {len(rows)}; active sessions: {len(sessions)}"]
    if behind_only_count:
        lines.append(f"behind-only rows omitted: {behind_only_count}")
    if attention_rows:
        lines.append("attention rows:")
        lines.extend(
            render_worktree_attention_row(row, branch_prefix) for row in attention_rows
        )
    else:
        lines.append("attention rows: none")
    return limit_lines("\n".join(lines), MAX_WORKTREE_LINES)


def load_worktree_state(root: Path) -> str:
    branch_prefix, _ = load_manifest(root)
    return summarize_worktree_state(build_worktree_state(root), branch_prefix)
