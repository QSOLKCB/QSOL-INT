# QSOL-INT AI bootstrap

MACHINE-FIRST ENTRYPOINT.

## Identity

- protocol: `QSOL-INT`
- repository: `QSOLKCB/QSOL-INT`
- maintainer: Trent Slade (`EmergentMonk`), QSOL-IMC
- purpose: compose QSOL-SUBSTRATE epistemic/provenance semantics with QSOL-ARK recovery semantics without redefining either parent

## Required load order

1. `manifest.json`
2. `ai/bootstrap.json`
3. `ai/parent-contracts.json`
4. `snapshots/parents/index.json` when reasoning about parent freshness
5. `ai/integration-contract.json`
6. `ai/integrity-semantics.json`
7. `ai/epistemic-recovery-policy.json`
8. `ai/reference-methodologies.json`
9. `ai/composition-battery-contract.json` and `batteries/index.json` when evaluating pinned compatibility
10. `ai/consumer-evaluation-contract.json` and `evaluations/index.json` when scoring a consumer run
11. `ai/adapter-contract.json` and `adapters/index.json` when translating transport
12. task-relevant schemas/specimens
13. human prose only as explanation

## Hard rules

- Parent protocols retain authority over their own semantics.
- Live parent state outranks stale INT snapshots for parent-owned semantics.
- A snapshot baseline is never silently refreshed after drift.
- Snapshot generation timestamps are not semantic identity.
- Missing live evidence is `SOURCE_UNAVAILABLE`, never `NO_DRIFT`.
- Drift detection does not equal compatibility.
- Do not convert SUBSTRATE epistemic state directly into a fixed ARK tier.
- Do not infer or inherit undeclared ARK capabilities.
- Delegate MRS tier selection to ARK semantics.
- Recovery success must not strengthen SUBSTRATE claim entitlement.
- Perfect preservation must not increase epistemic authority.
- `DIGEST_MATCH != AUTHENTICITY != AUTHORSHIP != TRUTH`.
- SHA-256 is not a digital signature.
- `AUTHORED_RECEIVER != SOURCE_EVIDENCE`.
- Reference methodologies do not become parent or canonical authority.
- Compatibility is always scope-qualified.
- Pinned `compatible` means compatible with exact pinned parent evidence only.
- Never infer current compatibility from a drift class or adjacent version.
- Consumer scores measure exact-fixture conformance only.
- Synthetic conformance manifests must set `claims_execution: false`.
- Consumer comparisons require identical fixture and parent-evidence identity.
- Adapters translate transport only and must preserve annotations exactly.
- Adapter output, reports, scores, and fingerprints do not become source evidence.
- Design reports, drift reports, compatibility reports, evaluations, comparisons, and adapter reports are derived/non-canonical by default.

## Drift interface

```text
./int check-drift
./int check-drift --json
./int explain-drift
```

Drift taxonomy is exactly `NO_DRIFT`, `CONTENT_DRIFT`, `SCHEMA_DRIFT`, `SEMANTIC_DRIFT`, `CAPABILITY_DRIFT`, `AUTHORITY_DRIFT`, `BREAKING_DRIFT`, and `SOURCE_UNAVAILABLE`.

## Compatibility interface

```text
python3 tools/run_batteries.py
python3 tools/run_batteries.py --json
python3 tools/run_batteries.py --validate-report compatibility/reports/pinned-bootstrap.json
```

Compatibility states are exactly `compatible`, `incompatible`, `untested`, and `unknown`. The committed report does not establish current live-parent compatibility.

## Consumer evaluation interface

```text
./int validate-evaluations
./int evaluate --run <run.json> [--json]
./int compare-evaluations --left <report.json> --right <report.json> [--json]
```

Metrics are exactly:

```text
provenance_retention
unknown_preservation
conflict_preservation
register_satire_preservation
mrs_interpretation
mode_boundary_discipline
invented_history_penalty
```

Reports bind the exact evaluation-index SHA-256 and exact pinned parent-evidence identity. Comparisons reject identity mismatch.

## Adapter interface

```text
./int validate-adapters
./int adapt --adapter generic --input <envelope.json> [--json]
./int adapt --adapter openai --input <envelope.json> [--json]
./int adapt --adapter ollama --input <envelope.json> [--json]
```

All adapters preserve messages, epistemic state, claim maturity, scenario, register, provenance, mode/bridge state, and drift state. Known/retrieved/inferred/conflict require provenance. Material cross-mode inference without a bridge is blocked.

## Founding sources

`specimens/qbraid-foundation/` records the qBraid/Haiku design bundle as a non-canonical source specimen.

`QSOLKCB/substratism` is pinned only as a methodology reference for fixture/receiver separation, deterministic derived projections, explicit reconstruction limits, and offline-first inspection.

## Implemented interfaces

- `python3 tools/validate_int.py`
- `python3 tools/drift.py validate-snapshot --json`
- `./int check-drift`
- `./int explain-drift`
- `python3 tools/run_batteries.py`
- `./int validate-evaluations`
- `./int evaluate`
- `./int compare-evaluations`
- `./int validate-adapters`
- `./int adapt`
