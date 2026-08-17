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
4. `ai/integration-contract.json`
5. `ai/integrity-semantics.json`
6. `ai/epistemic-recovery-policy.json`
7. `ai/reference-methodologies.json`
8. `ai/composition-battery-contract.json` when evaluating compatibility
9. `batteries/index.json` when running PR #3 composition tests
10. task-relevant schemas/specimens
11. human prose only as explanation

## Hard rules

- Parent protocols retain authority over their own semantics.
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
- Live parent freshness remains `untested` until PR #2 drift evidence exists.
- Never infer compatibility from adjacent versions.
- Design reports and compatibility reports are derived/non-canonical by default.

## PR #3 machine interface

```text
python3 tools/run_batteries.py
python3 tools/run_batteries.py --json
python3 tools/run_batteries.py --validate-report compatibility/reports/pinned-bootstrap.json
```

Compatibility states are exactly:

```text
compatible
incompatible
untested
unknown
```

The committed baseline report is `compatibility/reports/pinned-bootstrap.json`.

Its parent identities, case results, and fingerprint are deterministic. The report does not establish current live-parent compatibility.

## Founding sources

`specimens/qbraid-foundation/` records the qBraid/Haiku design bundle as a non-canonical source specimen.

`QSOLKCB/substratism` is pinned only as a methodology reference for fixture/receiver separation, deterministic derived projections, explicit reconstruction limits, and offline-first inspection.

## Implemented interfaces

- `python3 tools/validate_int.py`
- `python3 tools/run_batteries.py`

Live parent drift tooling (`./int check-drift`, `./int explain-drift`) remains PR #2 work.
