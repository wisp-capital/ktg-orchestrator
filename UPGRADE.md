# Framework Upgrades

Use this file when ai-max `FRAMEWORK_VERSION` changes.

## Upgrade Path

1. Update local ai-max first: `git -C ~/repos/ai-max pull --ff-only`.
2. Run `just upgrade-plan` in this orchestrator and read the ordered adoption steps.
3. Compare this repo with `~/repos/ai-max/templates/orchestrator-bootstrap/`.
4. Copy or merge bootstrap changes, preserving repo-specific `manifest.toml`
   entries, domain notes, and local command customizations.
5. Set `framework_version` in `manifest.toml` to the value in
   `~/repos/ai-max/FRAMEWORK_VERSION`.
6. Run `just nav-index` so generated navigation files match `manifest.toml`.
7. Run `just orchestrator-check` and fix every `FAIL` line.
8. Open a PR titled `chore: adopt ai-max <version>`.

`just orchestrator-check --strict-docs` additionally fails when the recurring
docs coherence scan is stale or still has high-severity findings. Use that mode
only when this repo chooses to gate docs freshness in CI.
