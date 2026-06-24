# ktg-orchestrator Justfile

set shell := ["bash", "-c"]

home := env_var_or_default("HOME", "/tmp")
ai_max_dir := env_var_or_default("AI_MAX_DIR", home / "repos/ai-max")
python := "python3"

# No local orchestrator binary is required; wrapped repos build in their own worktrees
build:
    @echo "no local build"

# Print AI-max startup context and cache it in .startup-snapshot.md
startup:
    @{{python}} tools/startup_snapshot.py --write .startup-snapshot.md

# Assemble worktrees for a task
assemble slug *args:
    {{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" assemble {{slug}} {{args}}

# Show status of all wrapped repos
status:
    @{{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" status

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
    {{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" ship {{args}}

# Clean stale or orphaned worktrees
clean *args="":
    {{python}} "{{ai_max_dir}}/tools/worktree-assembler.py" clean {{args}}

# --- ai-max workflow CLI (lean v7.7) ---

# derived state dashboard from specs/ + eval reports (replaces STATUS.md)
state:
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . state

# Inspect the authoritative generated-state root
state-root *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . state-root status {{args}}

# lean operating-model workflow CLI (new/check/eval/gaps/state) - see ~/repos/ai-max
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

# Save a scratch prompt handoff under .amx/prompts/ (pass --stdin or --body)
prompt-save title *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . prompt save "{{title}}" {{args}}

# List scratch prompt handoffs
prompt-list:
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . prompt list

# Show one scratch prompt handoff
prompt-show prompt_id:
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . prompt show {{prompt_id}}

# Remove one scratch prompt handoff
prompt-rm prompt_id:
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . prompt rm {{prompt_id}}

# Create a draft target-state delta for human approval
delta-new slug:
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . delta new {{slug}}

# Create active materialization work from an approved delta
materialize delta:
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . materialize {{delta}}

# Run a scenario check and record the result
run spec scenario *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . run {{spec}} {{scenario}} {{args}}

# Show latest scenario run results
run-status *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . run status {{args}}

# Report Specs at the scenario-green / gap-closed human-review threshold
run-threshold *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . run threshold {{args}}

# Record an immutable proof run
proof-record proof result report *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . proof record --proof {{proof}} --result {{result}} --report {{report}} {{args}}

# Show latest proof results
proof-status *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . proof status {{args}}

# Report Specs at the proof-green / gap-closed human-review threshold
proof-threshold *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . proof threshold {{args}}

# Scaffold a proof definition for a Spec
proof-new proof *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . proof new {{proof}} {{args}}

# Run a proof harness for an eval area
eval area *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . eval {{area}} {{args}}

# Run a scanner adapter and record canonical eval gaps
scan kind area *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . scan {{kind}} {{area}} {{args}}

# Track eval gaps and update generated gap state
gaps area *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . gaps {{area}} {{args}}

# Emit, dry-run, execute, or PR-sync corrective-action packets for eligible unguarded gaps
dispatch area *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . dispatch {{area}} {{args}}

# Run one eval -> gaps -> dispatch pass; schedule externally for cadence
loop area *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . loop {{area}} {{args}}

# Validate PR classification: spec_delta, materialization, or chore
pr-check type *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . pr-check --type {{type}} {{args}}

# Validate this repo against the shared ai-max orchestrator contract
orchestrator-check *args="":
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . orchestrator-check {{args}}

# Print ordered framework adoption steps for this orchestrator
upgrade-plan:
    @{{python}} "{{ai_max_dir}}/scripts/amx.py" --root . orchestrator-check --upgrade-plan

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
