# ktg-proxy Justfile

set shell := ["bash", "-c"]

# Build the Rust tool
build:
    cargo build --release

# Assemble worktrees for a task
assemble slug *args:
    cargo run --release -- assemble {{slug}} {{args}}

# Show status of all wrapped repos
status:
    cargo run --release -- status

# Ship changes (push + open PRs)
ship *args:
    cargo run --release -- ship {{args}}

# Teardown worktrees
teardown *args:
    cargo run --release -- teardown {{args}}
