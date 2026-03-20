---
name: validate-universe
description: Validate the repo universe — checks that all node/edge references resolve, curated overlays are consistent, and invariants have verification obligations.
---

# /validate-universe — Validate Repo Universe

Check the integrity of your repo universe.

## What It Checks

1. **Manifest** — generation metadata is present and valid
2. **Node integrity** — all nodes have required fields (id, type, source, freshness, confidence)
3. **Edge integrity** — all `from` and `to` references resolve to real node IDs
4. **Overlay resolution** — all targets in invariants, ownership, and source-of-truth files resolve
5. **Invariant completeness** — every invariant has at least one verification obligation
6. **Staleness** — flags nodes or edges with timestamps older than a threshold
7. **Contract consistency** — dispatch the `contract-mapper` agent to verify that curated contracts still match the codebase

## Usage

```
/validate-universe
```

## Output

- PASS with summary, or
- FAIL with specific violations listed

## When to Run

- After `/map` generates a new universe
- After editing curated overlays
- In CI as a pre-merge check
