---
name: map
description: Build the repo universe — scan codebase and generate dependency graph
---

Build the repo universe for this repository.

Read `prompts/map.md` for full instructions. Execute:

1. Run `python repo_universe/scripts/build_manifest.py` (or the scripts from Agent-Trace)
2. Review generated manifest for warnings
3. Guide user to create curated overlays from templates
4. Suggest running `/validate-universe` after generation
