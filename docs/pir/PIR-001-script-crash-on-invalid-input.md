# PIR-001: Python Scripts Crash on Invalid Input

## Metadata

| Field | Value |
|-------|-------|
| **PIR ID** | PIR-001 |
| **Date** | 2026-03-20 |
| **Severity** | P2 |
| **Status** | Final |
| **Incident date** | 2026-03-18 |
| **Detection date** | 2026-03-19 |
| **Resolution date** | 2026-03-20 |

## Zone Check

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Severity** | P2 | Scripts functional on valid input; crash on edge cases |
| **Containment** | Contained | All five scripts audited and patched |
| **Blast Radius** | 3 of 5 scripts in `scripts/` | build_manifest.py, check_query_schema.py, query_impact.py |

## 1. Summary

Three of five Agent-Trace Python scripts crashed with unhandled exceptions when given invalid input. `build_manifest.py` raised `OSError` on nonexistent paths, `check_query_schema.py` raised `FileNotFoundError`, and `query_impact.py` returned all ADR nodes unconditionally regardless of query. Additional issues included silent `except Exception: pass` blocks suppressing errors, dead code in `SKIP_DIRS`, and endpoint regex false positives. All issues were remediated with input validation, proper error handling, and dead code removal.

## 2. Timeline

| Time | Event | Actor |
|------|-------|-------|
| 2026-03-18 | Scripts shipped in v1.0.0 with happy-path-only testing | Development |
| 2026-03-19 | Error-path test suite (v2 test plan) executed; crashes detected | Testing |
| 2026-03-19 | Triage confirmed P2 — functional on valid input, raw stack traces on edge cases | Development |
| 2026-03-20 | Input validation, error handling, dead code cleanup applied | Development |
| 2026-03-20 | All scripts pass error-path tests; PIR finalized | Development |

## 3. Five Whys

1. **Why?** — Scripts crash with unhandled exceptions on invalid input.
2. **Why?** — No input validation exists at script entry points.
3. **Why?** — Scripts were built for the happy path only; no error-path testing in v1.
4. **Why?** — The v1 test plan covered structural correctness only, not edge cases.
5. **Why?** -> **ROOT CAUSE:** Entry-point input validation was never scoped into v1 requirements. Error-path coverage was deferred implicitly rather than explicitly scheduled.

## 4. Blast Radius

| Radius | Affected | How |
|--------|----------|-----|
| Direct | `build_manifest.py`, `check_query_schema.py`, `query_impact.py` | Unhandled exceptions on invalid input; raw stack traces shown to user |
| Adjacent | `common.py`, `validate_universe.py` | Silent `except Exception: pass` suppressed real errors; dead code in SKIP_DIRS |
| Downstream | Any repo using Agent-Trace `/map` or `/query` commands | Commands invoking crashed scripts would fail with no actionable error message |
| Potential (if undetected) | User trust in blast-radius analysis | A governance tool that crashes on bad input undermines the safety guarantees it exists to provide |

## 5. Prompt Forensics

### Triggering input
```
# build_manifest.py
python build_manifest.py /nonexistent/path

# check_query_schema.py
python check_query_schema.py missing-file.json

# query_impact.py
python query_impact.py --file changed.py  # returns ALL nodes, not just impacted ones
```

### Expected vs actual
- Expected: Graceful error message with exit code 1 explaining what went wrong.
- Actual: Raw `OSError` / `FileNotFoundError` stack traces; `query_impact.py` silently returned the entire dependency graph.

## 6. What Went Well

- The v2 error-path test suite caught all three crash vectors before any user reported them.
- Scripts were correct on valid input — the core logic was sound; only the boundary handling was missing.
- The codebase was small enough (5 scripts, single directory) that a full audit was feasible in one pass.

## 7. What Went Wrong

- **No input validation at entry points.** All three scripts assumed valid filesystem paths and well-formed JSON.
- **Silent exception swallowing.** `except Exception: pass` blocks in shared code hid real errors, making debugging harder.
- **Dead code.** `SKIP_DIRS` contained entries that were never matched, adding confusion during review.
- **Regex false positives.** Endpoint detection regex matched non-endpoint strings, inflating the dependency graph.
- **query_impact.py logic error.** Missing filter condition caused unconditional return of all ADR nodes.

## 8. Where We Got Lucky

- No user encountered these crashes in production before the v2 test plan caught them.
- The `query_impact.py` bug returned too many results rather than too few — a conservative failure mode. If it had silently dropped nodes, blast-radius analysis would have been dangerously incomplete.

## 9. Remediation

### Immediate fix
- Added `os.path.exists()` / `os.path.isdir()` checks at entry points of `build_manifest.py` and `check_query_schema.py`.
- Wrapped file I/O in `try/except` with descriptive error messages and `sys.exit(1)`.
- Fixed `query_impact.py` filter logic to return only impacted nodes.

### Permanent fix
- Replaced all `except Exception: pass` with explicit exception types and logged warnings.
- Removed dead code from `SKIP_DIRS`.
- Tightened endpoint regex to reduce false positives.
- Added error-path test cases to the test suite covering nonexistent paths, malformed JSON, and empty input.

### Detection improvement
- Error-path tests now run as part of the standard validation suite, not as an optional second pass.

## 10. Action Items

| # | Action | Priority | Owner | Due | Status |
|---|--------|----------|-------|-----|--------|
| 1 | Add input validation to all script entry points | P2 | Dev | 2026-03-20 | Done |
| 2 | Replace silent `except Exception: pass` with typed handlers | P2 | Dev | 2026-03-20 | Done |
| 3 | Remove dead code in SKIP_DIRS | P3 | Dev | 2026-03-20 | Done |
| 4 | Fix endpoint regex false positives | P2 | Dev | 2026-03-20 | Done |
| 5 | Fix query_impact.py unconditional node return | P2 | Dev | 2026-03-20 | Done |
| 6 | Add error-path tests to standard test suite | P2 | Dev | 2026-03-20 | Done |

## 11. Lessons Learned

1. **Validate inputs at system boundaries, not deeper.** Entry-point validation is cheaper than debugging crashes in inner functions. Every script that accepts external input (paths, files, CLI args) must validate before processing.
2. **Silent exception handling is worse than crashing.** `except Exception: pass` masks real bugs and delays detection. Prefer explicit exception types with logged context.
3. **Test plans must explicitly scope error paths.** If edge-case testing is deferred, it must appear as a tracked action item — implicit deferral means it never happens.
