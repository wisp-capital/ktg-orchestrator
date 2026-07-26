# Minimal agent contract — ktg-orchestrator

This is an orchestration-only repo. Source changes belong in explicitly
assembled worktrees; do not edit linked primary checkouts.

Product Documents, when this repo uses them, describe desired cross-repository
capability. The owning repositories' code, configuration, schemas, and ordinary
tests are authoritative for current behavior. An Inbox Work Item selects a
bounded delivery slice; it needs concrete scenarios and normal-suite proof
mappings before implementation; manual evidence is a retained exception when
automation is impractical. The dashboard is passive Product Document completion
plus Inbox state; do not create batches, Agent Runs, queues, headless workers,
dispatchers, or autonomous loops.

Before implementation, inspect the owning source and tests for reusable seams.
Build a shared foundation only for a repeatable need; otherwise implement
directly in the owning domain. The manifest and context map route that review;
they do not prove behavior.

- Never use the `Default` Kore shell for ForwardTest work; use the documented
  ForwardTest path and shell only.
- Live trading, broker, or capital actions require an explicit user request
  and the owning repo's existing capital guardrails.
- Default context is intentionally minimal. Do not run startup, state, scan,
  proof, inbox, or prompt workflows unless the task explicitly needs one.
- Optional skills and workflows are opt-in. Before activating one, announce
  its exact name and why. Every later user-facing update must include the
  active optional-context names until they are deactivated; announce removal.
- Use focused verification and lowercase Conventional Commit subjects.
