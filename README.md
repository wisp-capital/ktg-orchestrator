# ktg-proxy

A proxy / orchestration meta-repo for KTG (Kore Trading Gateway) related work.

Wraps KTG-related source repos, provides a single workspace for cross-cutting
development, and ships changes back to each repo's origin as a pull request.

It is **orchestration-only**: it stores no source code. The real source lives in
each repo's own checkout listed in `manifest.toml`. ktg-proxy only holds a
manifest, a Rust-based tool, and docs. Assembled worktrees land in `workspace/`
(gitignored) at runtime.

## Wrapped repos

`manifest.toml` is the source of truth — edit it to add repos for KTG work.

## Usage

```sh
just assemble my-task --repo kotquant --repo kore-proxy
just assemble my-task
just status
just ship --draft
just teardown --delete-branch
```

Without `just`, build and run the Rust tool directly:
```sh
cargo build --release
./target/release/ktg-proxy assemble my-task --repo kotquant
./target/release/ktg-proxy status
./target/release/ktg-proxy ship --draft
./target/release/ktg-proxy teardown --delete-branch
```

## How it works

- `manifest.toml` lists each wrapped repo: local path, remote, base branch, lang.
- `assemble <slug>` runs `git worktree add` in each source repo, creating
  `workspace/<name>` on branch `stark/<slug>` from `origin/main`. Your primary
  checkout is never touched.
- `ship` pushes each branch and runs `gh pr create --base main --fill` from
  inside the worktree, so the PR targets the right repo.
- `teardown` removes the worktrees (add `--delete-branch` to drop the branch).

## AI-max operating state

`/Users/alexcstark/repos/ai-max` is the reusable operating framework:
Intent -> Scenarios -> Build -> Verify -> Archive, shallow/deep/spike
classification, truth labels, maturity levels, and handoff patterns.

ktg-proxy holds the KTG-specific state for that framework:

- `STATUS.md` is the active initiative dashboard.
- `initiatives/` holds active INIT docs.
- `checkpoints/` holds deep-work handoff docs.
- `archive/` holds completed initiatives and spikes.

Implementation work still happens in linked repo worktrees under `workspace/`.

## Requirements

- Rust (latest stable)
- `git`, `gh` (authenticated), and optionally `just`
- The wrapped repos already cloned at the paths listed in `manifest.toml`
