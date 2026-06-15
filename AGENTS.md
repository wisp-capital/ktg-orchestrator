# AGENTS.md

**This is the canonical agent contract.** Read this first. All other documentation in this repo is reference material. If this file conflicts with any other document, this file wins.

## How we work

I state intent and boundaries. You handle everything else: classification,
requirements, design, implementation, verification, and reporting.

I review results, evidence, caveats, and decisions — not implementation details.

## Session Start

0. Surface due reminders: run
   `python3 /Users/alexcstark/repos/ai-max/scripts/due_reminders.py` from the
   state repo. Act on anything due (or consciously re-date it in
   `REMINDERS.md` and say so). Claude Code runs this automatically via a
   SessionStart hook in the state repo; Codex, pi, and any other agent run it
   per this step.
1. Read `STATUS.md` — know what's active and blocked
2. Read `SESSION_TODO.md` if present — surface unchecked `Now` items and the
   highest-priority `Next` item
3. Read active INIT docs — know current work in progress
4. Check git branch and worktree state
5. Identify the next action
6. Read `ideas/` only when selecting future work or when the user asks to save,
   revisit, or promote an idea. Treat each subfolder as a primary tag.

If the next action is unclear, the session starts by fixing `STATUS.md`.

## System Map

To understand the KTG system this repo orchestrates — or to diagnose an operational
issue ("we got a signal but no order went out") — read these first; they save you
tracing source across three repos:

- **`docs/context/ktg-system.md`** — the pipeline map: kotquant/KTG publishes a signal
  → ZMQ `stark/events4` → korpse runs the trade-plan state machine → orders on the
  Kore account; kore-proxy is the return path. Components, signal types, gating,
  topics/ports/hosts, log locations.
- **`docs/runbooks/`** — operational runbooks. Start with
  **`docs/runbooks/missing-order.md`** for a missing or dropped order.

For cross-repo agent routing, use the generated
[`docs/navigation/manifest-index.md`](docs/navigation/manifest-index.md). Refresh
it with `just nav-index` after editing `manifest.toml`, and verify it with
`just nav-check`.

These map into the authoritative per-repo docs (`korpse/docs/signal-flow.md`,
`korpse/CLAUDE.md`, `kore-proxy/README.md`); read those for field-level detail.

## Where to fix signal / order behavior

**Prefer fixing trading-signal behavior in kotquant (signal generation) over korpse
(the Kore strategy) whenever the fix can be made on the kotquant side.** korpse runs
as a Kore-platform strategy and **script promotion is painful** (bundle → upload →
server build → forward-test reload), so changes there are slower and riskier to ship.
Keep korpse a faithful executor of the signal contract and push sign / quantity /
target decisions upstream into kotquant.

Only change korpse when the behavior genuinely cannot live in the signal — the
script-owned policy in `korpse/docs/signal-flow.md` (order routing, reprice cadence,
reject handling, pricing rails). Example: the 2026-06-12 short-increase sign issue
(positive `quantity` published for a short → korpse `invalid_target`) was fixed in
kotquant by publishing a signed increase quantity, leaving korpse untouched. See
`docs/runbooks/missing-order.md`.

## Session Recovery

If a session ends unexpectedly, the next session must resume without escalation.

**Checkpoint file:** Every session writes a lightweight checkpoint to the current
working directory on every turn (`.session-checkpoint.md`) and a durable one on
graceful close (`SESSION_CHECKPOINT.md`). The session start ritual reads the
checkpoint first — if present, it surfaces the last action and next step before
proceeding.

**SESSION_TODO.md scoping:** Store one-off todos in the **worktree root** if the
session is running in a worktree. Store them in the **repo root** only when not
in a worktree. Global cross-repo todos live in `ai-max/SESSION_TODO.md`. Never
run two concurrent sessions in the same working directory.

## Communication patterns

1. I set intent and guardrails. You restate, surface unknowns, and classify the
   work as one-off todo, idea, deep, shallow, or spike.
2. If **deep**: automatically spawn the mission-commander subagent to orchestrate
   parallel phase execution. The commander writes handoff docs, dispatches
   mission-executor subagents, and reports back with merged results. I only see
   the final summary.
3. If **shallow**: execute inline. Build, verify, report, stop.
4. If **spike**: time-boxed discovery. Report findings and recommendation.
5. If **idea**: save a lightweight M0 note for later. Do not create an INIT,
   worktree, PR, or active status row.
