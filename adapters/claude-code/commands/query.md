---
name: query
description: Query impact of changing a target — blast radius, tests, invariants
---

Query the repo universe for impact analysis.

Read `prompts/query.md` for full instructions. Execute:

1. Accept target (file path, symbol, or endpoint) from user
2. Run `python repo_universe/scripts/query_impact.py --target <target>`
3. If no script exists, perform manual dependency mapping
4. Present structured results with confidence levels
