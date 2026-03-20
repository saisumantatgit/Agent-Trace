#!/usr/bin/env python3
"""Query the repo universe for the impact of changing a target.

Usage:
    python scripts/query_impact.py --target <path-or-symbol> [--change-type behavioral]
"""

import argparse
import json
import sys
from pathlib import Path

from common import (
    get_curated_dir,
    get_generated_dir,
    get_repo_root,
    load_json,
    load_yaml,
)


def load_universe(repo_root: Path) -> dict:
    """Load the full repo universe (generated + curated)."""
    gen_dir = get_generated_dir(repo_root)
    cur_dir = get_curated_dir(repo_root)

    universe = {
        "manifest": {},
        "nodes": [],
        "edges": [],
        "node_index": {},
        "invariants": [],
        "ownership": {},
        "sources_of_truth": [],
    }

    # Load generated
    manifest_path = gen_dir / "manifest.json"
    if manifest_path.exists():
        universe["manifest"] = load_json(manifest_path)

    nodes_path = gen_dir / "nodes.json"
    if nodes_path.exists():
        universe["nodes"] = load_json(nodes_path)
        universe["node_index"] = {n["id"]: n for n in universe["nodes"]}

    edges_path = gen_dir / "edges.json"
    if edges_path.exists():
        universe["edges"] = load_json(edges_path)

    # Load curated overlays
    inv_path = cur_dir / "invariants.yaml"
    if inv_path.exists():
        data = load_yaml(inv_path)
        universe["invariants"] = data.get("invariants", [])

    own_path = cur_dir / "ownership.yaml"
    if own_path.exists():
        universe["ownership"] = load_yaml(own_path)

    sot_path = cur_dir / "source_of_truth.yaml"
    if sot_path.exists():
        data = load_yaml(sot_path)
        universe["sources_of_truth"] = data.get("sources_of_truth", [])

    return universe


def find_target_node(universe: dict, target: str) -> dict | None:
    """Find a node matching the target string."""
    index = universe["node_index"]

    # Direct ID match
    if target in index:
        return index[target]

    # Path match
    for node_id, node in index.items():
        if node.get("path") == target:
            return node
        if node_id.endswith(f":{target}"):
            return node

    # Fuzzy: match by name
    for node in universe["nodes"]:
        if node.get("name") == target:
            return node
        if target in node.get("path", ""):
            return node

    return None


def find_direct_dependencies(universe: dict, target_id: str) -> list[str]:
    """Find nodes that the target directly depends on."""
    deps = []
    for edge in universe["edges"]:
        if edge["from"] == target_id and edge["type"] in ("imports", "depends_on", "calls"):
            deps.append(edge["to"])
    return deps


def find_indirect_dependencies(universe: dict, target_id: str, depth: int = 2) -> list[str]:
    """Find transitive dependencies up to a given depth."""
    visited = set()
    frontier = {target_id}

    for _ in range(depth):
        next_frontier = set()
        for node_id in frontier:
            for edge in universe["edges"]:
                if edge["from"] == node_id and edge["type"] in ("imports", "depends_on", "calls"):
                    if edge["to"] not in visited and edge["to"] != target_id:
                        next_frontier.add(edge["to"])
                        visited.add(edge["to"])
        frontier = next_frontier

    return list(visited)


def find_backward_prerequisites(universe: dict, target_id: str) -> list[str]:
    """Find things that must be true for the target to work (constrained_by, invariants)."""
    prereqs = []
    for edge in universe["edges"]:
        if edge["to"] == target_id and edge["type"] in ("constrained_by",):
            prereqs.append(edge["from"])

    # Check invariants
    for inv in universe["invariants"]:
        targets = inv.get("targets", [])
        if target_id in targets or any(target_id.endswith(t.split(":")[-1]) for t in targets):
            prereqs.append(f"invariant:{inv['id']}")

    return prereqs


