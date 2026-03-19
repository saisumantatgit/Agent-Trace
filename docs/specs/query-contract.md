# Agent Query Contract v1

## Interface Name

Use the term `agent query`.

The first implementation is a script interface:

```text
python repo_universe/scripts/query_impact.py --target <path-or-symbol>
```

## Inputs

Required:

- `--target`
  - a repo path
  - a symbol id
  - an endpoint id

Optional:

- `--change-type`
  - `behavioral`
  - `schema`
  - `doc`
  - `test`

## Required Output Fields

- `target`
- `current_contract`
- `direct_dependencies`
- `indirect_dependencies`
- `backward_prerequisites`
- `forward_blast_radius`
- `impacted_tests`
- `impacted_docs_and_adrs`
- `invariants`
- `source_of_truth`
- `verification_obligations`
- `risk_summary`
- `confidence`
- `stale_areas`
- `unmapped_or_low_confidence_areas`

## Output Shape

```json
{
  "target": "symbol:src/app/deps.py:get_data_store",
  "current_contract": "Returns injected store unless explicit mode is enabled",
  "direct_dependencies": [
    "symbol:src/app/factory.py:create_app"
  ],
  "indirect_dependencies": [
    "file:src/app/routes.py"
  ],
  "backward_prerequisites": [
    "invariant:respect-injected-dependency"
  ],
  "forward_blast_radius": [
    "symbol:src/app/routes.py:get_status"
  ],
  "impacted_tests": [
    "test:tests/test_factory.py::test_injected_store_is_respected"
  ],
  "impacted_docs_and_adrs": [
    "adr_doc:docs/decisions/ADR-001-dependency-injection.md"
  ],
  "invariants": [
    "invariant:respect-injected-dependency"
  ],
  "source_of_truth": [
    "code",
    "tests"
  ],
  "verification_obligations": [
    "Run factory integration tests",
    "Confirm injected dependencies are preserved"
  ],
  "risk_summary": "Factory contract is broader than concrete store type. A local fix can break generic dependency injection.",
  "confidence": 0.91,
  "stale_areas": [
    "ADR wording may lag current behavior"
  ],
  "unmapped_or_low_confidence_areas": []
}
```

## Behavioral Rules

- the query must prefer precise node ids when available
- the query must include low-confidence gaps rather than hiding them
- empty arrays are acceptable when the map truly contains no evidence
- the output must stay machine-readable and must not require free-form prose parsing

## Skill Integration Rules

- the skill determines when the query is mandatory
- the query determines what the likely impact surface is
- the agent must acknowledge query results before risky edits
