# Preferences

Process and code tradeoffs for `ktg-orchestrator`. Per `AGENTS.md`, check here before
escalating on a tradeoff; if it's documented, apply it and log the decision. The
reusable cross-repo preferences live in `~/repos/ai-max/PREFERENCES.md`; this file
holds only KTG-specific tradeoffs.

| ID | Preference |
|----|------------|
| P-001 | **Never edit the primary checkouts.** All implementation happens in `workspace/<name>` worktrees created by `just assemble`. Changes to `ktg-orchestrator` itself go on a `stark/` branch / worktree of this repo, never on `main`. |
| P-002 | **Branch prefix `stark/`** for all task branches (set in `manifest.toml`). |
| P-003 | **Lowercase Conventional Commit** subjects and PR titles: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `perf:`, `ci:`. |
| P-004 | **One PR per repo.** `ship` pushes each worktree branch and opens a PR targeting that repo's `main`. Cross-cutting work becomes several coordinated PRs, not one. |
| P-005 | **Diagnose before code.** For operational questions ("why didn't an order go out"), start from `docs/runbooks/` and live logs (`kore-logs`, read-only) before reading or changing source. |
| P-006 | **Map, don't copy.** When documenting the system here, point at the authoritative per-repo doc; do not restate field-level contracts that can drift (`korpse/docs/signal-flow.md` owns signal semantics). |
| P-007 | **Never guess a live credential.** `KORE_LOG_PASSWORD` for `--env live` comes from the user / vault; `--env fwd` uses the documented value `access`. |
| P-008 | **Fix signal/order behavior in kotquant, not korpse, when possible** — korpse script promotion is painful, so prefer changing signal generation upstream. See AGENTS.md "Where to fix signal / order behavior". |