def find_forward_blast_radius(universe: dict, target_id: str) -> list[str]:
    """Find things that will break if the target changes."""
    blast = []
    for edge in universe["edges"]:
        if edge["to"] == target_id and edge["type"] in ("imports", "depends_on", "calls"):
            blast.append(edge["from"])
    return blast


def find_impacted_tests(universe: dict, target_id: str) -> list[str]:
    """Find tests that exercise the target."""
    tests = []
    target_node = universe["node_index"].get(target_id)
    target_path = target_node.get("path", "") if target_node else ""

    for edge in universe["edges"]:
        if edge["to"] == target_id and edge["type"] == "tested_by":
            tests.append(edge["from"])
        elif edge["from"] == target_id and edge["type"] == "tested_by":
            tests.append(edge["to"])

    # Also find test nodes that reference the target's file
    for node in universe["nodes"]:
        if node["type"] == "test" and target_path and target_path in node.get("path", ""):
            if node["id"] not in tests:
                tests.append(node["id"])

    return tests


def find_impacted_docs(universe: dict, target_id: str) -> list[str]:
    """Find docs and ADRs that reference the target."""
    docs = []
    for edge in universe["edges"]:
        if edge["type"] == "documents":
            if edge["from"] == target_id or edge["to"] == target_id:
                other = edge["to"] if edge["from"] == target_id else edge["from"]
                docs.append(other)

    # Check ADR nodes whose content references the target path
    target_node = universe["node_index"].get(target_id)
    if target_node:
        target_path = target_node.get("path", "")
        if target_path:
            for node in universe["nodes"]:
                if node["type"] == "adr_doc" and node["id"] not in docs:
                    # Only include if the ADR's path overlaps with the target path
                    adr_path = node.get("path", "")
                    if target_path in adr_path or Path(target_path).stem in adr_path:
                        docs.append(node["id"])

    return docs


def find_invariants(universe: dict, target_id: str) -> list[str]:
    """Find invariants that constrain the target."""
    invariants = []
    target_node = universe["node_index"].get(target_id)
    target_path = target_node.get("path", "") if target_node else ""

    for inv in universe["invariants"]:
        targets = inv.get("targets", [])
        for t in targets:
            if t == target_id or (target_path and target_path in t):
                invariants.append(f"invariant:{inv['id']}")
                break
    return invariants


def find_source_of_truth(universe: dict, target_id: str) -> list[str]:
    """Find source-of-truth declarations relevant to the target."""
    sources = []
    target_node = universe["node_index"].get(target_id)
    target_path = target_node.get("path", "") if target_node else ""

    for sot in universe["sources_of_truth"]:
        refs = sot.get("references", [])
        for ref in refs:
            if ref == target_id or (target_path and target_path in ref):
                sources.append(sot.get("primary", "unknown"))
                break
    return list(set(sources))


def compute_verification_obligations(
    universe: dict, target_id: str, impacted_tests: list[str], invariants: list[str]
) -> list[str]:
    """Derive verification obligations from the impact analysis."""
    obligations = []

    if impacted_tests:
        obligations.append("Run impacted tests")

    for inv_ref in invariants:
        inv_id = inv_ref.replace("invariant:", "")
        for inv in universe["invariants"]:
            if inv["id"] == inv_id:
                for vo in inv.get("verification_obligations", []):
                    obligations.append(vo)

    if not obligations:
        obligations.append("Manual verification required — no automated tests mapped")

    return obligations


def compute_confidence(universe: dict, target_id: str, result: dict) -> float:
    """Compute overall confidence score."""
    scores = []

    target_node = universe["node_index"].get(target_id)
    if target_node:
        scores.append(target_node.get("confidence", 0.5))

    # Lower confidence if many unmapped areas
    if result.get("unmapped_or_low_confidence_areas"):
        scores.append(0.4)

    # Higher confidence if tests exist
    if result.get("impacted_tests"):
        scores.append(0.8)
    else:
        scores.append(0.3)

    return round(sum(scores) / len(scores), 2) if scores else 0.5


