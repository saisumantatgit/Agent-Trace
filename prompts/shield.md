# Safe Remediation Prompt

You are performing a dependency-aware remediation. Before editing any code, you must understand the blast radius.

## Workflow

1. **Identify the edit target** from the user's change request (file, symbol, route, or contract surface)

2. **Query impact** — run `python repo_universe/scripts/query_impact.py --target <target>` if available. If not, manually map dependencies:
   - File imports and direct callers
   - Symbol references
   - Route handlers and dependency wiring
   - Tests with matching names or touched modules
   - ADRs and docs that mention the target

3. **Restate the contract** before editing:
   - Current contract (what the code does now)
   - Intended change (what should change)
   - Non-goals (what should NOT change)
   - Fragile boundaries (where breakage is likely)

4. **Inspect impact** from the query result:
   - Direct and indirect dependencies
   - Backward prerequisites and forward blast radius
   - Impacted tests, docs, ADRs
   - Invariants and source-of-truth declarations
   - Stale or low-confidence areas

5. **Edit only after acknowledging impact** — do not touch risky boundaries until the query result is reviewed

6. **Verify against the impact surface**:
   - Reproduce the scenario or symptom
   - Run impacted tests
   - Verify the contract surface, not just the local path
   - State what was NOT verified

7. **Escalate** if confidence is too low — stop and ask the user

## Required Output

Your reasoning must include: target, current contract, intended change, blast radius, impacted tests, impacted docs/ADRs, invariants, verification plan, and missing confidence.
