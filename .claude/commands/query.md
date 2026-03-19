---
name: query
description: Query the impact of changing a specific target — returns blast radius, dependencies, impacted tests, invariants, and confidence. Requires a repo universe built with /map.
---

# /query — Impact Query

Query the repo universe to understand the impact of changing a specific target.

## What You Provide

A target — one of:

- a file path: `src/app/auth.py`
- a symbol: `symbol:src/app/deps.py:get_data_store`
- an endpoint: `endpoint:GET:/api/v1/users`

Optionally, a change type:

- `behavioral` — logic change (default)
- `schema` — data shape change
- `doc` — documentation change
- `test` — test change

## What It Returns

```json
{
  "target": "...",
  "current_contract": "...",
  "direct_dependencies": [],
  "indirect_dependencies": [],
  "backward_prerequisites": [],
  "forward_blast_radius": [],
  "impacted_tests": [],
  "impacted_docs_and_adrs": [],
  "invariants": [],
  "source_of_truth": [],
  "verification_obligations": [],
  "risk_summary": "...",
  "confidence": 0.0,
  "stale_areas": [],
  "unmapped_or_low_confidence_areas": []
}
```

## Example

```
/query src/app/middleware/auth.py --change-type behavioral
```

## No Repo Universe?

If no repo universe exists, the query falls back to manual dependency mapping using file imports, symbol references, and test name heuristics. Confidence will be lower.
