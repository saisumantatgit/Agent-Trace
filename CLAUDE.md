# Agent-Shield

Agent-Shield is a Claude Code plugin that provides dependency-aware remediation. Before an agent edits risky code, it maps the blast radius using a hybrid graph + curated contracts model.

## Architecture

Three layers:

1. **Repo Universe** — Machine-generated graph (files, symbols, imports, routes, tests) + human-curated overlays (invariants, ownership, source-of-truth)
2. **Agent Query** — Script interface that traverses the graph to return blast radius, impacted tests, invariants, and confidence before edits
3. **Safe Remediation Skill** — 7-step workflow that mandates querying before risky edits

## Commands

| Command | What It Does |
|---------|-------------|
| `/shield` | Full safe-remediation workflow |
| `/map` | Build/update the repo universe |
| `/query` | Query impact of changing a target |
| `/validate-universe` | Validate repo universe integrity |

## Agents

| Agent | Role |
|-------|------|
| `impact-analyzer` | Analyzes blast radius from query results |
| `contract-mapper` | Maps current contracts before edits |
| `manifest-builder` | Guides manifest building |

## Scripts (Python)

| Script | Purpose |
|--------|---------|
| `build_manifest.py` | Scan codebase, generate nodes + edges |
| `query_impact.py` | Query blast radius for a target |
| `validate_universe.py` | Validate manifest integrity |
| `check_query_schema.py` | Validate query output schema |
| `common.py` | Shared utilities |

## Key Design Decisions

- **Hybrid model**: machine-generated graph + human-curated overlays — avoids stale inventories and semantics-blind code graphs
- **Agent query is mandatory** before risky edits — the skill enforces this
- **Freshness and confidence** metadata on every node and edge — agents can assess certainty
- **File-based JSON** storage (not graph DB) — simple, inspectable, CI-friendly
- **Generated and curated facts always distinguishable** via `source` field — prevents false certainty

## Single Source of Truth

- `prompts/` — LLM-agnostic core prompts (all adapters wrap these)
- `scripts/` — Python tooling (copied into target repos by install.sh)
- `templates/` — Example curated overlays
- `references/` — Skill reference docs
- `docs/specs/` — Locked schema and contract specifications
