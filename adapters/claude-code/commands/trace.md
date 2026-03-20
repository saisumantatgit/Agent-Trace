---
name: trace
description: Run safe remediation — map blast radius before editing risky code
---

Load and follow the safe-remediation skill from the prompts directory.

Read `prompts/trace.md` for the full workflow. Execute all 7 steps:

1. Identify the edit target
2. Query impact (script or manual fallback)
3. Restate the contract
4. Inspect blast radius
5. Edit only after impact is understood
6. Verify against the impact surface
7. Escalate if confidence is too low
