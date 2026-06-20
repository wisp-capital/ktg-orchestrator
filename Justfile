# ktg-orchestrator Justfile

set shell := ["bash", "-c"]

home := env_var_or_default("HOME", "/tmp")
ai_max_dir := env_var_or_default("AI_MAX_DIR", home / "repos/ai-max")
python := "python3"

# Build the Rust routing tool
build:
    cargo build --release

# Print AI-max startup context and cache it in .startup-snapshot.md
startup:
    @{{python}} tools/startup_snapshot.py --write .startup-snapshot.md

# Assemble worktrees for a task
assemble slug *args:
    cargo run --release -- assemble {{slug}} {{args}}

# Show status of all wrapped repos
status:
    @cargo run --release -- status

# Clone/pull every primary checkout listed in manifest.toml
pull-all:
    {{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" pull-all

# Regenerate manifest-derived cross-repo navigation files
nav-index:
    {{python}} "{{ai_max_dir}}/scripts/nav_index.py" --root . write

# Verify generated navigation files are in sync with manifest.toml
nav-check:
    {{python}} "{{ai_max_dir}}/scripts/nav_index.py" --root . check

# Route a task to the repo(s) it belongs in — the cheap first call at task start.
route query *args:
    {{python}} "{{ai_max_dir}}/scripts/route.py" --root . "{{query}}" {{args}}

# Ship changes (push + open PRs)
ship *args:
    cargo run --release -- ship {{args}}

# Teardown worktrees
teardown *args:
    cargo run --release -- teardown {{args}}

# --- ai-max workflow CLI (lean v7.1) ---

# derived state dashboard from specs/ + eval reports (replaces STATUS.md)
state:
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . state

# lean operating-model workflow CLI (new/check/eval/gaps/state) — see ~/repos/ai-max
amx *args:
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . {{args}}

# Verify stale generated artifacts are not in the active agent context path
context-audit *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . context-audit {{args}}

# Show whether the recurring agent-run docs coherence scan is fresh
docs-scan-status *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . docs-scan status {{args}}

# Emit the self-contained prompt for an agent-run docs coherence scan
docs-scan-prompt *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . docs-scan prompt {{args}}

# Record a completed agent-run docs coherence scan
docs-scan-record report high="0" medium="0" low="0" *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . docs-scan record --report {{report}} --high {{high}} --medium {{medium}} --low {{low}} {{args}}

# Agent metrics: prompt count + agent runtime per session, signal only
metrics *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" metrics {{args}}

# --- Orchestrator Inbox (capture / review / batch-complete) ---

# session-start nudge: surface Inbox (daily) + Someday (weekly) if a review is due
inbox-status:
    @{{python}} "{{ai_max_dir}}/scripts/inbox.py" status

# show all items (which=inbox|someday|all) — for daily/weekly review
inbox-show which="inbox":
    @{{python}} "{{ai_max_dir}}/scripts/inbox.py" show --which {{which}}

# mark a review complete (weekly=true for the Someday review)
inbox-reviewed weekly="":
    @{{python}} "{{ai_max_dir}}/scripts/inbox.py" reviewed {{weekly}}
