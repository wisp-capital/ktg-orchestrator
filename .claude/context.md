# ktg-orchestrator — domain context

This repo coordinates the **KTG (Kore Trading Gateway)** pipeline. It stores no
source; it makes the system understandable and operable from one place.

**The pipeline in one line:** a kotquant/KTG strategy publishes a signal → ZMQ
`stark/events4` → korpse (a Kore strategy) runs the trade-plan state machine and
places the order on the Kore account → kore-proxy carries Kore's events back to
internal Wisp systems.

**Start here:**

- **`docs/context/ktg-system.md`** — full system map (components, the 5 signal types,
  state machine + gating, topics/ports/hosts, account→log mapping).
- **`docs/runbooks/missing-order.md`** — "signal received but no order sent" diagnosis.
- **`AGENTS.md`** — the agent operating contract (sessions, depths, escalation).
- **`DECISIONS.md` / `PREFERENCES.md`** — KTG-specific structural decisions and tradeoffs.

The authoritative per-repo docs (read for field-level detail):
`korpse/docs/signal-flow.md`, `korpse/CLAUDE.md`, `kore-proxy/README.md`.

The broader cross-repo architecture for the whole `~/repos` ecosystem lives in
`~/repos/.claude/`.