6. If **one-off todo**: update `SESSION_TODO.md`. Do not create an INIT,
   worktree, PR, or active status row unless execution starts immediately.
7. For deep work: scenarios define the contract. Executors build autonomously.
8. PRs are checkpoints, not endpoints. Deep initiatives continue after merge.
9. You report after completion. I archive. For deep initiatives, the archive includes a Process Profile (see `~/repos/ai-max/docs/operating-model.md` §14). We move to the next thing.

## Reminders

Date-based obligations live in the state repo's `REMINDERS.md`:

```text
## Pending
- YYYY-MM-DD: <action> (<context links>)
## Done
- YYYY-MM-DD: <action> — done YYYY-MM-DD
```

`scripts/due_reminders.py` prints entries due today or earlier plus a 7-day
upcoming window, and stays silent otherwise. When a reminder fires, the agent
acts on it or re-dates it, then moves it to Done. Use reminders for dated
commitments (deprecation windows, scheduled phase kickoffs, follow-ups) — not
for ordinary next actions, which belong in `STATUS.md`.

## Idea Backlog

**Idea** — an unstarted M0 candidate initiative. It captures a thought we may
revisit later, plus the smallest validation step. Ideas are not active work and
are not completed discovery.

Store ideas in `ideas/<primary-tag>/` or `<repo>/ideas/<primary-tag>/` as
`IDEA-YYYY-MM-DD-<slug>.md`. The folder is the primary tag. Promote an idea to
an INIT only when work is selected for discovery or implementation.

## One-off Todos

**One-off todo** — a concrete operational reminder or small task that should be
visible in the next session, but is not yet an initiative and is not broad enough
to be an idea backlog entry.

Store one-off todos in `SESSION_TODO.md` at the **worktree root** if the
session is running in a worktree. Store them in the **repo root** only when not
in a worktree. Global cross-repo todos live in `ai-max/SESSION_TODO.md`. Never
run two concurrent sessions in the same working directory.
Use `Now` for urgent blockers and `Next` for queued tasks. Include acceptance
constraints on the checklist line when they matter. When work starts, either
check the todo off after completion or promote it into the normal shallow,
spike, or deep workflow.

## Three depths

One-off todos and ideas are capture lanes. They are not operating depths.

**Shallow** — bounded task. Build, verify, report, stop. Executed inline. No subagents. Adversarial review: off by default (velocity).
**Deep** — multi-phase system. Auto-spawn mission-commander to orchestrate parallel
phase execution. Executors build autonomously in parallel waves. PRs are checkpoints.
Adversarial review: on by default (complexity).
**Spike** — exploratory. Time-boxed discovery. Output is a recommendation
(abandon, shallow, or deep) with findings and unknowns. Adversarial review: on by default (uncertainty).

## Truth labels

Use for claims that affect trust, decisions, or reproducibility:

| Label | Meaning |
|---|---|
| Verified | Proven by test, run, report, or direct inspection |
| Inferred | Reasonable but not proven |
| Assumed | Taken as given; could be wrong |
| Unknown | Not checked |

## Maturity

| Level | Meaning |
|---|---|
| M0 Sketch | Idea, notebook, rough prototype |
| M1 Runnable | Can run; setup may be fragile |
| M2 Reproducible | Same inputs → same outputs |
| M3 Comparable | Results stored and can be compared |
| M4 Scalable | Works at realistic data size/runtime |
| M5 Production-ready | Reusable without handholding |

Operational states (Deployed, Monitored) are tags applied to M5 artifacts, not additional maturity levels.

## Escalate when

A decision would change what a system design says, what the human would
do next, or what the system is safe to do. Specifically:

- Scope expands beyond approved intent
- A semantic or data assumption materially changes what a backtest would conclude
- A result expected to be reproducible cannot be reproduced
- A metric is misleading or incorrectly defined
- Runtime makes the workflow impractical
- Multiple sessions need coordination beyond the current tracking
- Any path touches live trading, broker connectivity, order routing, or capital
- Deployment to production without explicit approval (unless fully automated at autonomy level 5)
- Rollback decision when not automated with predefined thresholds
- The next autonomous action cannot be reconstructed from the files

## Do not escalate for

File names, directory layout, helpers, tests, routine implementation choices,
documented tradeoffs in PREFERENCES.md, status updates without blockers, code
review (happens at PR, not in chat), or normal PR workflow.

