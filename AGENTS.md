# Minimal agent contract — ktg-orchestrator

This is an orchestration-only repo. Source changes belong in explicitly
assembled worktrees; do not edit linked primary checkouts.

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
