# initiatives/

Active INIT docs — one file per initiative currently in flight. `STATUS.md` is the
dashboard; this directory holds the detail behind each active row.

Create an INIT for non-trivial work (cross-repo, multi-phase, safety-relevant, or
spanning sessions). Skip it for trivial edits (typos, single-file fixes) — those are
one-off todos in `SESSION_TODO.md`.

File name: `INIT-<short-kebab-id>.md`. Shape:

```markdown
# INIT - <Name>

**Status:** Intent | Scenarios | Build | Verify | Archive | Blocked
**Started:** YYYY-MM-DD
**Classification:** shallow | deep | spike
**Maturity target:** M0–M5
**Worktree slug:** <slug for `just assemble`>
**Linked repos:** <kotquant, korpse, kore-proxy>

## Intent
<Goal + guardrails in plain English>

## Scenarios            # the contract for deep work
### S-001: <Name>
Given <precondition> / When <action> / Then <observable>
Evidence: <test / command / report / artifact>

## Scope
- In:
- Out:

## Status Log
- YYYY-MM-DD: <phase / status / evidence>

## Next Autonomous Action
<one concrete action, or "none - complete">
```

When an initiative completes, move its INIT file to `archive/` and update `STATUS.md`.
