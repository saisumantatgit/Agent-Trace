#!/usr/bin/env python3
"""Build the repo universe manifest — scan codebase and generate nodes + edges.

Usage:
    python scripts/build_manifest.py [--repo-root PATH] [--language LANG]
"""

import argparse
import ast
import os
import re
import sys
from pathlib import Path

from common import (
    LANGUAGE_EXTENSIONS,
    SKIP_DIRS,
    get_generated_dir,
    get_repo_root,
    make_edge,
    make_node,
    make_node_id,
    now_iso,
    save_json,
)


def should_skip(path: Path) -> bool:
    """Check if a path should be skipped during scanning."""
    parts = path.parts
    return any(part in SKIP_DIRS or part.endswith(".egg-info") for part in parts)


def discover_files(repo_root: Path, language: str | None = None) -> list[Path]:
    """Discover source files in the repository."""
    if language and language in LANGUAGE_EXTENSIONS:
        extensions = LANGUAGE_EXTENSIONS[language]
    else:
        extensions = set()
        for exts in LANGUAGE_EXTENSIONS.values():
            extensions.update(exts)

    files = []
    for root, dirs, filenames in os.walk(repo_root):
        root_path = Path(root)
        rel = root_path.relative_to(repo_root)
        if should_skip(rel):
            dirs.clear()
            continue
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.endswith(".egg-info")]
        for fname in filenames:
            if Path(fname).suffix in extensions:
                files.append(root_path / fname)
    return sorted(files)


def extract_python_symbols(file_path: Path) -> list[dict]:
    """Extract function and class definitions from a Python file."""
    symbols = []
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return symbols

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append({
                "name": node.name,
                "type": "function",
                "line": node.lineno,
            })
        elif isinstance(node, ast.ClassDef):
            symbols.append({
                "name": node.name,
                "type": "class",
                "line": node.lineno,
            })
    return symbols


def extract_python_imports(file_path: Path) -> list[str]:
    """Extract import targets from a Python file."""
    imports = []
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(file_path))
    except (SyntaxError, UnicodeDecodeError):
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def extract_js_ts_symbols(file_path: Path) -> list[dict]:
    """Extract function and class definitions from JS/TS files using regex."""
    symbols = []
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
    except UnicodeDecodeError:
        return symbols

    patterns = [
        (r"(?:export\s+)?(?:async\s+)?function\s+(\w+)", "function"),
        (r"(?:export\s+)?class\s+(\w+)", "class"),
        (r"(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(", "function"),
    ]
    for pattern, sym_type in patterns:
        for i, line in enumerate(source.splitlines(), 1):
            for match in re.finditer(pattern, line):
                symbols.append({
                    "name": match.group(1),
                    "type": sym_type,
                    "line": i,
                })
    return symbols


def detect_endpoints(file_path: Path, source: str) -> list[dict]:
    """Detect HTTP endpoints from framework patterns."""
    endpoints = []
    patterns = [
        # FastAPI / Flask decorators
        r'@\w+\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)',
        # Express-style (app, router, server, api, blueprint)
        r'(?:app|router|server|api|blueprint)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, source, re.IGNORECASE):
            method = match.group(1).upper()
            path = match.group(2)
            endpoints.append({"method": method, "path": path})
    return endpoints


def is_test_file(file_path: Path) -> bool:
    """Heuristic: is this a test file?"""
    name = file_path.name.lower()
    parts = [p.lower() for p in file_path.parts]
    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith(".test.ts")
        or name.endswith(".test.js")
        or name.endswith(".spec.ts")
        or name.endswith(".spec.js")
        or "tests" in parts
        or "test" in parts
        or "__tests__" in parts
    )


def is_adr_or_doc(file_path: Path) -> bool:
    """Heuristic: is this an ADR or architecture doc?"""
    name = file_path.name.lower()
    parts = [p.lower() for p in file_path.parts]
    return (
        name.startswith("adr")
        or "adr" in parts
        or "decisions" in parts
        or (name.endswith(".md") and any(k in parts for k in ("docs", "doc", "architecture")))
    )


def resolve_python_import_to_path(
    import_module: str, repo_root: Path, file_map: dict[str, str]
) -> str | None:
    """Try to resolve a Python import to a file path in the repo."""
    candidates = [
        import_module.replace(".", "/") + ".py",
        import_module.replace(".", "/") + "/__init__.py",
    ]
    for candidate in candidates:
        if candidate in file_map:
            return candidate
    # Try partial match (last segment)
    parts = import_module.split(".")
    for i in range(len(parts)):
        partial = "/".join(parts[i:]) + ".py"
        if partial in file_map:
            return partial
    return None


