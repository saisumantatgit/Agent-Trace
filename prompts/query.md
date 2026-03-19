# Impact Query Prompt

You are querying the repo universe to understand the impact of changing a specific target.

## Input

- **Target**: a file path, symbol ID, or endpoint ID
- **Change type** (optional): behavioral, schema, doc, or test

## How to Query

If `repo_universe/scripts/query_impact.py` exists:
```
python repo_universe/scripts/query_impact.py --target <target> [--change-type <type>]
```

If no script exists, manually map:
1. File imports and direct callers of the target
2. Symbol references across the codebase
3. Route handlers and dependency wiring
4. Tests with matching names or touched modules
5. ADRs and docs mentioning the target

## Required Output Fields

- `target` — what is being changed
- `current_contract` — what the target currently does
- `direct_dependencies` — things the target directly depends on
- `indirect_dependencies` — transitive dependencies
- `backward_prerequisites` — things that must be true for the target to work
- `forward_blast_radius` — things that will break if the target changes
- `impacted_tests` — tests that exercise the target
- `impacted_docs_and_adrs` — documentation that references the target
- `invariants` — must-not-break contracts involving the target
- `source_of_truth` — authoritative sources for the target's behavior
- `verification_obligations` — what to verify after the change
- `risk_summary` — one-line risk assessment
- `confidence` — 0.0 to 1.0
- `stale_areas` — known outdated information
- `unmapped_or_low_confidence_areas` — gaps in the map

## Rules

- Prefer precise node IDs when available
- Include low-confidence gaps rather than hiding them
- Empty arrays are acceptable when the map truly contains no evidence
- Output must be machine-readable JSON
