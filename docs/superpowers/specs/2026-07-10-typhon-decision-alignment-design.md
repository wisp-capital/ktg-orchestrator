# Typhon live↔backtest decision alignment

Date: 2026-07-10  
Status: implemented — awaiting merge/deploy  
Repos: kotquant (Typhon / StructuredStrategy / forge BT); analysis in ktg-orchestrator

## Problem

Over 2026-05-28 → 2026-07-09, live Typhon on Dos and a forge Typhon backtest disagree badly on dollars (−$3.3k live closed vs −$0.8k BT at $1k risk). Decomposition showed two separate discrepancies:

| Discrepancy | What it is | Evidence |
|-------------|------------|----------|
| **Decision-making** | Live and BT enter/skip different symbol-days | Jaccard ~26%; 10 matched closed names agree within ~$70 at equal risk |
| **Execution** | Live signals with no Dos fills | 9 days Dos had **zero account-wide Gr8 fills** despite Typhon signals |

On shared decisions, the edge model matches. The dollar gap is mostly different books + Dos blackouts—not slippage on overlaps.

## Priority

1. **Primary (this design):** align **decision-making** so live enter/skip matches the backtest clock and regime inputs. Fills may still differ.
2. **Secondary (understand, not fix here):** document and diagnose the Dos execution blackouts so we know why signals did not become tape. No Kore/locate code change in this workstream unless diagnosis proves a one-line footgun.

## Goal (primary)

Live Typhon and forge BT make the same **enter/skip** decisions.

Success metric: **decision Jaccard** =

`|live Entry signals ∩ BT entry (date, symbol)| / |union|`

Target: **≥ 80%** on a re-run of 2026-05-28 → 2026-07-09 after the change (baseline ~26%). Ignore NeverFilled, open positions, and fill PnL for this metric.

## Non-goals

- Forcing symbol-exact **fills** or matching live PnL to BT PnL
- Fixing Dos/Kore locate/risk blackouts (secondary track only)
- Changing Hydra/Chimera wiring unless they opt into the same flag later
- Re-tuning Typhon item criteria / score floors (orthogonal)

## Approach (approved): live adopts BT’s decision clock

### A1. Bar-close-only entries (live)

Add `StrategyConfig.entriesOnMinuteBarOnly: Boolean = false`. Typhon sets it `true`.

When true:

1. Do **not** schedule `ContinuousScan` in live for that strategy (BT already skips ContinuousScan for `AlgoBuySellPattern` because `includeTrades()` is false).
2. Entry evaluation / Entry emission only from `MinuteBarEvent` (same path BT uses today via `onMinuteBar` → `evaluateForSignals`).
3. Disable `shouldDeferEntryUntilLiveQuote` for that strategy so entry publishes on the bar close, not a later quote (avoids reshuffling which names consume daily/concurrent slots).
4. Existing-position eval, halt handlers, and exits unchanged.

Implementation surface (kotquant):

- `StrategyConfig.kt` — new flag + doc comment
- `StructuredStrategy.kt` — gate ContinuousScan scheduling; gate entry path by event type; skip live-quote defer when flag set
- `Typhon.kt` — enable the flag

### A2. Honest BT regime inputs

Forge/runtime pattern whitelists shrink `MarketMd.symbolMdMap`, so `avgChangeAtrs(MidCapPlus)` in BT ≠ live (full MidCapPlus). Typhon items gate on that average.

For Typhon fidelity / compare runs:

- Prefer full MidCapPlus in MD aggregates: e.g. run with runtime whitelist off / `scopeInitDataToSymbolWhitelist=false`, or equivalent forge flags documented in this spec’s verify section.
- Do not treat a whitelist-skewed BT as the decision-alignment target.

Optional hardening (if flag-only is fragile): keep fill/event whitelist but compute universe aggregates from an unscoped MD view. Only if A2-via-flags is insufficient in the prove step.

### A3. Proof

1. **Unit tests:** with `entriesOnMinuteBarOnly=true`, ContinuousScan and quote-defer paths do not emit Entry; MinuteBar still can.
2. **Replay compare:** re-forge Typhon over 2026-05-28 → 2026-07-09 with honest regime inputs; compute decision Jaccard vs live `signals` (Typhon Entry). Report before (~26%) and after (≥80% target).
3. Matched-name PnL check remains a sanity check only (already ~aligned).

## Secondary track: understand execution discrepancy

Already known:

- Backfilled `NeverFilled` on Dos = signal present, no matching Gr8 fill (not Centerpoint `ExitReason.NeverFilled` writers on the KTG path).
- On 2026-06-02, 06-04, 06-22, 06-24, 06-25, 06-26, 06-29, 06-30, 07-01: **entire Dos account** had zero Gr8 fills while Typhon still published signals (mix of Buy and Sell).

### Execution findings (2026-07-10)

- Confirmed via `/tmp/dos_trades_cache.json` (Gr8 matched trades for account 14924): those nine dates have `dos_fills=0` account-wide, not Typhon-only.
- Fill days in the same window (e.g. 2026-05-28, 06-12, 07-06) show normal Dos tape.
- Implication: decision alignment (this design) will not fix dark-day PnL; Kore/korpse path for Dos needs a separate ops dig (`worker_14924` / `signal_received` vs reject/skip).

Follow-up (read-only / ops), after or parallel to A:

1. Pull Kore `worker_14924` / korpse logs for one dark day vs one fill day (e.g. 2026-06-25 vs 2026-07-06).
2. Classify: signal never received vs `entry_rejected` vs `order_submit_skipped` vs resting unfilled.
3. Write a short note under `docs/runbooks/` — no behavior change unless a clear bug.

Out of scope for the primary PR.

## Risks

- Live may enter slightly later and miss some mid-bar names that previously filled; that is intentional (match BT).
- Composite first-match can still diverge if bar MD differs live vs historical feed; 80% is the bar, not 100%.
- Disabling quote-defer changes live entry price slightly vs today; decisions (which symbol) are the priority.

## Verify commands (post-implement)

```text
# unit (kotquant)
./gradlew :stratio:test --tests '*entriesOnMinuteBarOnly*'   # or concrete test class name

# forge BT with full-regime inputs (exact flags TBD in plan)
./scripts/forge-bt.sh Typhon --start 2026-05-28 --end 2026-07-09 --use-source-files ...

# decision Jaccard vs live signals on epyc postgres
# (script or one-off: |sig ∩ bt| / |sig ∪ bt| on date+symbol)
```

## Decision log

- 2026-07-10: Care about both discrepancies; **decision-making is the priority to fix now**.
- 2026-07-10: Align on decisions even if executed trades differ.
- 2026-07-10: Approved Approach A (live adopts BT bar-close clock + honest BT regime).
