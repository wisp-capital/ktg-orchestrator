# Specs — the one work artifact

A **Spec** is one target-state record: `specs/<slug>.spec.md`. It is the decision and
the contract. Format and full model: ai-max `templates/template.spec.md` and
`docs/operating-model.md`. Scaffold one with `just amx new <slug>`; elicit one
from rough intent with the bundled `amx-spec` skill (hard rule 8).

A Spec has a `+++`-fenced TOML frontmatter (the machine surface) and prose below
(`## Intent`, `## Scenarios`, `## Decisions`, `## Constraints & Tradeoffs`,
`## Context`). A big effort is a parent Spec with child Specs (`parent` /
`children` frontmatter).

## Well-formedness (what `just amx check` enforces)

- `+++` frontmatter parses, with `id`, `status`, and a `guardrails` list.
- Specs with `"capital"` in `guardrails` declare a numeric `capital_budget_usd`.
- `## Intent` is present and non-empty.
- `## Scenarios` has at least one bullet, and **every scenario names a runnable
  check** — either set `eval = "<area>"` in the frontmatter (the whole area's
  eval is the proof) or put `check: ...` on every scenario line.
- `## Constraints & Tradeoffs` is present (per-feature boundaries the builder
  must honor).

## The loop

```
just amx new <slug> → write Intent + Scenarios → you approve → build → eval green → merge
```

- State is derived: `just state` generates the dashboard from Specs + git/PR +
  eval reports. Do not hand-maintain `STATUS.md`.
- Proof: `just amx eval <area>` runs `evals/<area>/eval.py`.
- Capital guardrail: a Spec with `"capital"` in `guardrails` must pass
  `~/repos/ai-max/scripts/check_capital_envelope.py` before any real order or
  broker connectivity. KTG work touches live trading — use it.
