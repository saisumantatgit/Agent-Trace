# Agent-Shield

> **Shield your code.**
> Dependency-aware remediation for AI agent workflows — map blast radius before you edit, not after you break.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Commands](https://img.shields.io/badge/Commands-4-orange.svg)](#commands)
[![Platforms](https://img.shields.io/badge/Platforms-5-purple.svg)](#platform-support)

---

## The Problem

You've seen it happen: an agent fixes one file and silently breaks three others. The local code looks correct — but the injected dependency is gone, the contract test fails, and the ADR now contradicts reality.

Agents don't fail because they can't write code. They fail because **they can't see the blast radius.**

Agent-Shield fixes that. Before any risky edit, it maps dependencies, surfaces invariants, and forces the agent to acknowledge what could break — then ties verification to the impacted surface, not just the local code path.

---

## How It Works

```
Change Request
    ↓
1. Identify target (file, symbol, route, contract)
    ↓
2. Query repo universe → blast radius, tests, invariants, confidence
    ↓
3. Restate contract → current behavior, intended change, non-goals
    ↓
4. Inspect impact → dependencies, backward prereqs, forward blast
    ↓
5. Edit only after impact acknowledged
    ↓
6. Verify against impact surface → run tests, check contracts, state gaps
    ↓
7. Escalate if confidence too low → stop and ask
```

---

## The Repo Universe

A hybrid model — generated structure + curated contracts:

| Layer | Source | What It Captures |
|-------|--------|-----------------|
| **Generated** | Machine (parsers, heuristics) | Files, symbols, imports, routes, tests, call/define edges |
| **Curated** | Human (maintainers) | Invariants, ownership, source-of-truth, criticality |

Generated facts and curated facts are **always distinguishable** via the `source` field. An agent can tell whether an edge is parser-derived or manually asserted — no false certainty.

```
repo_universe/
├── generated/          ← Machine-built (build_manifest.py)
│   ├── manifest.json
│   ├── nodes.json
│   └── edges.json
└── curated/            ← Human-maintained
    ├── invariants.yaml
    ├── ownership.yaml
    └── source_of_truth.yaml
```

---

## Commands

| Command | When | What It Does |
|---------|------|-------------|
| **`/shield`** | Before risky edits | Full 7-step safe remediation workflow |
| **`/map`** | Setup + periodic refresh | Build/update the repo universe |
| **`/query <target>`** | Before editing a specific target | Query blast radius, tests, invariants |
| **`/validate-universe`** | After changes to universe | Check integrity of nodes, edges, overlays |

### Example

```bash
/shield Fix the auth middleware to reject expired tokens — currently it silently passes them through
```

Output: target, current contract, blast radius, impacted tests, invariants, verification plan, confidence score.

---

## Installation

```bash
# Clone
git clone https://github.com/saisumantatgit/Agent-Shield.git

# Install into your project (auto-detects your CLI)
cd your-project/
bash /path/to/Agent-Shield/install.sh
```

Or for Claude Code, install as a plugin:

```bash
cp -r Agent-Shield/ ~/.claude/plugins/agent-shield/
```

### What Gets Installed

| CLI Tool | What Gets Installed |
|----------|-------------------|
| **Claude Code** | `.claude/commands/*.md` + agents + skill + hook |
| **Codex** | Appends to `AGENTS.md` |
| **Cursor** | `.cursor/rules/shield.md` |
| **Aider** | Appends to `.aider.conf.yml` |
| **Generic** | Raw prompt files |

Plus: `repo_universe/scripts/` (Python), curated overlay templates, and prompts.

---

## Quick Start

```bash
# 1. Install
bash /path/to/Agent-Shield/install.sh

# 2. Build the repo universe
/map

# 3. Customize your invariants
# Edit repo_universe/curated/invariants.yaml

# 4. Validate
/validate-universe

# 5. Use before risky edits
/shield "Fix the payment processing retry logic"
```

---

## Scripts

Python tooling for building and querying the repo universe:

| Script | Purpose |
|--------|---------|
| `build_manifest.py` | Scan codebase, generate nodes + edges |
| `query_impact.py` | Query blast radius for a target |
| `validate_universe.py` | Validate manifest integrity |
| `check_query_schema.py` | Validate query output schema |

Requirements: Python 3.9+. Optional: `pyyaml` for curated overlay support.

---

## Manual Fallback

No repo universe? No problem. The skill degrades gracefully:

1. File imports and direct callers
2. Symbol references
3. Route handlers and dependency wiring
4. Tests with matching names or touched modules
5. ADRs and docs that mention the target

Confidence is reported as lower when using manual fallback.

---

## Platform Support

| Platform | Config | Notes |
|----------|--------|-------|
| Claude Code | `.claude-plugin/plugin.json` | Full support (agents + commands + skill) |
| Codex | `AGENTS.md` | Prompt-based |
| Cursor | `.cursor/rules/shield.md` | Rules-based |
| Aider | `.aider.conf.yml` | Config-based |
| Generic | `prompts/*.md` | Paste into any LLM |

---

## Architecture Decisions

- **Hybrid graph model**: Machine-generated structure + human-curated overlays — best of both worlds
- **File-based JSON storage**: Simple, inspectable, CI-friendly (no graph DB for v1)
- **Mandatory agent query**: The skill enforces querying before risky edits
- **Confidence and freshness on every fact**: Agents can assess certainty and staleness
- **Generated vs curated always distinguishable**: The `source` field prevents false certainty

---

## Part of the Agent Suite

| Tool | What It Does | Tagline |
|------|-------------|---------|
| [**Agent-PROVE**](https://github.com/saisumantatgit/Agent-PROVE) | Makes agents think before they act | "Prove it or it fails." |
| [**Agent-Scribe**](https://github.com/saisumantatgit/Agent-Scribe) | Makes agents remember what they learned | "Nothing is lost." |
| **Agent-Shield** | Makes agents see before they edit | "Shield your code." |

PROVE validates your thinking. Scribe records your learning. **Shield maps your blast radius.** Together: think rigorously, remember everything, edit safely.

---

## Origin

Extracted from the repo-universe research — an investigation into how AI agents can safely remediate code in production-leaning repositories without silently breaking adjacent contracts. The hybrid model (generated graph + curated overlays) emerged as the right balance between machine precision and human intent.

The methodology is domain-agnostic. The tooling works on any codebase.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Adding language support
- Adding CLI adapters
- Extending the query contract
- Modifying curated overlays

---

## License

[MIT](LICENSE)
