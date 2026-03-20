---
name: trace
description: Run the full safe-remediation workflow — identify target, query impact, restate contract, inspect blast radius, edit, verify. Use before any risky code change.
---

# /trace — Safe Remediation

Run the full dependency-aware remediation workflow before making a risky edit.

## What You Provide

Describe the change you need to make. Include:

- the file or symbol being changed
- what the change should accomplish
- any known constraints or concerns

## What Happens

1. **Identify** — Derive the edit target from your description
2. **Query** — Run `query_impact.py` against the repo universe (or manual fallback)
3. **Restate** — Document the current contract, intended change, non-goals, fragile boundaries
4. **Inspect** — Review blast radius: dependencies, tests, docs, invariants, stale areas
5. **Edit** — Make the change only after impact is understood and acknowledged
6. **Verify** — Run impacted tests, confirm contract surface, state what was NOT verified
7. **Escalate** — Stop and ask if confidence is too low

## Output

Structured remediation report:

- Target
- Current contract
- Intended change
- Blast radius
- Impacted tests
- Impacted docs/ADRs
- Invariants
- Verification plan
- Missing confidence

## Example

```
/trace Fix the auth middleware to reject expired tokens — currently it silently passes them through
```
