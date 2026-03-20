#!/usr/bin/env python3
"""Validate that query_impact.py output conforms to the query contract schema.

Usage:
    python scripts/query_impact.py --target <target> | python scripts/check_query_schema.py
    python scripts/check_query_schema.py --file output.json
"""

import argparse
import json
import sys


REQUIRED_FIELDS = {
    "target": str,
    "current_contract": str,
    "direct_dependencies": list,
    "indirect_dependencies": list,
    "backward_prerequisites": list,
    "forward_blast_radius": list,
    "impacted_tests": list,
    "impacted_docs_and_adrs": list,
    "invariants": list,
    "source_of_truth": list,
    "verification_obligations": list,
    "risk_summary": str,
    "confidence": (int, float),
    "stale_areas": list,
    "unmapped_or_low_confidence_areas": list,
}


def check_schema(data: dict) -> list[str]:
    """Check that the query output matches the required schema."""
    errors = []

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in data:
            errors.append(f"Missing required field: {field}")
            continue

        value = data[field]
        if isinstance(expected_type, tuple):
            if not isinstance(value, expected_type):
                errors.append(f"Field '{field}' must be one of {expected_type}, got {type(value).__name__}")
        elif not isinstance(value, expected_type):
            errors.append(f"Field '{field}' must be {expected_type.__name__}, got {type(value).__name__}")

    # Validate confidence range
    if "confidence" in data:
        conf = data["confidence"]
        if isinstance(conf, (int, float)) and (conf < 0.0 or conf > 1.0):
            errors.append(f"Confidence must be 0.0-1.0, got {conf}")

    # Validate list items are strings
    for field in REQUIRED_FIELDS:
        if field in data and isinstance(data[field], list):
            for i, item in enumerate(data[field]):
                if not isinstance(item, str):
                    errors.append(f"Field '{field}[{i}]' must be a string, got {type(item).__name__}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Check query output schema")
    parser.add_argument("--file", type=str, help="JSON file to validate (default: stdin)")
    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file) as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        data = json.load(sys.stdin)

    errors = check_schema(data)

    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASS — query output conforms to schema")
        sys.exit(0)


if __name__ == "__main__":
    main()
