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
