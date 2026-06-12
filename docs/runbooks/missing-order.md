# Runbook: signal received but no order sent

Use this when a strategy fired a signal (Entry / **Increase** / Reduce / Exit) but no
order showed up on the Kore account. Read [`../context/ktg-system.md`](../context/ktg-system.md)
first if you don't know the pipeline.

The pipeline has four stages where a signal can die. Walk them in order — each step
narrows the cause to one component.

```
[1] kotquant published it?  →  [2] korpse received it?  →
[3] korpse accepted it?     →  [4] korpse submitted the order?
```

## Step 1 — Was the signal published? (kotquant / KTG)

If the strategy never published, the gate is upstream in kotquant (the strategy
didn't emit it, or a pre-publish check suppressed it) and nothing downstream will
show it.

- **Where:** the `ktg_wbe` container log.
- **Look for:** `KtgSignalHandler - Published signal ... to KTG` for the symbol +
  signal type + timestamp.
- **Found it?** → go to Step 2. **Absent?** → root cause is upstream in kotquant; stop
  here and investigate the strategy's signal-emission path.

## Step 2 — Did korpse receive it?

- **Where:** `worker_<accountId>.log` on the Kore host. Resolve the account id first
  (main log `accountName=...`; korpse default is **204018 / AStark Kore 09**).
- **Pull it:** `kore-logs` skill (read-only). Recipes:

  ```bash
  # list the log dir / find worker files
  python3 ~/repos/korpse/scripts/fetch_kore_logs.py --env live --list

  # one symbol across a worker file
  python3 ~/repos/korpse/scripts/fetch_kore_logs.py --env live --account <id> --grep TEAM

  # only the decision events, since market open today
  python3 ~/repos/korpse/scripts/fetch_kore_logs.py --env live --account <id> \
      --events signal_received,increase_accept,increase_ignored,increase_rejected,order_submit,order_submit_skipped \
      --since "YYYY-MM-DD 09:30"
  ```

  (`--env live` needs `KORE_LOG_PASSWORD`; `--env fwd` uses `KORE_LOG_PASSWORD=access`.)

- **Look for:** `signal_received` for the symbol. **Absent?** → the signal was
  published but korpse didn't get it: check routing (`shell_id`/`account_id` mismatch,
  `symbol` mismatch), the `event_channel` (default `stark/events4`), or whether the
  korpse instance for that symbol/account is running.

## Step 3 — Did korpse accept it, or drop it?

For an **Increase**, accepting means transitioning to `Increasing`.

| Log event | Meaning | Cause |
|-----------|---------|-------|
| `increase_accept` | Accepted → `Increasing` | go to Step 4 |
| `increase_ignored reason=no_active_trade` | **Most common.** No open position when the Increase arrived | Increase only works from `Active`/`Increasing`; position was `None`/`Pending` |
| `increase_ignored reason=exit_in_progress` | Position was being exited | Increase ignored while `Exiting` |
| `increase_ignored reason=reduce_in_progress` | Position was being reduced | Increase ignored while `Reducing` |
| `increase_ignored reason=invalid_target` | Computed target ≤ current filled | would shrink exposure, not add (check `score`/`quantity`) |
| `increase_rejected reason=risk_cap_blocked cap=...` | Risk limit hit at accept time | `max_order_shares` / `max_position_notional` / `max_buying_power` / etc. |

(Analogous events exist for Entry/Reduce/Modify; the `*_ignored`/`*_rejected` reason
strings tell you which guard fired.)

## Step 4 — Did the order actually submit?

Accepted but still no order on Kore:

| Log event | Meaning |
|-----------|---------|
| `order_submit` | Order sent — it did go out (check the main log / Kore acks/fills) |
| `order_submit_skipped reason=trading_halted` | Symbol halted, no limit-on-open path |
| `order_submit_skipped reason=non_positive_qty` | Sizing rounded to 0 (e.g. volume sizing) |
| `order_submit_skipped reason=invalid_market_data` | No/stale bid-ask |
| `wide_spread_gate_tripped action=reject\|defer` | Spread too wide |
| `locate_rate_gate_tripped action=defer` | HTB symbol, locate rate-limited |

