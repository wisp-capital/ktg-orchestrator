# ktg-orchestrator

A proxy/orchestration meta-repo for KTG (Kore Trading Gateway) work.
It wraps KTG source repos, provides isolated worktrees, and ships changes
back to each repo as a pull request. It stores no source code.

## Delivery model

This repository's Product Documents and cross-repository decisions describe
desired behavior, including future work. Current behavior comes from the owning
source repository's code, configuration, schemas, and ordinary tests. Select a
bounded delivery slice, make its scenarios concrete, then map them to the
owner's normal suite before implementation. Manual evidence is a retained
exception, not a parallel testing framework.

Review the actual owner code and tests for reuse before implementation. The
manifest and system map are routing aids, not behavior authorities.

## Wrapped repos

The active repos are listed in [`manifest.toml`](manifest.toml): kotquant,
kore-proxy, korpse, and infra.

## The KTG system

A kotquant/KTG strategy publishes a signal to ZMQ `stark/events4`; korpse runs
the trade-plan state machine and places the order; kore-proxy carries Kore
events back to internal systems.

- [`docs/context/ktg-system.md`](docs/context/ktg-system.md) — system map.
- [`docs/runbooks/missing-order.md`](docs/runbooks/missing-order.md) — missing
  order diagnosis.

## Usage

```sh
just assemble my-task --repo kotquant --repo kore-proxy
just assemble my-task
just status
just ship --draft
just clean --force
```

Implementation work happens in linked repo worktrees under `workspace/`.
Requirements: Python 3.11+, git, gh, and optionally just.
