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
8. task-relevant schemas/specimens
9. human prose only as explanation

## Hard rules

- Parent protocols retain authority over their own semantics.
- Do not convert SUBSTRATE epistemic state directly into a fixed ARK tier.
- Do not infer or inherit undeclared ARK capabilities.
- Delegate MRS tier selection to ARK semantics.
- Recovery success must not strengthen SUBSTRATE claim entitlement.
- `DIGEST_MATCH != AUTHENTICITY != AUTHORSHIP != TRUTH`.
- SHA-256 is not a digital signature.
- `AUTHORED_RECEIVER != SOURCE_EVIDENCE`.
- Reference methodologies do not become parent or canonical authority.
- Pinned parent snapshots are last-known offline evidence; live material drift fails closed until compatibility is re-evaluated.
- Design reports are non-canonical by default.

## Founding sources

`specimens/qbraid-foundation/` records the qBraid/Haiku design bundle as a non-canonical source specimen.

`QSOLKCB/substratism` is pinned only as a methodology reference for fixture/receiver separation, deterministic derived projections, explicit reconstruction limits, and offline-first inspection.

## Implemented interface

`python3 tools/validate_int.py`

This validates the local bootstrap; live parent drift tooling remains planned.
