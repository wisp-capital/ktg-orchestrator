# judelaw-imbalance-sleeve — JudeLaw auction / imbalance sleeve

Proofs live beside this file in `judelaw-imbalance-sleeve.proofs.toml`.

## What This System Does

JudeLaw (Gr8Trade `14449`) is the KTG WispOnly home for auction and
imbalance trading. The sleeve is one coherent family — not a pile of near-
duplicate largecap imbalance variants — with two live modes:

| Mode | Session | Strategy |
| --- | --- | --- |
| Close continuation (short) | last minutes into the close | `JudeLawImbalanceSellPressure` |
| Close clearing convergence | last 3 minutes into the close | `JudeLawClosingAuctionConvergence` |
| Open fade | pre-open | `JudeLawOpeningAuctionConvergence` |

Strategies that do not earn a distinct mode (JudeLawV2, HughGrant, TransitV2,
BrintDavy) stay out of the live sleeve.

Capital uses the existing JudeLaw envelope: $750K buying power, $75K max
position value. Primary risk sits on ImbalanceSellPressure; secondary on
ClosingAuctionConvergence; OpeningAuctionConvergence is sized smaller until
open liquidity is proven.

## Domain Model

| Concept | Meaning |
| --- | --- |
| JudeLaw sleeve | The auction/imbalance capital bucket on KTG shell/account JudeLaw (`14449`). |
| Close continuation | Trade with accelerating institutional sell imbalance into the close (short-only). |
| Close convergence | Trade continuous price toward auction clearing when they diverge (both sides). |
| Open fade | Fade pre-open clearing vs reference dislocation; expect reversion after the open. |
| Capital envelope | JudeLaw `maxPositionValue` = $75,000; Spec capital budget matches that ceiling. |

## Capability Model

### Live Routing

- `JudeLawImbalanceSellPressure`, `JudeLawClosingAuctionConvergence`, and
  `JudeLawOpeningAuctionConvergence` are present in `KtgWispOnlyStrategies`
  as strategy-ref aliases and map only to the JudeLaw shell/account.
- Unaliased `ClosingAuctionConvergence` / `ImbalanceSellPressure` /
  `OpeningAuctionConvergence` refs are not active on WispOnly (Centerpoint may
  still run its own copies).
- JudeLaw’s Kore worker starts at early premarket so open-fade signals can
  execute; it is not limited to a 15:00 ET start.

### Risk Envelope

- Guardrail is `capital` with budget `$75,000` (existing JudeLaw max position).
- Live risk amounts are sized to use that envelope: ISP primary, CAC secondary,
  Opening smaller.
- Per-strategy `maxNotionalPerTrade` must not sit below the JudeLaw max
  position when the alias is meant to fill the envelope.
- One JudeLaw auction position per symbol per session: if ISP and CAC both
  qualify on the same name, ISP wins (stricter mega-flow gate). Existing
  TargetState open-position dedup is the V1 enforcement.

### Non-goals for this sleeve

- Do not wire JudeLawV2, HughGrant, TransitV2, or BrintDavy as live siblings.
- Do not invent a close-fade strategy until an event study supports it.
- Do not raise JudeLaw buying power or max position in V1.

## Lifecycle / State Model

```text
Spec approved -> a1-strategies notional floors (if needed) -> kotquant wiring
  -> infra JudeLaw schedule early-premarket -> capital envelope check
  -> ktg_wisponly deploy + kore-scheduler deploy -> live signal/fill watch
```

## Safety Rules

- Run `check_capital_envelope.py` with notional `75000` before broker
  connectivity or order routing for this Spec.
- Do not deploy kotquant routing until strategy classes exist on
  `a1-strategies/main` (or the vendored path kotquant builds against).
- Deploy Kore schedule changes on trx50 via the standard infra path; do not
  leave JudeLaw at 15:00-only if OpeningAuction is live on that shell.

## Edge Cases And Decisions

### What if ClosingAuction and SellPressure both fire on the same mega-cap?

ISP is the primary close-continuation short. CAC may also qualify on clearing
divergence. V1 accepts TargetState “already open” dedup and documents ISP as
priority; a dedicated conflict gate is V2.

> DECIDED: One position per symbol per JudeLaw session; ISP preferred over CAC.

### What if open fade has poor premarket liquidity?

OpeningAuctionConvergence stays at reduced risk versus ISP/CAC until live
fills prove capacity. Do not size it to the full envelope in V1.

> DECIDED: Opening leg is intentionally smaller than the close legs.

## What This System Will Not Do

- It will not raise JudeLaw account buying power, max position quantity, or
  max position value in V1.
- It will not promote the old largecap imbalance quartet as separate live
  strategies on JudeLaw.
- It will not claim research-feed “auction blocked” status applies to live
  KTG — live already consumes Nasdaq/NYSE imbalance events.

## Reference: Scenario Catalog

- `SCN-LIVE-001`: Capital envelope allows the declared JudeLaw rollout notional.
- `SCN-LIVE-002`: Three JudeLaw aliases are wired and routed to JudeLaw.
- `SCN-LIVE-003`: JudeLaw Kore schedule starts at early premarket (not 15:00-only).