## Hard rules

1. No live trading, broker connectivity, order routing, or capital exposure
   without explicit approval.
2. Every decision-grade result records lineage: code version, data version,
   config, universe, time range, fill/cost model, metrics, and caveats.
3. Reproducibility status must be explicit for every meaningful result.
4. Unknowns and caveats must be surfaced, not buried.
5. `STATUS.md` must name the next autonomous action for every active initiative.
6. A PR is a checkpoint, not an endpoint. Deep initiatives continue after merge.
7. Add structure only after repeated friction.
8. Unstarted ideas belong in `ideas/<primary-tag>/`, not `initiatives/` or
   `archive/spikes/`.
9. One-off todos belong in `SESSION_TODO.md`, not `ideas/`, `initiatives/`, or
   `STATUS.md` active initiative rows.

## Autonomy Level

Current: 3
Target: 4
Promoted: 2026-06-08 by human

### Promotion criteria

| To Level | Criterion | Metric | Threshold | Status |
|---|---|---|---|---|
| 4 | Archive search is useful | Archive findings led to reuse | 3/3 initiatives | 0/3 |
| 4 | Per-repo status works | Continuity failures | 0 across 3 sessions | 0/3 |
| 4 | Metrics are predictive | Escalations caught real issues | 100% precision | 1/3 |
| 5 | Scenario quality is high | Human approval time < 30s | 3/3 initiatives | 0/3 |
| 5 | Escalation judgment is correct | False positive/negative rate | < 10% | 0/3 |

### Demotion trigger

Any incident where the agent should have escalated but didn't, or the human had to intervene mid-stream for a decision-class issue. Demote to 3, investigate, fix the gap, re-qualify.

## Preference Ledger

Before escalating on a tradeoff, check `PREFERENCES.md`. If the preference is documented, apply it and log the decision in the initiative. If not, ask the human once (1 question, 2 choices max), log the answer in `PREFERENCES.md`, and never ask again. Never escalate for documented tradeoffs.

## Adversarial Review

Adversarial review is a second perspective that challenges each step. Default:
- Shallow: off (velocity)
- Deep: on (complexity)
- Spike: on (uncertainty)

Human can override per initiative: `Adversarial: on/off` in the intent.

When on, the agent produces a challenge report after scenarios, build, and verify.
See `~/repos/ai-max/docs/operating-model.md` §15 for full mechanism.

## Tools

The agent has access to the following standalone tools in this repo:

### ChatGPT Pro Wrapper
`tools/chatgpt-pro-wrapper/` — Standalone Python client for ChatGPT Pro / extended thinking models (o1-pro, o3, gpt-5.5, etc.).

- **CLI:** `python -m chatgpt_pro "prompt"` (with `--stdin`, `--reasoning-effort`, `--json`, `--model` flags)
- **Programmatic:** `from chatgpt_pro import ChatGPTProClient, Config`
- **Trigger detection:** `from chatgpt_pro import is_trigger, extract_prompt` — detects "Ask ChatGPT Pro: ..." style messages
- **Env vars:** `OPENAI_API_KEY`, `MODEL_NAME`, `REASONING_EFFORT`, `OPENAI_BASE_URL`
- **Auto API selection:** Uses `v1/responses` API for o-series / pro models, `v1/chat.completions` for others
- **Use when:** Extended reasoning needed, complex problem decomposition, or when the human explicitly asks to escalate to a stronger model

### Opus Wrapper
`tools/opus-wrapper/` — Standalone Python client for Anthropic Claude Opus frontier models (claude-4-5-opus-latest, etc.).

- **CLI:** `python -m opus "prompt"` (with `--stdin`, `--thinking`, `--thinking-budget`, `--json`, `--model` flags)
- **Programmatic:** `from opus import OpusClient, Config`
- **Trigger detection:** `from opus import is_trigger, extract_prompt` — detects "Ask Opus: ...", "Have Opus review: ...", "Opus, analyze: ..." style messages. Also routes standalone "Claude" triggers ("Ask Claude: ...", "Claude, review: ...") to Opus since Claude is the Anthropic model family.
- **Env vars:** `ANTHROPIC_API_KEY`, `OPUS_MODEL`, `OPUS_THINKING`, `OPUS_THINKING_BUDGET`, `OPUS_MAX_TOKENS`, `ANTHROPIC_BASE_URL`
- **Thinking mode:** Supports Anthropic thinking / extended reasoning with configurable budget tokens
- **Use when:** Anthropic model preferred, complex analysis requiring thinking mode, or when the human explicitly asks for Opus

