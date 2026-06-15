# ktg-orchestrator Justfile

set shell := ["bash", "-c"]

# Build the Rust tool
build:
    cargo build --release

# Print AI-max startup context and cache it in .startup-snapshot.md
startup:
    @python3 tools/startup_snapshot.py --write .startup-snapshot.md

# Assemble worktrees for a task
assemble slug *args:
    cargo run --release -- assemble {{slug}} {{args}}

# Show status of all wrapped repos
status:
    @cargo run --release -- status

# Regenerate manifest-derived cross-repo navigation files
nav-index:
    python3 /Users/alexcstark/repos/ai-max/scripts/nav_index.py --root . write

# Verify generated navigation files are in sync with manifest.toml
nav-check:
    python3 /Users/alexcstark/repos/ai-max/scripts/nav_index.py --root . check

# Ship changes (push + open PRs)
ship *args:
    cargo run --release -- ship {{args}}

# Teardown worktrees
teardown *args:
    cargo run --release -- teardown {{args}}
