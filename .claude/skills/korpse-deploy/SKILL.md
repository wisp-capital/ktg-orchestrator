---
name: korpse-deploy
description: "[korpse-deploy <branch-or-sha>]: Deploy a korpse source change to the ForwardTest Kore env via kti on trx50 — clean worktree -> just upload -> just build -> verify source -> (re)start the fwd instance on StarkFwdTest1. The DEPLOY half of the korpse fwd-test loop; pair with korpse-fwd-test (run) and kore-logs (verify)."
user_invocable: true
requires_approval: false
---

# korpse-deploy

Ships a korpse (KTG execution worker) source change to the **ForwardTest** Kore
strategy `korpsev4` and leaves it running the new build, ready to test. Every `kti`
command runs on **trx50** — that is where `kti` lives, scoped to the ForwardTest
environment. Full context + the war stories: the orchestrator runbook
`docs/runbooks/korpse-deploy-and-forward-test.md`.

The full loop is three skills: **korpse-deploy** (this — ship it) → **korpse-fwd-test**
(run a case) → **kore-logs** (verify the worker log).

## Prerequisite — kti grant

`kti forward start` and signal publishing are outward-facing; the auto-mode classifier
blocks them unless there is a standing-approval entry in `autoMode.allow` in
`~/.claude/settings.json` (a `permissions.allow` rule does NOT clear it — different gate).
The user must add it (the agent can't self-author consent), scoped to ForwardTest /
StarkFwdTest1 only. If blocked, stop and ask the user to add the grant or run the step
via `!`.

## Fixed facts

| Thing | Value |
|-------|-------|
| GUID | `3113d4e9-1296-442a-b0b4-c620db62243d` (`korpsev4`) |
| Account | `203607` ("AStark Kore8"), env **ForwardTest** |
| Fwd-test shell | **`StarkFwdTest1`** — NEVER `Default` (Default fans out to LIVE accounts) |
| kti host | **trx50**, `/usr/local/bin/kti`, ForwardTest-scoped |
| kore version | `4.1.13` |

## Steps (arg = the korpse branch name or sha to deploy)

1. **Push** the korpse branch to origin (caller usually did this).
2. **Deploy from a CLEAN worktree** — never the primary `/root/repos/korpse` (often dirty,
   on a deploy branch):
   ```bash
   ssh trx50 'cd /root/repos/korpse && git fetch origin <BRANCH> \
     && git worktree add -f /root/repos/korpse-deploy-tmp origin/<BRANCH>'
   ```
3. **Upload + build** (server-side compile, waits):
   ```bash
   ssh trx50 'cd /root/repos/korpse-deploy-tmp && just upload && just build'
   ```
   - **If `just upload` fails** `missing explicit section metadata for bundled file: X.h`:
     the new header `X.h` needs a case in `scripts/bundle-upload-source.sh` in BOTH
     `section_title()` and `section_description()`. Add it, commit, re-push, re-fetch the
     worktree, retry. (A korpse-side fix auto-defaults this — but older checkouts hard-fail.)
4. **Verify the source took** (this is the Script Editor content):
   ```bash
   ssh trx50 'kti strategy list | grep korpsev4'                          # date == today
   ssh trx50 'kti strategy code 3113d4e9-1296-442a-b0b4-c620db62243d | grep -c <new-token>'  # > 0
   ```
   - `kti einstein sync-script` does NOT exist in this kti — `kti strategy upload` IS the
     editor/source update. Don't chase it.
5. **(Re)start the fwd instance** so it runs the new build:
   ```bash
   ssh trx50 "kti forward running --account 'AStark Kore8' --json"
   ssh trx50 "kti forward start 3113d4e9-1296-442a-b0b4-c620db62243d \
     --account 'AStark Kore8' --all-symbols --params '{\"shell_id\":\"StarkFwdTest1\"}'"
   ```
6. **Report** upload + build status + the running instance, then hand off:
   `/korpse-fwd-test --test <name>` to run, then `kore-logs` to verify.

## Cleanup (after testing)

```bash
# instruction-id from `kti forward running --json`
ssh trx50 "kti forward stop 3113d4e9-1296-442a-b0b4-c620db62243d --account 'AStark Kore8' --symbol '' --instruction-id '{...}'"
ssh trx50 'git -C /root/repos/korpse worktree remove --force /root/repos/korpse-deploy-tmp'
```

## Safety notes

- Read-only kti (`strategy list`/`code`, `forward running`) is always safe.
- `upload`/`build`/`forward start`/`stop` mutate **ForwardTest only** — never live. The
  shell is always `StarkFwdTest1`; never `Default`.
- This does not touch live/production accounts or the KtgWispOnly/KtgWbe live rosters.
