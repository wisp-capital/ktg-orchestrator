from __future__ import annotations

from pathlib import Path

from tools import startup_snapshot, startup_worktrees


STATUS_TEXT = """# Status

## Active initiatives

| ID | Name | Depth | Stage | Maturity | Next action | Blocked? |
|---|---|---|---|---|---|---|
| [missing-order-runbook](initiatives/INIT-missing-order-runbook.md) | Missing Order Runbook | Shallow | Build | M2 target | Verify the runbook path. | No |

## Decisions needed

- [none]

## Recently completed

| ID | Name | Outcome | Archived |
|---|---|---|---|
"""


def test_render_snapshot_includes_ktg_startup_context(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "STATUS.md").write_text(STATUS_TEXT, encoding="utf-8")
    (tmp_path / "SESSION_TODO.md").write_text(
        "## Now\n"
        "- [ ] Confirm KTG startup snapshot\n"
        "\n"
        "## Next\n"
        "- [ ] Revisit archived signal docs\n",
        encoding="utf-8",
    )
    lock_dir = tmp_path / ".initiative-locks" / "missing-order-runbook.lock"
    lock_dir.mkdir(parents=True)
    (lock_dir / "info.txt").write_text(
        "initiative: missing-order-runbook\n"
        "agent: codex\n"
        "taken: 2026-06-14T21:00:00Z\n"
        "scope: startup command port\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(startup_snapshot, "run_due_reminders", lambda root: "")
    monkeypatch.setattr(startup_snapshot, "load_git_state", lambda root: "## main...origin/main")
    monkeypatch.setattr(
        startup_snapshot,
        "load_worktree_state",
        lambda root: "unavailable (cargo target missing)",
    )

    snapshot = startup_snapshot.render_snapshot(tmp_path)

    assert "**Active Initiatives**" in snapshot
    assert "`[missing-order-runbook](initiatives/INIT-missing-order-runbook.md)`" in snapshot
    assert "depth Shallow" in snapshot
    assert "stage Build" in snapshot
    assert "next: Verify the runbook path." in snapshot
    assert "**Live Locks**" in snapshot
    assert "`missing-order-runbook` - agent codex; taken 2026-06-14T21:00:00Z" in snapshot
    assert "- [ ] confirm-ktg-startup-snapshot: Confirm KTG startup snapshot" in snapshot
    assert "- [ ] revisit-archived-signal-docs: Revisit archived signal docs" in snapshot
    assert "## main...origin/main" in snapshot
    assert "unavailable (cargo target missing)" in snapshot


def test_main_writes_snapshot_file(tmp_path: Path, monkeypatch, capsys) -> None:
    (tmp_path / "STATUS.md").write_text(STATUS_TEXT, encoding="utf-8")
    output_file = tmp_path / ".startup-snapshot.md"

    monkeypatch.setattr(startup_snapshot, "run_due_reminders", lambda root: "")
    monkeypatch.setattr(startup_snapshot, "load_git_state", lambda root: "clean")
    monkeypatch.setattr(startup_snapshot, "load_worktree_state", lambda root: "none")
    monkeypatch.setattr(
        startup_snapshot.sys,
        "argv",
        ["startup_snapshot.py", "--root", str(tmp_path), "--write", str(output_file)],
    )

    startup_snapshot.main()

    stdout = capsys.readouterr().out
    assert stdout == output_file.read_text(encoding="utf-8")
    assert "**Startup Snapshot**" in stdout


def test_summarize_worktree_state_keeps_attention_rows_compact() -> None:
    raw_state = """SESSION  REPO        BASE  ASSEMBLED  BRANCH       DIRTY  AHEAD  BEHIND
alpha    kotquant    main  yes        stark/alpha  0      0      4
beta     korpse      main  yes        stark/other  3      1      0
gamma    kore-proxy  main  no         -            -      -      -
"""

    summary = startup_worktrees.summarize_worktree_state(raw_state, branch_prefix="stark/")

    assert "rows: 3; active sessions: 3" in summary
    assert "behind-only rows omitted: 1" in summary
    assert "alpha/kotquant" not in summary
    assert "beta/korpse: branch stark/other; dirty 3; ahead 1; behind 0; branch mismatch" in summary
    assert "gamma/kore-proxy: not assembled" in summary


def test_load_worktree_state_reads_manifest_workspace_without_rust_tool(
    tmp_path: Path,
    monkeypatch,
) -> None:
    (tmp_path / "manifest.toml").write_text(
        'branch_prefix = "stark/"\n'
        '[[repo]]\n'
        'name = "kotquant"\n'
        'trunk = "main"\n'
        '[[repo]]\n'
        'name = "korpse"\n'
        'trunk = "main"\n',
        encoding="utf-8",
    )
    (tmp_path / "workspace" / "korpse").mkdir(parents=True)

    def fake_git_output(path: Path, args: list[str]) -> str | None:
        if path.name != "korpse":
            return None
        if args == ["branch", "--show-current"]:
            return "stark/ktg-fix"
        if args == ["status", "--porcelain"]:
            return " M strategy.cpp"
        if args == ["rev-list", "--left-right", "--count", "origin/main...HEAD"]:
            return "2\t1"
        raise AssertionError(f"unexpected git call: {path} {args}")

    monkeypatch.setattr(startup_worktrees, "git_output", fake_git_output)

    state = startup_worktrees.load_worktree_state(tmp_path)

    assert "rows: 2; active sessions: 1" in state
    assert "kotquant: not assembled" in state
    assert "ktg-fix/korpse: branch stark/ktg-fix; dirty 1; ahead 1; behind 2" in state
