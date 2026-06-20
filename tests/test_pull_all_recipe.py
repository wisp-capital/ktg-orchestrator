from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_just_pull_all_dispatches_to_shared_ai_max_tool() -> None:
    if shutil.which("just") is None:
        return

    result = subprocess.run(
        ["just", "--dry-run", "pull-all"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, result.stderr
    assert "tools/worktree-assembler.py" in output
    assert "pull-all" in output
