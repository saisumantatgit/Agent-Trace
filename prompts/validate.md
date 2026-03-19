# Validate Repo Universe Prompt

You are validating the integrity of a repo universe.

## What to Check

### 1. Manifest Integrity
- `repo_universe/generated/manifest.json` exists and has valid metadata
- Version, repo_root, generated_at, and generator fields are present

### 2. Node Integrity
- Every node in `nodes.json` has: id, type, source, freshness, confidence
- Node types are valid: file, symbol, test, endpoint, adr_doc, invariant
- Confidence values are between 0.0 and 1.0
- Freshness values are valid ISO 8601 timestamps

### 3. Edge Integrity
- Every edge in `edges.json` has: from, to, type, source, freshness, confidence
- Every `from` and `to` reference resolves to a real node ID in `nodes.json`
- Edge types are valid: imports, defines, calls, tested_by, depends_on, documents, constrained_by

### 4. Curated Overlay Resolution
- Every target in `invariants.yaml` resolves to a real node
- Every target in `ownership.yaml` resolves to a real node or subsystem
- Every reference in `source_of_truth.yaml` resolves

### 5. Invariant Completeness
- Every invariant has at least one verification obligation
- Every invariant points to at least one real test or has an explicit gap note

### 6. Staleness
- Flag nodes or edges older than 30 days as potentially stale

## Output

Report PASS or FAIL with specific violations listed.