If you see `increase_accept` but **no** `order_submit` and **no** skip event, the
order action was generated but suppressed silently — usually no valid bid/ask
(`has_valid_adjust_market` false) or the target was already met (`diff == 0`).

## Common root causes (lead with the first)

1. **Increase before the position was open** → `increase_ignored: no_active_trade`.
   The fix is timing/sequencing on the strategy side, not korpse. This is the first
   thing to check for "we got an increase signal but didn't add."
2. Routing mismatch (`shell_id`/`symbol`) → `signal_received` absent.
3. Risk cap → `increase_rejected: risk_cap_blocked`.
4. Market conditions at submit → `order_submit_skipped` / `wide_spread_gate_tripped`.

## Worked example — 2026-06-12 TEAM, RBLX, APLD

All three published Increase signals from the WBE engine (`wisp-ktg-wbe` on epyc,
`KtgSignalHandler - Publishing increase signal`). All three were **received by korpse**
and **dropped as `increase_ignored reason=invalid_target`** — but for two distinct
reasons. None produced an add order.

| Symbol | Acct / shell (strategy) | Position when Increase arrived | Increase | Drop | Root cause |
|--------|------------------------|-------------------------------|----------|------|------------|
| TEAM | 14908 / `TpeLc1` (DijkstraSlide) | **short −367** | `qty=734 score=2.0` | `invalid_target proposed_target=734 current=-367` | **Sign bug.** korpse uses `signal.quantity` directly as a signed target; kotquant publishes it **positive** for a short → `+734` vs `−367` is opposite-sign → rejected. |
| RBLX | 14908 / `TpeLc1` (DijkstraSlide) | **short −859** | `qty=1718 score=2.0` | `invalid_target proposed_target=1718 current=-859` | Same sign bug (second short, identical pattern). |
| APLD | 14914 / `TpeLc4` (Ford) | **long 641** (planned 216) | `qty=432 score=2.0` | `invalid_target proposed_target=432 current=641` | **Overfill, not sign.** Position had grown to 641 via external `intent=none` fills, so the requested target (432, = 2×planned 216) was *below* the live position. |

In all three, a follow-up larger Increase one minute later hit `signal_throttled`
(inside the prior signal's `valid_until` window).

**Root cause in code** (`korpse/src/trade_plan_struct.h`, `update_for_increase`): when
`signal.quantity != 0` it sets `proposed_target = signal.quantity` (no direction
applied), then requires `same_direction` with `current_quantity` and
`abs(proposed_target) > abs(current_quantity)`. The `score × filled_quantity` branch
*is* correctly signed, but the explicit-quantity branch wins. Entry uses
`direction × abs(quantity)`; Increase does not — that asymmetry is the bug for shorts.

**How this was found (and a fetch caveat):**
- `fetch_kore_logs.py --env live --list` → 19 `worker_<acct>.log` (all `14xxx`).
- `--account 14914 --grep APLD` → APLD overfilled to 641; `increase_ignored invalid_target current=641`.
- `--account 14908 --grep TEAM` / `--grep RBLX` → short positions, `proposed_target` positive vs negative `current`.
- **Caveat:** looping the fetcher over all 19 accounts in one shot returns empty
  (rapid relay calls fail). Use **single calls or batches of ~4**; do not trust a
  bulk-loop negative. The main platform log (`2026-06-12.log`) does **not** carry the
  `Order -`/`sym=` worker lines, so it is not a reliable per-symbol order check —
  use the per-account `worker_<id>.log`.

**Takeaways:**
- `invalid_target` is the headline event for "got an increase, didn't add." Read its
  `proposed_target` vs `current`: **opposite sign** ⇒ short + unsigned published qty
  (the sign bug); **same sign, proposed ≤ current** ⇒ position already at/above target
  (often overfilled past plan via `intent=none` fills).
- Positions grew well beyond plan on all three via external `intent=none` fills
  (APLD→1282, TEAM→967, RBLX→2459) — a separate issue worth its own look.
