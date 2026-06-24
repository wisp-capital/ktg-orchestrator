# ktg-orchestrator

A proxy / orchestration meta-repo for KTG (Kore Trading Gateway) related work.

Wraps KTG-related source repos, provides a single workspace for cross-cutting
development, and ships changes back to each repo's origin as a pull request.

It is **orchestration-only**: it stores no source code. The real source lives in
each repo's own checkout listed in `manifest.toml`. ktg-orchestrator only holds a
manifest, framework command wiring, and docs. Assembled worktrees land in `workspace/`
(gitignored) at runtime.

## Wrapped repos

| Repo | Checkout | Base branch | Lang |
|------|----------|-------------|------|
| kotquant | `~/repos/kotquant` | `main` | Kotlin |
| kore-proxy | `~/repos/kore-proxy` | `main` | Rust |
| korpse | `~/repos/korpse` | `main` | C++ |

For cross-repo agent routing, use the generated
[`docs/navigation/manifest-index.md`](docs/navigation/manifest-index.md). Refresh
it with `just nav-index` after editing `manifest.toml`, and verify it with
`just nav-check`.

## The KTG system

These three repos form one loop: a **kotquant/KTG** strategy publishes a signal to
ZMQ `stark/events4` → **korpse** (a Kore strategy) runs the trade-plan state machine
and places the order on the Kore account → **kore-proxy** carries Kore's events back
to internal systems. To understand the pipeline or diagnose an operational problem,
read these (they save tracing source across all three repos):

- **[`docs/context/ktg-system.md`](docs/context/ktg-system.md)** — the system map:
  components, signal types, state machine + gating, topics/ports/hosts, log locations.
- **[`docs/runbooks/missing-order.md`](docs/runbooks/missing-order.md)** — diagnose a
  signal that produced no order (e.g. an Increase that didn't add).

## Usage

```sh
just assemble my-task --repo kotquant --repo kore-proxy
just assemble my-task
just status
just nav-index
just nav-check
just ship --draft
just clean --force
```

Scratch prompt handoffs live under `.amx/prompts/`, which is gitignored and
independent of wrapped source worktrees. Use `just prompt-save "title" --stdin`,
`just prompt-list`, `just prompt-show <prompt-id>`, and `just prompt-rm
<prompt-id>` for ad hoc prompts that another session should load later.

Without `just`, run the shared ai-max worktree assembler directly:
```sh
python3 ~/repos/ai-max/tools/worktree-assembler.py assemble my-task --repo kotquant
python3 ~/repos/ai-max/tools/worktree-assembler.py status
python3 ~/repos/ai-max/tools/worktree-assembler.py ship
python3 ~/repos/ai-max/tools/worktree-assembler.py clean --force
```

## How it works

- `manifest.toml` lists each wrapped repo: local path, remote, base branch, lang.
- `assemble <slug>` runs `git worktree add` in each source repo, creating
  `workspace/<slug>/<name>` on branch `stark/<slug>` from `origin/main`. Your primary
  checkout is never touched.
- `ship` pushes dirty assembled branches; open PRs manually if the shared
  assembler cannot infer the desired PR body.
- `clean --force` removes stale or orphaned worktrees.

## AI-max operating state

`/Users/alexcstark/repos/ai-max` is the reusable operating framework: Specs
define target state, inline scenarios define compliance, CI is the breakage
gate, and the eval continuously reports completeness gaps.

ktg-orchestrator holds the KTG-specific state for that framework:

- `just state` is the derived dashboard for active Spec and scenario/run state.
- `STATUS.md` is retained only as legacy transition context until all stale rows
  have been retired.
- Legacy work artifacts and deep-work handoffs are historical context unless a
  current Spec or materialization record points at them.
- `archive/` holds completed initiatives and spikes.

Implementation work still happens in linked repo worktrees under `workspace/`.

## Requirements

- Python 3.11+
- `git`, `gh` (authenticated), and optionally `just`
- The wrapped repos already cloned at the paths listed in `manifest.toml`
