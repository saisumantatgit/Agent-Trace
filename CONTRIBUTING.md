# Contributing to Agent-Trace

## Adding Language Support

The `build_manifest.py` script extracts symbols and imports. To add a new language:

1. Add the file extension to `LANGUAGE_EXTENSIONS` in `scripts/common.py`
2. Create `extract_<language>_symbols()` in `build_manifest.py`
3. Create `extract_<language>_imports()` in `build_manifest.py`
4. Add endpoint detection patterns for the language's frameworks

## Adding a CLI Adapter

1. Create a directory in `adapters/<your-cli>/`
2. Wrap the prompts from `prompts/` in your CLI's native format
3. Update `install.sh` to detect and install your adapter

## Adding Invariants

1. Edit `repo_universe/curated/invariants.yaml`
2. Every invariant must have:
   - At least one target (must resolve to a real node)
   - At least one verification obligation
   - Confidence, owner, and subsystem metadata
3. Run `/validate-universe` to check resolution

## Modifying Curated Overlays

- `invariants.yaml` — must-not-break contracts
- `ownership.yaml` — team ownership declarations
- `source_of_truth.yaml` — what wins when artifacts diverge

All target references must resolve to real nodes in `repo_universe/generated/nodes.json`.

## Extending the Query Contract

The query output schema is locked in `docs/specs/query-contract.md`. Adding fields:

1. Add the field to the spec
2. Update `query_impact.py` to populate it
3. Update `check_query_schema.py` to validate it
4. Update the skill and prompts to use it

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes following the conventions above
4. Commit with a descriptive message (`git commit -m "Add: description of change"`)
5. Push to your fork (`git push origin feature/your-feature`)
6. Open a Pull Request against `main`

Pull requests should include:
- Description of what changed and why
- Any testing you performed
- Reference to related issues (if applicable)