### Codex Wrapper
`tools/codex-wrapper/` — Standalone Python client for OpenAI's latest frontier Codex models (gpt-5, etc.). Clean, lightweight wrapper distinct from the Pro / extended-thinking tool.

- **CLI:** `python -m codex "prompt"` (with `--stdin`, `--temperature`, `--json`, `--model` flags)
- **Programmatic:** `from codex import CodexClient, Config`
- **Trigger detection:** `from codex import is_trigger, extract_prompt` — detects "Ask Codex: ...", "Latest Codex: ...", "Have Codex review: ..." style messages
- **Env vars:** `OPENAI_API_KEY`, `CODEX_MODEL`, `CODEX_MAX_TOKENS`, `CODEX_TEMPERATURE`, `OPENAI_BASE_URL`
- **API:** Uses `v1/chat.completions` API for fast, general-purpose frontier model access
- **Use when:** Quick access to latest frontier Codex model without extended reasoning overhead, general analysis, or when the human asks for Codex

## Domain Context and Decisions

- **KTG system map:** How the orchestrated pipeline works + how to diagnose it:
  `docs/context/ktg-system.md` and `docs/runbooks/` in this repo. See also `.claude/context.md`.
- **Cross-repo domain context:** Broader multi-repo architecture and dependencies:
  `.claude/` in `~/repos/`.
- **Global decisions:** Structural decisions specific to this repo: `DECISIONS.md` in
  this repo. Reusable operating-model decisions: `~/repos/ai-max/DECISIONS.md`.
- **Best practices / tradeoffs:** KTG-specific code/process preferences:
  `PREFERENCES.md` in this repo. Reusable preferences: `~/repos/ai-max/PREFERENCES.md`.

The agent reads these as part of session startup. Structural decisions in `DECISIONS.md` are not revisited without explicit human direction.

## Mission Tree (Automatic Subagent Execution)

For deep initiatives, the workflow automatically spawns subagents. No manual commands. No `/phase` or `/commander`. The user states intent; the workflow handles the rest.

### How it works

1. **Intent received** → Agent classifies as deep (>3 phases, cross-repo, multi-milestone)
2. **Auto-spawn commander** → `subagent({ agent: "mission-commander", mode: "fork" })` with the INIT doc
3. **Commander analyzes** → Reads plan, identifies parallel waves, writes handoff docs
4. **Parent reads wave plan** → Parent reads handoff docs + challenge report from commander
5. **Auto-dispatch executors** → Parent spawns up to 4 `mission-executor` subagents simultaneously
6. **Executors build** → Each reads handoff doc, builds, verifies, creates PR, reports back to parent
7. **Parent merges** → Collects results, updates STATUS.md, presents final summary to user

### User sees

```
Intent: Wire SEC Form 4 insider data into backtesting
Classification: Deep (5 phases, 2 repos)

Wave 1 dispatched automatically (3 phases in parallel):
- Phase 1 (dagster): PR #124, 7 tests passed
- Phase 2 (kotquant event): PR #2746, 6 tests passed
- Phase 3 (kotquant feed): PR #2746, 4 tests passed

Wave 2 ready (2 phases sequential):
- Phase 4 (backtest assembly): waiting for Phase 3
- Phase 5 (strategy hook): waiting for Phase 4
```

### No manual control

- **Never ask** the user whether to use subagents. The workflow decides.
- **Never ask** the user to review handoff docs before dispatching. The commander writes and dispatches.
- **Never ask** the user to approve wave transitions. The commander executes autonomously.
- **The user only sees** the final summary — PR links, test results, blockers, and next actions.

### Wave planning (commander decides automatically)

**Parallel:**
- Different repos
- Different modules in same repo, no shared files
- Read-only vs. write phases

**Sequential:**
- Phase N+1 imports/uses code from Phase N
- Same file modified by both
- Second phase tests first phase's output

### Speed

- **Subagent overhead:** ~30 seconds per spawn
- **Parallel speedup:** 2-3x for multi-phase initiatives
- **Break-even:** Worth it for >2 parallelizable phases or cross-repo work
- **Not worth it:** Shallow tasks (single file, low risk) execute inline automatically
