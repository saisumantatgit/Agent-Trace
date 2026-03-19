---
name: map
description: Build or update the repo universe — generates manifest, nodes, and edges from the codebase. Run this before using /query or /shield.
---

# /map — Build Repo Universe

Generate the dependency map for this repository.

## What It Does

1. Scans the codebase for files, symbols, imports, routes, tests, and docs
2. Generates `repo_universe/generated/manifest.json`, `nodes.json`, `edges.json`
3. Reports coverage: what was mapped, what was missed, confidence levels

## Prerequisites

- Python 3.9+
- The repo must be at its root (where `repo_universe/` will be created)

## Usage

```
/map
```

Or with options:

```
/map --language python    # Scope to Python files
/map --include-tests      # Include test discovery
```

## Output

- `repo_universe/generated/manifest.json` — metadata about the generation run
- `repo_universe/generated/nodes.json` — all discovered nodes (files, symbols, tests, endpoints)
- `repo_universe/generated/edges.json` — all discovered relationships

## After Mapping

1. Review the generated manifest for warnings
2. Create curated overlays in `repo_universe/curated/` (use templates from `templates/`)
3. Run `/validate-universe` to check integrity
4. Use `/query` or `/shield` to query impact before edits
