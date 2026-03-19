# Manifest Schema v1

## Storage Layout

```text
repo_universe/
├── generated/
│   ├── manifest.json
│   ├── nodes.json
│   └── edges.json
└── curated/
    ├── invariants.yaml
    ├── ownership.yaml
    └── source_of_truth.yaml
```

## Manifest Metadata

`manifest.json` contains:

```json
{
  "version": "v1",
  "repo_root": ".",
  "generated_at": "2026-03-19T12:00:00Z",
  "generator": "repo_universe/scripts/build_manifest.py",
  "warnings": []
}
```

## v1 Node Types

- `file`
- `symbol`
- `test`
- `endpoint`
- `adr_doc`
- `invariant`

## v1 Edge Types

- `imports`
- `defines`
- `calls`
- `tested_by`
- `depends_on`
- `documents`
- `constrained_by`

## Required Metadata on Every Node and Edge

- `source` — where the fact came from (parser, heuristic, manual)
- `freshness` — ISO 8601 UTC timestamp
- `confidence` — numeric, 0.0 to 1.0
- `owner` — team or person (use "unknown" if not determinable)
- `subsystem` — architecture grouping (use "unknown" if not determinable)
- `criticality` — high, medium, low, or unknown

## Node Shape

```json
{
  "id": "symbol:src/app/deps.py:get_data_store",
  "type": "symbol",
  "name": "get_data_store",
  "path": "src/app/deps.py",
  "source": "parser",
  "freshness": "2026-03-19T12:00:00Z",
  "confidence": 0.93,
  "owner": "platform",
  "subsystem": "core",
  "criticality": "high",
  "metadata": {
    "language": "python",
    "line": 12
  }
}
```

## Edge Shape

```json
{
  "from": "symbol:src/app/routes.py:get_status",
  "to": "symbol:src/app/deps.py:get_data_store",
  "type": "depends_on",
  "source": "parser",
  "freshness": "2026-03-19T12:00:00Z",
  "confidence": 0.87,
  "owner": "platform",
  "subsystem": "core",
  "criticality": "high",
  "metadata": {
    "reason": "dependency injection"
  }
}
```

## Generation Rules

- Generated facts and curated facts must stay distinguishable
- Unknown `owner`, `subsystem`, or `criticality` values may be set to `unknown`
- `confidence` must be numeric and between `0.0` and `1.0`
- `freshness` must be ISO 8601 UTC timestamps
- Every `from` and `to` reference in `edges.json` must resolve to a real node id

## Deferred v1 Entities

Not generated in first build, but reserved in design:

- Nodes: `data_store`, `schema_artifact`, `external_dependency`, `service`, `dataset`
- Edges: `reads`, `writes`, `implements`, `owned_by`, `served_by`, `cross_repo_depends_on`
