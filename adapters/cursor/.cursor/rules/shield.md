# Agent-Shield — Dependency-Aware Remediation

## Rule: Query Before Risky Edits

When changing code in app factories, dependency injection, persistence, schemas, routing, orchestration, mapping, or auth:

1. Query `repo_universe/scripts/query_impact.py --target <target>` first (or manually map dependencies)
2. Restate the current contract before editing
3. Review blast radius, impacted tests, invariants
4. Edit only after impact is acknowledged
5. Verify against the impact surface, not just the local code path
6. Stop and ask if confidence is too low

## Manual Dependency Mapping (when no repo universe exists)

1. File imports and direct callers
2. Symbol references
3. Route handlers and dependency wiring
4. Tests with matching names or touched modules
5. ADRs and docs mentioning the target

## Required Output for Risky Edits

Include in your reasoning: target, current contract, intended change, blast radius, impacted tests, impacted docs/ADRs, invariants, verification plan, missing confidence.
