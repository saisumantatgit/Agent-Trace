# Scenario Walkthroughs

## Injected Dependency Contract

Target:

- `symbol:src/app/deps.py:get_data_store`

Expected query outcome:

- app factory as backward prerequisite
- route handlers in blast radius
- contract test in impacted tests
- injected-store invariant

## API to Persistence Propagation

Target:

- a route or store method involved in read/write operations

Expected query outcome:

- store writer and reader surfaces
- downstream consumers or report builders
- affected tests

## ADR Drift

Target:

- ADR-governed code path

Expected query outcome:

- docs or ADR nodes
- stale-area warnings
- source-of-truth declarations

## Schema Migration

Target:

- database model or schema definition

Expected query outcome:

- all read/write paths to the changed table or model
- serialization and deserialization boundaries
- API contract tests
- migration script references

## Auth Middleware Change

Target:

- authentication or authorization middleware

Expected query outcome:

- all protected routes as forward blast radius
- session management as backward prerequisite
- integration tests for auth flows
- security-related invariants
