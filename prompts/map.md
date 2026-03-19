# Build Repo Universe Prompt

You are building a dependency map (repo universe) for this repository.

## What to Generate

Scan the codebase and produce three files in `repo_universe/generated/`:

### manifest.json
```json
{
  "version": "v1",
  "repo_root": ".",
  "generated_at": "<ISO 8601 UTC>",
  "generator": "repo_universe/scripts/build_manifest.py",
  "warnings": []
}
```

### nodes.json
Array of node objects. Each node has:
- `id` — unique identifier (e.g., `file:src/app/auth.py`, `symbol:src/app/auth.py:verify_token`)
- `type` — one of: file, symbol, test, endpoint, adr_doc, invariant
- `name` — human-readable name
- `path` — file path relative to repo root
- `source` — how it was discovered (parser, heuristic, manual)
- `freshness` — ISO 8601 UTC timestamp
- `confidence` — 0.0 to 1.0
- `owner` — team or person (use "unknown" if not determinable)
- `subsystem` — architecture grouping (use "unknown" if not determinable)
- `criticality` — high, medium, low, or unknown

### edges.json
Array of edge objects. Each edge has:
- `from` — source node ID (must resolve to a real node)
- `to` — target node ID (must resolve to a real node)
- `type` — one of: imports, defines, calls, tested_by, depends_on, documents, constrained_by
- `source`, `freshness`, `confidence`, `owner`, `subsystem`, `criticality`

## After Generation

1. Review warnings in manifest.json
2. Create curated overlays in `repo_universe/curated/` for invariants, ownership, and source-of-truth
3. Run validation to check integrity
