# Typhon bar-close decision alignment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Live Typhon enter/skip decisions match forge BT (bar-close clock + honest regime inputs).

**Architecture:** `StrategyConfig.entriesOnMinuteBarOnly` gates ContinuousScan scheduling, entry emission to `MinuteBarEvent` only, and disables live-quote entry defer. Typhon enables the flag. Fidelity BT runs without runtime-whitelist MD skew.

**Tech Stack:** Kotlin (kotquant stratio + wisp-strategies), JUnit tests, forge-bt for prove.

**Spec:** `ktg-orchestrator/docs/superpowers/specs/2026-07-10-typhon-decision-alignment-design.md`

**Worktree:** `workspace/<slug>/kotquant` on `stark/<slug>` (never primary checkout).

---

### Task 1: Config flag + StructuredStrategy gates

**Files:**
- Modify: `stratio/.../StrategyConfig.kt`
- Modify: `stratio/.../StructuredStrategy.kt`
- Test: `stratio/src/test/...` (new or extend existing StructuredStrategy test)

**Steps:**
1. Add `entriesOnMinuteBarOnly: Boolean = false` with doc comment.
2. Skip ContinuousScan schedule when flag true (live `schedulePostInitScans` / `onStart`).
3. In `evaluateForEntrySignalsAfterPattern` (or entry emit path): if flag and event !is MinuteBarEvent → return empty after optional onScan-only if needed; simplest: return empty before entry gates when not MinuteBar.
4. In `shouldDeferEntryUntilLiveQuote`: return false when flag true.
5. Unit test: flag on → Timer ContinuousScan / Quote defer do not produce Entry; MinuteBar can.
6. Commit: `feat: add entriesOnMinuteBarOnly for BT-aligned live entries`

### Task 2: Enable on Typhon

**Files:**
- Modify: `strategies/wisp-strategies/.../Typhon.kt`

**Steps:**
1. Set `entriesOnMinuteBarOnly = true` in `strategyConfig`.
2. Commit: `feat(typhon): enter only on minute bar close`

### Task 3: Prove decision Jaccard

**Files:**
- Optional script under kotquant/scripts or one-off
- Forge BT with `--use-source-files` and no runtime-whitelist skew

**Steps:**
1. Run forge Typhon 2026-05-28→2026-07-09 with full-regime MD.
2. Jaccard live Entry signals vs BT entries; target ≥80% (note: live signals are pre-change historical — prove unit behavior + document that live Jaccard needs post-deploy window OR simulate by replaying if available).
3. **Important:** Historical live signals were produced under ContinuousScan; post-deploy Jaccard is the real proof. Unit tests + code path parity are the ship gate; Jaccard on old signals is a lower bound / not expected to jump until new live tape.

**Ship gate:** unit tests green + Typhon flag on + PR. Jaccard remeasure after deploy (or note in PR).

### Task 4: Execution discrepancy note (secondary)

Append short “Execution findings” stub to design doc pointing at Dos dark days; no code fix.

---

## Out of scope

Dos/Kore blackout fix, Hydra/Chimera flag, PnL matching.
