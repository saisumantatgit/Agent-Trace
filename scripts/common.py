"""Common utilities for repo universe scripts."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def get_repo_root() -> Path:
    """Find the repo root by walking up from cwd looking for .git."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()


def get_universe_dir(repo_root: Path | None = None) -> Path:
    """Get the repo_universe directory path."""
    root = repo_root or get_repo_root()
    return root / "repo_universe"


def get_generated_dir(repo_root: Path | None = None) -> Path:
    """Get the generated output directory."""
    return get_universe_dir(repo_root) / "generated"


def get_curated_dir(repo_root: Path | None = None) -> Path:
    """Get the curated overlays directory."""
    return get_universe_dir(repo_root) / "curated"


def now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> Any:
    """Load a JSON file."""
    with open(path) as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    """Save data as formatted JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def load_yaml(path: Path) -> Any:
    """Load a YAML file. Returns empty dict if pyyaml not available."""
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        print(f"Warning: pyyaml not installed. Cannot load {path}")
        return {}


def make_node_id(node_type: str, path: str, name: str | None = None) -> str:
    """Create a stable node ID.

    Examples:
        make_node_id("file", "src/app/auth.py") -> "file:src/app/auth.py"
        make_node_id("symbol", "src/app/auth.py", "verify_token") -> "symbol:src/app/auth.py:verify_token"
    """
    if name:
        return f"{node_type}:{path}:{name}"
    return f"{node_type}:{path}"


def make_node(
    node_type: str,
    path: str,
    name: str,
    source: str = "parser",
    confidence: float = 0.8,
    owner: str = "unknown",
    subsystem: str = "unknown",
    criticality: str = "unknown",
    metadata: dict | None = None,
) -> dict:
    """Create a node object conforming to the manifest schema."""
    node_id = make_node_id(node_type, path, name if node_type != "file" else None)
    node = {
        "id": node_id,
        "type": node_type,
        "name": name,
        "path": path,
        "source": source,
        "freshness": now_iso(),
        "confidence": confidence,
        "owner": owner,
        "subsystem": subsystem,
        "criticality": criticality,
    }
    if metadata:
        node["metadata"] = metadata
    return node


def make_edge(
    from_id: str,
    to_id: str,
    edge_type: str,
    source: str = "parser",
    confidence: float = 0.8,
    owner: str = "unknown",
    subsystem: str = "unknown",
    criticality: str = "unknown",
    metadata: dict | None = None,
) -> dict:
    """Create an edge object conforming to the manifest schema."""
    edge = {
        "from": from_id,
        "to": to_id,
        "type": edge_type,
        "source": source,
        "freshness": now_iso(),
        "confidence": confidence,
        "owner": owner,
        "subsystem": subsystem,
        "criticality": criticality,
    }
    if metadata:
        edge["metadata"] = metadata
    return edge


# Valid types per the v1 schema
VALID_NODE_TYPES = {"file", "symbol", "test", "endpoint", "adr_doc", "invariant"}
VALID_EDGE_TYPES = {
    "imports", "defines", "calls", "tested_by",
    "depends_on", "documents", "constrained_by",
}

# Directories to skip during scanning
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "dist", "build", ".eggs", "*.egg-info",
    "repo_universe",
}

# File extensions to scan by language
LANGUAGE_EXTENSIONS = {
    "python": {".py"},
    "javascript": {".js", ".jsx", ".mjs"},
    "typescript": {".ts", ".tsx"},
    "go": {".go"},
    "rust": {".rs"},
    "java": {".java"},
    "ruby": {".rb"},
}
