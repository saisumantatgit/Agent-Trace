# Dependency Heuristics

Use these heuristics when deriving a target or checking impact:

- if the change is in an app factory, inspect dependency injection and runtime mode switches
- if the change is in persistence, inspect route handlers, report builders, and contract tests
- if the change is in mapping or enrichment, inspect downstream rules and reports
- if the change is in ADR-governed code, inspect stale-doc risk and source-of-truth markers
- if the change touches an invariant target, treat the query as mandatory

Manual fallback order when no query interface exists:

1. file imports and direct callers
2. symbol references
3. route handlers and dependency wiring
4. tests with matching names or touched modules
5. ADRs and research docs that mention the target path
