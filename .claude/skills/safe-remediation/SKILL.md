---
name: safe-remediation
description: >
  Use this skill for bug fixes, regressions, and risky code edits in mature repos
  where local changes may break adjacent contracts. It maps dependencies and
  invariants before edits, requires an agent query on fragile boundaries, and
  ties verification to the impacted surface.
license: MIT
compatibility: >
  Designed for agents with file search and shell or tool execution. Best results
  when a repo-universe query interface is available.
metadata:
  domain: software-engineering
  maturity: stable
  primary_use: remediation
allowed-tools: Read Glob Grep Bash
---

# Safe Remediation

Use this skill when a change is likely to affect more than one local file or contract surface.

## Trigger

Activate this skill when:

- the user asks to fix a bug, regression, or contract issue
- the change touches app factories, dependency injection, persistence, schemas, routing, orchestration, mapping, auth, or any known invariant surface
- the repo is large enough that local reasoning can silently miss blast radius

Do not activate this skill for:

- trivial formatting
- prose-only edits
- isolated local changes with no callable or data dependencies

## Workflow

### 1. Identify the edit target

Derive the target from the change request:

- changed file
- changed symbol
- changed route or endpoint
- contract surface named in the bug report

### 2. Run the agent query

If the repo-universe query interface is available, use it before editing.

Preferred shape:

```text
python repo_universe/scripts/query_impact.py --target <path-or-symbol>
```

If no query interface exists, fall back to manual dependency mapping:

1. file imports and direct callers
2. symbol references
3. route handlers and dependency wiring
4. tests with matching names or touched modules
5. ADRs and docs that mention the target path

Explicitly report lower confidence when using the manual fallback.

### 3. Restate the contract

Before editing, write down:

- the current contract
- the intended change
- non-goals
- likely fragile boundaries

### 4. Inspect impact

Use the query result to inspect:

- direct dependencies
- indirect dependencies
- backward prerequisites
- forward blast radius
- impacted tests
- impacted docs and ADRs
- invariants
- stale or low-confidence areas

### 5. Edit only after impact is understood

Do not edit a risky boundary until the query result has been acknowledged.

### 6. Verify against the impact surface

Verification must match the query result:

- reproduce the scenario or symptom
- run impacted tests or nearest equivalents
- verify the contract surface, not only the local code path
- explicitly state what was not verified

### 7. Escalate when confidence is too low

Stop and ask the user if:

- the dependency map is too incomplete
- multiple contract interpretations remain plausible
- the repo is already in conflicting flux
- required verification infrastructure is missing

## Required Output Shape

For risky edits, your reasoning must explicitly include:

- target
- current contract
- intended change
- blast radius
- impacted tests
- impacted docs or ADRs
- invariants
- verification plan
- missing confidence

## References

Read these as needed:

- [references/repo-universe-model.md](../../references/repo-universe-model.md)
- [references/dependency-heuristics.md](../../references/dependency-heuristics.md)
- [references/evaluation-rubric.md](../../references/evaluation-rubric.md)
- [references/platform-portability.md](../../references/platform-portability.md)
- [references/scenario-walkthroughs.md](../../references/scenario-walkthroughs.md)