def find_stale_areas(universe: dict, target_id: str) -> list[str]:
    """Find stale or potentially outdated areas related to the target."""
    stale = []
    for doc_id in find_impacted_docs(universe, target_id):
        doc_node = universe["node_index"].get(doc_id)
        if doc_node and doc_node.get("confidence", 1.0) < 0.7:
            stale.append(f"{doc_id} (low confidence: {doc_node['confidence']})")
    return stale


def query_impact(universe: dict, target: str, change_type: str = "behavioral") -> dict:
    """Run a full impact query for the given target."""
    target_node = find_target_node(universe, target)

    if not target_node:
        return {
            "target": target,
            "current_contract": "Unknown — target not found in repo universe",
            "direct_dependencies": [],
            "indirect_dependencies": [],
            "backward_prerequisites": [],
            "forward_blast_radius": [],
            "impacted_tests": [],
            "impacted_docs_and_adrs": [],
            "invariants": [],
            "source_of_truth": [],
            "verification_obligations": ["Manual verification required — target not in universe"],
            "risk_summary": f"Target '{target}' not found in repo universe. Manual dependency mapping required.",
            "confidence": 0.2,
            "stale_areas": [],
            "unmapped_or_low_confidence_areas": [f"Target '{target}' is not mapped"],
        }

    target_id = target_node["id"]
    direct_deps = find_direct_dependencies(universe, target_id)
    indirect_deps = find_indirect_dependencies(universe, target_id)
    backward = find_backward_prerequisites(universe, target_id)
    blast = find_forward_blast_radius(universe, target_id)
    tests = find_impacted_tests(universe, target_id)
    docs = find_impacted_docs(universe, target_id)
    invariants = find_invariants(universe, target_id)
    sot = find_source_of_truth(universe, target_id)
    stale = find_stale_areas(universe, target_id)

    verification = compute_verification_obligations(universe, target_id, tests, invariants)

    # Identify unmapped areas
    unmapped = []
    if not tests:
        unmapped.append("No tests mapped for this target")
    if not docs:
        unmapped.append("No documentation mapped for this target")

    result = {
        "target": target_id,
        "current_contract": f"See {target_node['path']} — contract must be restated before editing",
        "direct_dependencies": direct_deps,
        "indirect_dependencies": indirect_deps,
        "backward_prerequisites": backward,
        "forward_blast_radius": blast,
        "impacted_tests": tests,
        "impacted_docs_and_adrs": docs,
        "invariants": invariants,
        "source_of_truth": sot if sot else ["code"],
        "verification_obligations": verification,
        "risk_summary": "",
        "confidence": 0.0,
        "stale_areas": stale,
        "unmapped_or_low_confidence_areas": unmapped,
    }

    result["confidence"] = compute_confidence(universe, target_id, result)

    # Generate risk summary
    risk_parts = []
    if blast:
        risk_parts.append(f"{len(blast)} items in blast radius")
    if invariants:
        risk_parts.append(f"{len(invariants)} invariants constrain this target")
    if not tests:
        risk_parts.append("no tests mapped")
    if stale:
        risk_parts.append(f"{len(stale)} stale areas")
    result["risk_summary"] = ". ".join(risk_parts) if risk_parts else "Low risk — minimal dependencies found"

    return result


def main():
    parser = argparse.ArgumentParser(description="Query repo universe for impact analysis")
    parser.add_argument("--target", required=True, help="Target path, symbol, or endpoint")
    parser.add_argument("--change-type", default="behavioral",
                        choices=["behavioral", "schema", "doc", "test"],
                        help="Type of change")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    args = parser.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else get_repo_root()
    if not repo_root.exists():
        print(f"Error: Repository root does not exist: {repo_root}", file=sys.stderr)
        sys.exit(1)
    universe = load_universe(repo_root)

    if not universe["nodes"]:
        print("Error: No repo universe found. Run build_manifest.py first.", file=sys.stderr)
        sys.exit(1)

    result = query_impact(universe, args.target, args.change_type)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
