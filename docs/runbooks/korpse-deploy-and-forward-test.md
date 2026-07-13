# Runbook: deploy a korpse change to ForwardTest + run the fwd-test suite

Use this to ship a korpse (KTG execution worker) source change to the **ForwardTest**
Kore environment and prove it live with `scripts/test_forward.py`. This is the exact
sequence that landed the TWAP slicer on 2026-07-13; every step here is a place a
first attempt actually broke.

Related: the `korpse-fwd-test` skill (runs the suite), the `kore-logs` skill /
[`missing-order.md`](./missing-order.md) (reads worker logs), `docs/context/ktg-system.md`.

## Fixed facts (korpsev4 / ForwardTest)

| Thing | Value |
|-------|-------|
| Strategy GUID | `3113d4e9-1296-442a-b0b4-c620db62243d` (name `korpsev4`) |
| Kore account | `203607` ("AStark Kore8"), env **ForwardTest** |
| Fwd-test shell | **`StarkFwdTest1`** — NEVER `Default` (Default fans out to LIVE accounts) |
| Where `kti` lives | **trx50** (`/usr/local/bin/kti`), scoped to ForwardTest — `kti strategy list` header confirms |
| kore version | `4.1.13` |
| Signal endpoint | `tcp://epyc.nyc:30087` (events4 bus) |
| Fwd worker log | `logaccess@10.10.10.127:/kcore_fwd_logs/worker_203607.log` (pw `access`) — **only reachable via the trx50 relay** |

## Prerequisite: the agent needs kti access

`kti forward start` / signal-publish are outward-facing and the auto-mode classifier
blocks them by default. `permissions.allow` does NOT clear it (that gate is
`autoMode`). Add a standing-approval entry to `autoMode.allow` in
`~/.claude/settings.json` (the user must add it — the agent can't self-author consent),
scoped to ForwardTest / `StarkFwdTest1` only. See the 2026-07-13 TWAP session.

## Deploy (source → Kore)

1. **Push your korpse branch** to origin.
2. **Deploy from a CLEAN worktree on trx50 — do NOT use `/root/repos/korpse`.** That
   primary checkout is often dirty and on a deploy branch (`deploy/so-upload-pipeline`).
   ```bash
   ssh trx50 'cd /root/repos/korpse && git fetch origin <branch> \
     && git worktree add /root/repos/korpse-<slug> <sha>'
   ```
3. **Upload + build:**
   ```bash
   ssh trx50 'cd /root/repos/korpse-<slug> && just upload && just build'
   ```
   - `just upload` → `kti strategy upload` (bundles `src/korpse.cpp` + headers).
   - `just build` → `kti strategy build <guid> --kore-version 4.1.13 --wait` (server-side compile).
   - ⚠️ **New header?** `scripts/bundle-upload-source.sh` requires a per-file **section
     title + description** for every bundled header. A new `foo.h` fails with
     `missing explicit section metadata for bundled file: foo.h`. Add a case to BOTH
     `section_title()` and `section_description()`, commit, re-push, re-deploy.
4. **Verify the source actually took** (this is the "editor" content):
   ```bash
   ssh trx50 'kti strategy list | grep korpsev4'              # date should be TODAY
   ssh trx50 'kti strategy code <guid> | grep -c <your-new-symbol>'   # >0
   ```
   - ⚠️ **`kti einstein sync-script` does NOT exist** in this kti version (a stale hint
     printed by `kti strategy upload`). The `kti strategy upload` IS the editor/source
     update — no separate sync step. Don't chase it.

## Start the fwd instance (so it runs the new build)

A running instance keeps its old artifact — (re)start it after deploy:
```bash
ssh trx50 "kti forward running --account 'AStark Kore8' --json"   # check
ssh trx50 "kti forward start 3113d4e9-1296-442a-b0b4-c620db62243d \
  --account 'AStark Kore8' --all-symbols --params '{\"shell_id\":\"StarkFwdTest1\"}'"
```
Stop later with `kti forward stop <guid> --account 'AStark Kore8' --symbol "" \
--instruction-id '{...}'` (get the id from `kti forward running --json`).

## Run the test + verify

- **Run** (via the `korpse-fwd-test` skill, or its raw env command). It runs LOCALLY,
  publishes to `tcp://epyc.nyc:30087`, and polls the worker log through the relay:
  ```bash
  /korpse-fwd-test --test <name>      # e.g. twap_entry ; --list to see all
  ```
  - ⚠️ **RTH only** for Passive-priced tests — Passive limits rest at the bid; if the
    bid isn't hit in-window the test's `order_fill` gate fails even though placement
    worked. Fills are market-dependent; slicing/placement is what's really under test.
  - Signal quantities are auto-scaled ~10x down; blast radius is tiny.
- **Verify from the log** (`kore-logs` skill / `fetch_kore_logs.py --env fwd`):
  ```bash
  KORE_LOG_PASSWORD=access python3 ~/repos/korpse/scripts/fetch_kore_logs.py \
    --env fwd --account 203607 --grep <SYMBOL>
  ```
  Read `entry_accept` (armed qty), the `order_submit ... qty=... intent=init` children,
  and `order_fill`. For TWAP: children are `target/slices`, spaced the slice interval;
  Passive reprices repeat the same `qty` at `current=<held>` (no drift).

## Cleanup

```bash
ssh trx50 "kti forward stop 3113d4e9-... --account 'AStark Kore8' --symbol '' --instruction-id '{...}'"
ssh trx50 'git -C /root/repos/korpse worktree remove --force /root/repos/korpse-<slug>'
```

## Gotcha index (what broke first, on 2026-07-13)

1. New header (`twap_slicer.h`) → `just upload` failed on missing bundler section metadata.
2. trx50 `/root/repos/korpse` was dirty on a deploy branch → deployed from a clean worktree instead.
3. `kti einstein sync-script` errored (`unknown flag: --guid`) — command doesn't exist; upload already updated the source.
4. `kti forward start` + signal-publish were auto-mode-blocked → needed an `autoMode.allow` grant (not a `permissions.allow` rule).
5. Fwd log host `10.10.10.127` unreachable directly → only via the trx50 relay (the fetch script handles this).
6. `KORPSE_FORWARD_ENDPOINT` etc. are not in any shell env — the `korpse-fwd-test` skill supplies them.