def build_manifest(repo_root: Path, language: str | None = None) -> dict:
    """Build the complete repo universe manifest."""
    nodes = []
    edges = []
    warnings = []
    node_ids = set()

    # Discover files
    files = discover_files(repo_root, language)
    if not files:
        warnings.append("No source files found")
        return {"nodes": nodes, "edges": edges, "warnings": warnings}

    # Build file map for import resolution
    file_map = {}
    for f in files:
        rel = str(f.relative_to(repo_root))
        file_map[rel] = rel

    # Process each file
    for file_path in files:
        rel_path = str(file_path.relative_to(repo_root))
        suffix = file_path.suffix

        # Determine node type
        if is_test_file(file_path):
            file_node_type = "test"
        elif is_adr_or_doc(file_path):
            file_node_type = "adr_doc"
        else:
            file_node_type = "file"

        # Create file node
        file_node = make_node(
            node_type=file_node_type,
            path=rel_path,
            name=file_path.name,
            source="parser",
            confidence=0.95,
        )
        if file_node["id"] not in node_ids:
            nodes.append(file_node)
            node_ids.add(file_node["id"])

        # Extract symbols
        symbols = []
        if suffix == ".py":
            symbols = extract_python_symbols(file_path)
        elif suffix in {".ts", ".tsx", ".js", ".jsx"}:
            symbols = extract_js_ts_symbols(file_path)

        for sym in symbols:
            sym_node = make_node(
                node_type="symbol",
                path=rel_path,
                name=sym["name"],
                source="parser",
                confidence=0.9,
                metadata={"language": suffix.lstrip("."), "line": sym["line"]},
            )
            if sym_node["id"] not in node_ids:
                nodes.append(sym_node)
                node_ids.add(sym_node["id"])

            # File defines symbol
            edges.append(make_edge(
                from_id=file_node["id"],
                to_id=sym_node["id"],
                edge_type="defines",
                confidence=0.95,
            ))

        # Extract imports (Python)
        if suffix == ".py":
            imports = extract_python_imports(file_path)
            for imp in imports:
                target_path = resolve_python_import_to_path(imp, repo_root, file_map)
                if target_path:
                    target_id = make_node_id("file", target_path)
                    if target_id in node_ids:
                        edges.append(make_edge(
                            from_id=file_node["id"],
                            to_id=target_id,
                            edge_type="imports",
                            confidence=0.85,
                        ))

        # Detect endpoints
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
            endpoints = detect_endpoints(file_path, source)
            for ep in endpoints:
                ep_id = f"endpoint:{ep['method']}:{ep['path']}"
                if ep_id not in node_ids:
                    ep_node = make_node(
                        node_type="endpoint",
                        path=rel_path,
                        name=f"{ep['method']} {ep['path']}",
                        source="heuristic",
                        confidence=0.75,
                    )
                    ep_node["id"] = ep_id
                    nodes.append(ep_node)
                    node_ids.add(ep_id)
        except Exception as e:
            warnings.append(f"Endpoint detection failed for {rel_path}: {e}")

        # Map test files to their targets
        if is_test_file(file_path):
            # Heuristic: test_foo.py tests foo.py
            test_name = file_path.stem
            for prefix in ("test_", ""):
                for suffix_str in ("_test", "_spec", ".test", ".spec"):
                    test_name = test_name.replace(suffix_str, "").replace(prefix, "", 1)

            # Find matching source files
            for other_path in file_map:
                other_stem = Path(other_path).stem
                if other_stem == test_name and not is_test_file(Path(other_path)):
                    target_id = make_node_id("file", other_path)
                    if target_id in node_ids:
                        edges.append(make_edge(
                            from_id=make_node_id("test", rel_path),
                            to_id=target_id,
                            edge_type="tested_by",
                            source="heuristic",
                            confidence=0.6,
                        ))

    return {"nodes": nodes, "edges": edges, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description="Build repo universe manifest")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--language", help="Primary language to scan")
    args = parser.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else get_repo_root()
    if not repo_root.exists():
        print(f"Error: Repository root does not exist: {repo_root}", file=sys.stderr)
        sys.exit(1)
    print(f"Scanning: {repo_root}")

    result = build_manifest(repo_root, args.language)
    output_dir = get_generated_dir(repo_root)

    # Write manifest
    manifest = {
        "version": "v1",
        "repo_root": str(repo_root),
        "generated_at": now_iso(),
        "generator": "repo_universe/scripts/build_manifest.py",
        "warnings": result["warnings"],
    }
    save_json(output_dir / "manifest.json", manifest)

    # Write nodes and edges
    save_json(output_dir / "nodes.json", result["nodes"])
    save_json(output_dir / "edges.json", result["edges"])

    print(f"Generated: {len(result['nodes'])} nodes, {len(result['edges'])} edges")
    if result["warnings"]:
        for w in result["warnings"]:
            print(f"Warning: {w}")
    print(f"Output: {output_dir}")


if __name__ == "__main__":
    main()
