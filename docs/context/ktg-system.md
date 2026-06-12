# KTG System Map

**What KTG is:** the Kore Trading Gateway pipeline. A kotquant strategy decides to
trade, emits a signal, and that signal becomes a real order on the external **Kore**
trading platform. This document is the map: what the pieces are, where they live, how
a signal becomes an order, and where to look when one doesn't.

`ktg-orchestrator` stores no source — it coordinates the three repos below. The code
lives in each repo's own checkout (see `manifest.toml`). This map points into those
repos; it does **not** restate their contracts (that would drift). The
**authoritative sources** are listed at the bottom — read them for field-level detail.

## Components

| Component | Repo | Lang | Role |
|-----------|------|------|------|
| KTG signal publisher | `~/repos/kotquant` (KTG) | Kotlin | A strategy decides to trade and publishes a `SignalEvent` to ZMQ. `KtgSignalHandler` logs `Published signal ... to KTG`. |
| korpse | `~/repos/korpse` | C++ | A Kore-platform strategy. Subscribes to the signal channel, runs the trade-plan state machine, and places orders on the Kore account. **This is where a signal becomes an order.** |
| kore-proxy | `~/repos/kore-proxy` | Rust | The return path. Subscribes to Kore's own ZMQ events (rejects, positions, trade plans, halts), republishes them to internal Wisp systems, and logs metrics to QuestDB. |
| Kore | external platform | — | The broker/execution venue. korpse is deployed onto it as a strategy bound to a Kore **account** (= operator). |

## Outbound path — signal → order

```
kotquant/KTG strategy
   │  publishes SignalEvent JSON
   ▼
ZMQ topic  stark/events4
   │
   ▼
korpse  on_event_stream
   │  1. routing checks: shell_id (account_id) match, symbol match
   │  2. parse StreamEvent fields
   │  3. dispatch by signal_type
   ▼
handle_entry / handle_exit / handle_reduce / handle_increase / handle_modify
   │  updates the TradePlan state machine
   ▼
order.algo_buy() / order.algo_sell()   → Kore account (operator)
   │
   ▼
eval timer checks stop_loss / take_profit / stop_time
```

The signal channel is the korpse `event_channel` parameter (default `stark/events4`).

## Signal types

Five types. A signal is silently dropped if its `signal_type` is unknown, the
`symbol` doesn't match the instance, or (when `shell_id` is set) the `account_id`
doesn't match.

| Type | State transition | Quantity logic |
|------|------------------|----------------|
| **Entry** | `None`/`Pending` → `Pending` | `direction × abs(quantity)`; a later Entry can replace an in-flight pending entry |
| **Exit** | any → `Exiting` | target = 0, flatten |
| **Reduce** | `Active` → `Reducing` | `score × filled_qty`, where `score` is the fraction to **keep** (0.5 = keep half) |
| **Increase** | `Active`/`Increasing` → `Increasing` | explicit `quantity` > `score × filled` > `score × planned`; valid in-flight replacement allowed if target stays at/above filled |
| **Modify** | (unchanged) | updates `stop_loss` + `take_profit` only |

## Trade-plan state machine

```
None → Pending          (Entry signal)
Pending → Pending        (partial fill / replacement Entry)
Pending → Active         (target reached, or remainder ends after partial fill)
Active → Increasing      (Increase signal)
Active → Reducing        (Reduce signal)
Active → Exiting         (Exit signal, or stop_loss / take_profit / stop_time hit)
Increasing → Active      (target reached, terminal reject/cancel, retries exhausted)
Exiting → None           (position flat)
```

## Gating — why a signal may not produce an order

The state machine is the most common reason an order "didn't go out." Key rules:

- **Increase is ignored unless the position is `Active` or `Increasing`.** It is
  dropped while `None`, `Pending`, `Reducing`, or `Exiting`. So an Increase that
  arrives before the position is open (or while it is pending/being exited) produces
  **no order** — logged `increase_ignored reason=no_active_trade` (or
  `exit_in_progress` / `reduce_in_progress`).
- An Increase whose computed target is **below the current filled position** is
  ignored (`invalid_target`) — it would reduce exposure, not add.
- **Reduce** is ignored if there's no filled position, and ignored while an Increase
  is in progress.
- **Modify** is ignored if there's no active trade.
- Post-acceptance, an order can still be blocked: `increase_rejected risk_cap_blocked`
  (risk limits) or, at submission, `order_submit_skipped` (trading halted,
  non-positive qty, invalid market data), `wide_spread_gate_tripped`, or
  `locate_rate_gate_tripped` (HTB symbols).

For the full diagnosis decision tree, see
[`../runbooks/missing-order.md`](../runbooks/missing-order.md).

## Inbound path — Kore feedback

```
Kore platform
   │ (ZMQ)
   ▼
kore-proxy  proxy (koreproxy)
   │  event types: Init, Start, Reject, Position, TradePlan, Halt, HaltResume,
   │  Nasdaq/Nyse/Arca Imbalance, News, Log
   ├─→ ExternalEventPublisher → internal Wisp systems
   └─→ koreqdb → QuestDB metrics
```

korpse can also publish its own position state outbound to `stark/events3`
(`position_channel`, off by default) so kotquant can aggregate portfolio-level risk.

## Topics, ports, hosts

| Thing | Value |
|-------|-------|
| Signal channel (kotquant → korpse) | ZMQ `stark/events4` (korpse `event_channel`) |
| korpse position publish | ZMQ `stark/events3` (korpse `position_channel`, off by default) |
| kore-proxy ktgnet bus | sub `tcp://0.0.0.0:10087`, pub `tcp://0.0.0.0:10088` |
| kore-proxy relay (configs/logging) | HTTP `:8000` |
| QuestDB metrics | `epyc.nyc:31800` |
| Redis health keys | `SystemHealth::KoreProxy`, `::KoreRelay`, `::KtgNet` |

## Operators / accounts and logs

A Kore **account** is the operator a korpse instance trades under. korpse is deployed
under account **204018 (AStark Kore 09)** per `korpse/CLAUDE.md` (confirm at runtime —
there can be more than one).

Per-account korpse state-machine logs live on the Kore host as
`worker_<accountId>.log` (filename == account id, e.g. acct 204018 →
`worker_204018.log`):

| env | host | dir |
|-----|------|-----|
| `live` | `10.10.10.130` | `/kcore_logs` |
| `fwd` | `10.10.10.127` | `/kcore_fwd_logs` |

Pull them read-only with the **`kore-logs`** skill, which wraps
`~/repos/korpse/scripts/fetch_kore_logs.py`. The main platform log is `YYYY-MM-DD.log`
(raw acks/fills, `accountName=...`). Timestamps are ET.

The strategy-name → account mapping: the wisp side names the variant
(`KtgSignalHandler - Published signal ...` in the `ktg_wbe` container); Kore logs name
the account (`accountName=...` in the main log). Resolve the account id first, then
read its worker file.

## Authoritative sources (read these for detail)

- **`korpse/docs/signal-flow.md`** — the signal field contract, per-type semantics,
  routing, ownership model (script policy vs signal overrides). Source of truth for
  signal behavior.
- **`korpse/CLAUDE.md`** — korpse architecture, state machine, parameters
  (`event_channel`, `buy_algo`/`sell_algo`, account), deployment, tech debt.
- **`kore-proxy/README.md`** — the return-path services (proxy, relay, ktgnet, kftp),
  event types, QuestDB metrics, Redis health.
- **`kore-proxy/CLAUDE.md`** — kore-proxy service overview and messaging flow.
- The signal JSON contract is shared via hub-rs `signal_event.schema.json`.
