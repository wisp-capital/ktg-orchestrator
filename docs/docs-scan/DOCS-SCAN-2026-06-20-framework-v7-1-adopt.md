# Docs Coherence Scan — 2026-06-20 Framework v7.1 Adoption

Passes: 4

Paths reviewed:

- `AGENTS.md`
- `README.md`
- `Justfile`
- `justfile`
- `manifest.toml`
- `docs/navigation/README.md`
- `docs/navigation/manifest-index.md`
- `docs/navigation/manifest-index.json`

## Findings

Open high findings: 0
Open medium findings: 0
Open low findings: 0

## Fixes Made

1. Updated `manifest.toml` to declare `framework_version = "v7.1"` and
   `worktree_root = "workspace/"`.
2. Added v7.1 helper recipes for context audit, docs-scan status/prompt/record,
   and agent metrics.
3. Updated `AGENTS.md` from the v6 operating-model summary to the v7.1 Spec tree,
   proof, unowned-behavior, and materialization language.
4. Regenerated the manifest navigation index.

## Verification

- `just nav-check`
- `just amx check`
- `just context-audit`
- `just docs-scan-status --max-age-days 7`

## Blind Spots

This focused scan covers the KTG orchestrator framework adoption surface. It
does not audit the wrapped source repos.
