# Agent-Trace — Dependency-Aware Remediation

## Before Risky Edits

When fixing bugs, regressions, or making changes that touch app factories, dependency injection, persistence, schemas, routing, orchestration, mapping, or auth:

1. **Query impact first**: Run `python repo_universe/scripts/query_impact.py --target <file-or-symbol>` if available, otherwise manually map dependencies
2. **Restate the contract**: Document current behavior, intended change, non-goals, fragile boundaries
3. **Inspect blast radius**: Review direct/indirect dependencies, backward prerequisites, forward blast radius, impacted tests, invariants
4. **Edit only after acknowledging impact**
5. **Verify against the impact surface**: Run impacted tests, verify contract surface, state what was NOT verified
6. **Escalate** if confidence is too low

## Building the Repo Universe

Run `python repo_universe/scripts/build_manifest.py` to generate the dependency graph.
Run `python repo_universe/scripts/validate_universe.py` to check integrity.

## Curated Overlays

Maintain these in `repo_universe/curated/`:
- `invariants.yaml` — must-not-break contracts with verification obligations
- `ownership.yaml` — subsystem and target ownership
- `source_of_truth.yaml` — which artifacts are authoritative when they diverge
