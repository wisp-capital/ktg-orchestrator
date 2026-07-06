# charon-ktgwisponly-ogden - live Charon on KTG WispOnly Ogden

Proofs live beside this file in `charon-ktgwisponly-ogden.proofs.toml`.

## What This System Does

Charon runs as an open Wisp strategy in the KTG WispOnly live trader. It is
enabled through the normal committed deploy path: `wisp-strategies` provides the
strategy class, `kotquant` includes it in `KtgWispOnlyStrategies`, and the KTG
allocator routes its strategy ref to the existing Ogden KTG shell/account.

## Domain Model

| Concept | Meaning |
| --- | --- |
| Charon | Open small-cap parabolic backside short strategy recreated from the old hub-rs Ogden behavior. |
| KTG WispOnly | Personal KTG broker instance deployed by `just deploy ktg_wisponly`. |
| Ogden account | Existing KTG account/shell for this rollout; Gr8Trade account `14448`. |
| Base risk | Strategy sizing input. This rollout uses `Charon(500.asRisk())`. |
| Capital envelope | Maximum single-position live notional permitted for this rollout. |

## Capability Model

### Live Routing

- `Charon(500.asRisk())` is present in `KtgWispOnlyStrategies`.
- Strategy ref `Charon` maps to the Ogden KTG shell/account.
- Deployment uses the standard epyc deploy script, which pulls committed `main`
  from `wisp-strategies` and `kotquant` before building the live jar.

### Risk Envelope

- The declared live capital guardrail is `capital`.
- The maximum notional for this rollout is `$150,000`, matching the Ogden
  account's configured `maxPositionValue`.
- The rollout does not create a new account or raise Ogden account limits.

## Lifecycle / State Model

```text
strategy PR merged -> kotquant routing PR merged -> capital envelope check -> ktg_wisponly deploy -> container/log verification
```

## Safety Rules

- Run `check_capital_envelope.py` with notional `150000` before broker
  connectivity or order routing.
- Do not deploy unless Charon exists on `wisp-strategies/main` and the kotquant
  routing change exists on `kotquant/main`.
- If deployment fails, leave the previous running container/version in place or
  roll back with the standard `just rollback ktg_wisponly <sha>` path.

## Edge Cases And Decisions

### What happens if kotquant CI runs before the strategy repo merges?

The kotquant build can fail because `Charon` is not yet available through the
normal `wisp-strategies` symlink. Merge the strategy repo first, then rerun or
refresh the kotquant PR checks.

> DECIDED: The strategy repo must land before the routing PR lands.

## What This System Will Not Do

- It will not increase Ogden account buying power, max position quantity, or
  max position value.
- It will not enable Charon on WBE/shared KTG accounts.
- It will not bypass the standard epyc deploy script.

## Reference: Scenario Catalog

- `SCN-LIVE-001`: Capital envelope allows the declared Ogden rollout notional.
- `SCN-LIVE-002`: Charon is present in KTG WispOnly and routed to Ogden.
