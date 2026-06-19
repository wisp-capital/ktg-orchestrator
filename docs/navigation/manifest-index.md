# Manifest Navigation Index

Generated from `manifest.toml`. Do not hand-edit this file.
Refresh with `nav-index`; verify with `nav-check`.

- branch prefix: `stark/`
- worktrees: `workspace/<slug>/<repo>`
- PR base: each repo's `trunk` value

## Cross-Repo Routing Table

| Repo | Role | Base | Status | Edit policy | Default assemble |
|---|---|---|---|---|---|
| kotquant | KTG signal generation and upstream trading behavior | main | active | source | yes |
| kore-proxy | Kore return path and proxy for execution events | main | active | source | yes |
| korpse | Kore strategy executor and trade-plan state machine | main | active | source | yes |

## Disambiguation (known overlaps)

- **kotquant vs korpse**: KTG signal generation / strategy logic -> kotquant; order routing / trade-plan state machine / executor -> korpse
- **kore-proxy vs korpse**: Kore return path / proxy for execution events -> kore-proxy; strategy executor / trade-plan state machine -> korpse

## Repo Details

### kotquant

- role: KTG signal generation and upstream trading behavior
- status: active
- base branch: `main`
- language: kotlin
- checkout: `~/repos/kotquant`
- remote: `git@github.com:wisp-capital/kotquant.git`
- edit policy: source
- default assemble: yes
- read first: `AGENTS.md`, `README.md`
- verify: `./gradlew test --no-daemon`
- routes: signal generation; KTG strategy; trading behavior; kotquant
- examples: generate a KTG signal; change the KTG strategy logic; fix kotquant trading behavior

### kore-proxy

- role: Kore return path and proxy for execution events
- status: active
- base branch: `main`
- language: rust
- checkout: `~/repos/kore-proxy`
- remote: `git@github.com:wisp-capital/kore-proxy.git`
- edit policy: source
- default assemble: yes
- read first: `AGENTS.md`, `README.md`
- verify: `cargo test --workspace`
- routes: Kore proxy; execution events; return path
- examples: fix the Kore return path; proxy an execution event

### korpse

- role: Kore strategy executor and trade-plan state machine
- status: active
- base branch: `main`
- language: cpp
- checkout: `~/repos/korpse`
- remote: `git@github.com:wisp-capital/korpse.git`
- edit policy: source
- default assemble: yes
- read first: `AGENTS.md`, `README.md`, `docs/signal-flow.md`
- verify: `cmake --build build`
- routes: order routing; trade-plan state machine; missing order; korpse
- examples: fix the trade-plan state machine; route an order through korpse; handle a missing order
