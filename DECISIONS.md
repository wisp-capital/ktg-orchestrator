# Decisions

Structural decisions for `ktg-orchestrator`. Per `AGENTS.md`, these are not revisited
without explicit human direction. The reusable operating-model decisions live in
`~/repos/ai-max/DECISIONS.md`; this file holds only what is specific to KTG.

| ID | Decision | Rationale |
|----|----------|-----------|
| D-001 | This repo orchestrates exactly three KTG repos: **kotquant** (signal source), **korpse** (Kore strategy / order placement), **kore-proxy** (Kore event return path). | They form one signal→order→feedback loop. The orchestrator's job is to make that loop coherent for cross-cutting work. |
| D-002 | **Orchestration-only — no vendored source.** Source stays in each repo's own checkout (`manifest.toml`); work happens in `workspace/<name>` worktrees; changes ship as a PR per repo. | Keeps the proxying relationship clear and reversible; avoids submodule/subtree drift. |
| D-003 | **korpse is C++** because it runs *on* the Kore platform as a strategy (Kore SDK / libksherpa), not as an internal Wisp service. | Order placement happens inside Kore via `order.algo_buy()/algo_sell()`, so the strategy must be a native Kore strategy. |
| D-004 | The **signal contract is owned by the shared hub-rs `signal_event.schema.json`**, not by this repo or by korpse alone. kotquant publishes it; korpse consumes it. | One contract shared across producers/consumers. korpse mirrors hub-rs's signal handling. Field-level truth lives in `korpse/docs/signal-flow.md`. |
| D-005 | **Outbound and inbound are separate components.** korpse turns signals into orders (outbound); kore-proxy republishes Kore's events to internal systems + QuestDB (inbound). | Different directions, different languages, different failure modes. Diagnosis starts by deciding which direction broke. |
| D-006 | **System knowledge lives in `docs/context/` + `docs/runbooks/`**, mapping into the source repos rather than duplicating their docs. | An agent must be able to understand and diagnose the pipeline from this repo. Pointers (not copies) avoid drift against the authoritative per-repo docs. |
