# QSOL-INT — AI bootstrap

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
9. `ai/composition-battery-contract.json` when evaluating compatibility
10. `batteries/index.json` when running PR #3 composition tests
11. task-relevant schemas/specimens
12. human prose only as explanation

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
- PR #3 `compatible` means compatible with exact pinned parent evidence only.
- Never infer current compatibility from a drift class or adjacent version.
- Design reports, drift reports, and compatibility reports are derived/non-canonical by default.

## PR #2 machine interface

```text
./int check-drift
./int check-drift --json
./int explain-drift
```

Drift taxonomy is exactly:

```text
NO_DRIFT
CONTENT_DRIFT
SCHEMA_DRIFT
SEMANTIC_DRIFT
CAPABILITY_DRIFT
AUTHORITY_DRIFT
BREAKING_DRIFT
SOURCE_UNAVAILABLE
```

Typed outcomes are `INT_OK`, `INT_PARENT_DRIFT_DETECTED`, `INT_PARENT_SOURCE_UNAVAILABLE`, `INT_PARENT_SNAPSHOT_INVALID`, `INT_PARENT_RECEIPT_MISMATCH`, `INT_PARENT_CONTRACT_MISSING`, `INT_DRIFT_CLASSIFICATION_UNRESOLVED`, `INT_BREAKING_DRIFT`, and `INT_REVIEW_REQUIRED`.

Canonical drift JSON contains no generation timestamp. A changed byte is not automatically breaking semantic drift. Unknown impact requires review.

## PR #3 machine interface

```text
python3 tools/run_batteries.py
python3 tools/run_batteries.py --json
python3 tools/run_batteries.py --validate-report compatibility/reports/pinned-bootstrap.json
```

Compatibility states are exactly `compatible`, `incompatible`, `untested`, and `unknown`.

The committed baseline report is `compatibility/reports/pinned-bootstrap.json`. Its parent identities, case results, and fingerprint are deterministic. The report does not establish current live-parent compatibility.

## Founding sources

`specimens/qbraid-foundation/` records the qBraid/Haiku design bundle as a non-canonical source specimen.

`QSOLKCB/substratism` is pinned only as a methodology reference for fixture/receiver separation, deterministic derived projections, explicit reconstruction limits, and offline-first inspection.

## Implemented interfaces

- `python3 tools/validate_int.py`
- `python3 tools/drift.py validate-snapshot --json`
- `./int check-drift`
- `./int check-drift --json`
- `./int explain-drift`
- `python3 tools/run_batteries.py`
