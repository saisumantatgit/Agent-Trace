#!/usr/bin/env python3
"""Validate the integrity of the repo universe.

Usage:
    python scripts/validate_universe.py [--repo-root PATH]
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from common import (
    VALID_EDGE_TYPES,
    VALID_NODE_TYPES,
    get_curated_dir,
    get_generated_dir,
    get_repo_root,
    load_json,
    load_yaml,
)


class ValidationResult:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str):
        self.errors.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        lines = []
        if self.passed:
            lines.append("PASS")
        else:
            lines.append("FAIL")

        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for e in self.errors:
                lines.append(f"  - {e}")

        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for w in self.warnings:
                lines.append(f"  - {w}")

        return "\n".join(lines)


def validate_manifest(gen_dir: Path, result: ValidationResult):
    """Validate manifest.json."""
    manifest_path = gen_dir / "manifest.json"
    if not manifest_path.exists():
        result.error("manifest.json not found")
        return

    manifest = load_json(manifest_path)
    for field in ("version", "repo_root", "generated_at", "generator"):
        if field not in manifest:
            result.error(f"manifest.json missing field: {field}")


def validate_nodes(gen_dir: Path, result: ValidationResult) -> dict:
    """Validate nodes.json. Returns node index."""
    nodes_path = gen_dir / "nodes.json"
    if not nodes_path.exists():
        result.error("nodes.json not found")
        return {}

    nodes = load_json(nodes_path)
    if not isinstance(nodes, list):
        result.error("nodes.json must be an array")
        return {}

    node_index = {}
    required_fields = {"id", "type", "source", "freshness", "confidence"}

    for i, node in enumerate(nodes):
        node_id = node.get("id", f"<node at index {i}>")

        # Check required fields
        for field in required_fields:
            if field not in node:
                result.error(f"Node {node_id} missing field: {field}")

        # Validate type
        if node.get("type") not in VALID_NODE_TYPES:
            result.error(f"Node {node_id} has invalid type: {node.get('type')}")

        # Validate confidence
        conf = node.get("confidence")
        if conf is not None:
            if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
                result.error(f"Node {node_id} confidence must be 0.0-1.0, got {conf}")

        # Check freshness
        freshness = node.get("freshness")
        if freshness:
            try:
                dt = datetime.fromisoformat(freshness.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - dt).days
                if age_days > 30:
                    result.warn(f"Node {node_id} is {age_days} days old")
            except ValueError:
                result.error(f"Node {node_id} has invalid freshness: {freshness}")

        # Check for duplicate IDs
        if node_id in node_index:
            result.error(f"Duplicate node ID: {node_id}")
        node_index[node_id] = node

    return node_index


def validate_edges(gen_dir: Path, node_index: dict, result: ValidationResult):
    """Validate edges.json."""
    edges_path = gen_dir / "edges.json"
    if not edges_path.exists():
        result.error("edges.json not found")
        return

    edges = load_json(edges_path)
    if not isinstance(edges, list):
        result.error("edges.json must be an array")
        return

    required_fields = {"from", "to", "type", "source", "freshness", "confidence"}

    for i, edge in enumerate(edges):
        edge_label = f"edge[{i}] ({edge.get('from', '?')} -> {edge.get('to', '?')})"

        # Check required fields
        for field in required_fields:
            if field not in edge:
                result.error(f"{edge_label} missing field: {field}")

        # Validate type
        if edge.get("type") not in VALID_EDGE_TYPES:
            result.error(f"{edge_label} has invalid type: {edge.get('type')}")

        # Validate references resolve
        if edge.get("from") and edge["from"] not in node_index:
            result.error(f"{edge_label}: 'from' reference does not resolve: {edge['from']}")
        if edge.get("to") and edge["to"] not in node_index:
            result.error(f"{edge_label}: 'to' reference does not resolve: {edge['to']}")

        # Validate confidence
        conf = edge.get("confidence")
        if conf is not None:
            if not isinstance(conf, (int, float)) or conf < 0.0 or conf > 1.0:
                result.error(f"{edge_label} confidence must be 0.0-1.0, got {conf}")


def validate_overlays(cur_dir: Path, node_index: dict, result: ValidationResult):
    """Validate curated overlay files."""
    # Invariants
    inv_path = cur_dir / "invariants.yaml"
    if inv_path.exists():
        data = load_yaml(inv_path)
        for inv in data.get("invariants", []):
            inv_id = inv.get("id", "<unnamed>")

            # Check targets resolve
            for target in inv.get("targets", []):
                if target not in node_index:
                    result.warn(f"Invariant '{inv_id}' target does not resolve: {target}")

            # Check verification obligations exist
            if not inv.get("verification_obligations"):
                result.error(f"Invariant '{inv_id}' has no verification obligations")

            # Check tests reference
            tests = inv.get("tests", [])
            for test_ref in tests:
                if test_ref not in node_index:
                    result.warn(f"Invariant '{inv_id}' test reference does not resolve: {test_ref}")

    # Ownership
    own_path = cur_dir / "ownership.yaml"
    if own_path.exists():
        data = load_yaml(own_path)
        for target in data.get("owners", {}).get("targets", []):
            target_id = target.get("id", "")
            if target_id and target_id not in node_index:
                result.warn(f"Ownership target does not resolve: {target_id}")

    # Source of truth
    sot_path = cur_dir / "source_of_truth.yaml"
    if sot_path.exists():
        data = load_yaml(sot_path)
        for sot in data.get("sources_of_truth", []):
            topic = sot.get("topic", "<unnamed>")
            if not sot.get("primary"):
                result.error(f"Source of truth '{topic}' has no primary source")
            for ref in sot.get("references", []):
                if ref not in node_index:
                    result.warn(f"Source of truth '{topic}' reference does not resolve: {ref}")


def main():
    parser = argparse.ArgumentParser(description="Validate repo universe integrity")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    args = parser.parse_args()

    repo_root = args.repo_root or get_repo_root()
    gen_dir = get_generated_dir(repo_root)
    cur_dir = get_curated_dir(repo_root)

    result = ValidationResult()

    if not gen_dir.exists():
        result.error(f"Generated directory not found: {gen_dir}")
        print(result.summary())
        sys.exit(1)

    validate_manifest(gen_dir, result)
    node_index = validate_nodes(gen_dir, result)
    validate_edges(gen_dir, node_index, result)

    if cur_dir.exists():
        validate_overlays(cur_dir, node_index, result)
    else:
        result.warn("No curated overlays directory found")

    print(result.summary())
    sys.exit(0 if result.passed else 1)


if __name__ == "__main__":
    main()
