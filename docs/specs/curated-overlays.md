# Curated Overlays v1

Human-maintained overlay files layered on top of generated structure.

## File List

- `invariants.yaml`
- `ownership.yaml`
- `source_of_truth.yaml`

## `invariants.yaml`

Purpose: capture must-not-break contracts, attach verification obligations, point to real code, tests, and docs.

Shape:

```yaml
invariants:
  - id: "respect-injected-dependency"
    name: "Respect injected dependencies"
    description: "Factory-created dependencies must not be replaced implicitly"
    targets:
      - "symbol:src/app/factory.py:create_app"
      - "symbol:src/app/deps.py:get_data_store"
    docs:
      - "adr_doc:docs/decisions/ADR-001-dependency-injection.md"
    tests:
      - "test:tests/test_factory.py::test_injected_store_is_respected"
    verification_obligations:
      - "Run factory integration tests"
      - "Confirm injected dependencies are preserved"
    owner: "platform"
    subsystem: "core"
    criticality: "high"
    source: "manual"
    freshness: "2026-03-19T00:00:00Z"
    confidence: 1.0
```

Rules:

- every target, doc, and test reference must resolve
- every invariant must have at least one verification obligation
- every invariant used by the skill must point to at least one real test or an explicit gap note

## `ownership.yaml`

Purpose: define owners for subsystems, files, or specific symbols when generated metadata is insufficient.

Shape:

```yaml
owners:
  subsystems:
    api:
      owner: "api-team"
      criticality: "high"
  targets:
    - id: "file:src/app/deps.py"
      owner: "platform"
```

Rules:

- subsystem-level ownership is the default
- target-level ownership overrides subsystem defaults
- missing owners are allowed in v1 but should be reported by validation

## `source_of_truth.yaml`

Purpose: declare which artifacts should win when code, docs, and planning materials diverge.

Shape:

```yaml
sources_of_truth:
  - topic: "current-runtime-behavior"
    primary: "code"
    references:
      - "file:src/app/deps.py"
      - "test:tests/test_factory.py::test_injected_store_is_respected"
    notes: "Code and tests beat ADR text for current behavior"
```

Rules:

- every topic must declare one primary source class
- references must resolve
- if validation finds conflict between a declared source of truth and observed reality, the conflict must appear in query output
