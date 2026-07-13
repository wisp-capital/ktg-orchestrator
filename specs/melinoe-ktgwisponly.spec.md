# melinoe-ktgwisponly - live Melinoe on KTG WispOnly

Proofs live beside this file in `melinoe-ktgwisponly.proofs.toml`.

## What This System Does

Melinoe runs as an open Wisp strategy in the KTG WispOnly live trader. It is
enabled through the normal committed deploy path: `wisp-strategies` provides the
strategy class, `kotquant` includes it in `KtgWispOnlyStrategies`, and the KTG
allocator routes its strategy ref to the existing Icarus KTG shell/account.

## Domain Model

| Concept | Meaning |
| --- | --- |
| Melinoe | Open small-cap parabolic backside short strategy recreated from the old hub-rs Icarus behavior. |
| KTG WispOnly | Personal KTG broker instance deployed by `just deploy ktg_wisponly`. |
| Icarus account | Existing KTG account/shell for parabolic backside shorts; Gr8Trade account `14444`. |
| Capital envelope | Maximum single-position live notional permitted for this rollout. |

## Capability Model

### Live Routing

- `Melinoe(2500.asRisk())` is present in `KtgWispOnlyStrategies`.
- Strategy ref `Melinoe` maps to the Icarus KTG shell/account.
- Deployment uses the standard epyc deploy script, which pulls committed `main`
  from `wisp-strategies` and `kotquant` before building the live jar.

### Risk Envelope

- The declared live capital guardrail is `capital`.
- The maximum notional for this rollout is `$75,000`, matching the Icarus
  account's configured `maxPositionValue`.
- The rollout does not create a new account or raise Icarus account limits.

## Lifecycle / State Model

```text
strategy PR merged -> kotquant routing PR merged -> capital envelope check -> ktg_wisponly deploy -> container/log verification
```

## Safety Rules

- Run `check_capital_envelope.py` with notional `75000` before broker
  connectivity or order routing.
- Do not deploy unless Melinoe exists on `wisp-strategies/main` and the kotquant
  routing change exists on `kotquant/main`.
- If deployment fails, leave the previous running container/version in place or
  roll back with the standard `just rollback ktg_wisponly <sha>` path.

## Edge Cases And Decisions

### What happens if kotquant CI runs before the strategy repo merges?

The kotquant build can fail because `Melinoe` is not yet available through the
normal `wisp-strategies` symlink. Merge the strategy repo first, then rerun or
refresh the kotquant PR checks.

> DECIDED: The strategy repo must land before the routing PR lands.

## What This System Will Not Do

- It will not increase Icarus account buying power, max position quantity, or
  max position value.
- It will not enable Melinoe on WBE/shared KTG accounts.
- It will not bypass the standard epyc deploy script.

## Reference: Scenario Catalog

- `SCN-LIVE-001`: Capital envelope allows the declared Icarus rollout notional.
- `SCN-LIVE-002`: Melinoe is present in KTG WispOnly and routed to Icarus.
