# checkpoints/

Phase handoff docs for deep, multi-phase initiatives. When work is large enough to
split into waves, the design and per-phase handoffs live here so another session (or
subagent) can pick up without re-deriving context.

Typical files for an initiative `<slug>`:

- `<slug>-design.md` — the full phased plan: context, validated hotspots, parts/phases
  in ROI order, risks.
- `<slug>-wave<N>.md` — a single wave's handoff: linked INIT doc, worktree paths, the
  phase's scope, expected file changes, verification commands, blockers.

Keep these in sync with the initiative's `STATUS.md` row and its `initiatives/INIT-*.md`.
