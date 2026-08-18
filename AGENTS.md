# QSOL-INT Agent Contract

MACHINE-FIRST OPERATING CONTRACT.

## Authority order

1. live parent repository state for parent-owned semantics;
2. pinned parent evidence when live access is unavailable;
3. QSOL-INT canonical integration contracts for composition semantics only;
4. source design inputs and reference methodologies;
5. derived reports, receivers, evaluations, and prose projections.

## Parent ownership

QSOL-SUBSTRATE owns epistemic state, claim maturity, scenario/register semantics, modes/bridges, source policy, and public boundary. QSOL-ARK owns recovery tiers, tier capabilities, implementation state, MRS, and recovery behavior. QSOL-INT must not silently redefine either parent.

## Composition rules

- Never strengthen a SUBSTRATE claim because recovery succeeded.
- Never weaken uncertainty because bytes verified.
- Never treat ARK rank as evidence that lower tiers ran.
- Never infer ARK capabilities from rank or adjacency.
- Never create a canonical fixed mapping from SUBSTRATE state to ARK tier.
- Request only capabilities explicitly declared by ARK.
- Treat live/pinned parent disagreement as drift.
- Never promote an INT-authored receiver into source evidence.
- Perfect preservation must never increase epistemic authority.

## PR #2 drift discipline

- Validate the committed parent snapshot before comparing live state.
- Snapshot only exact machine contracts INT depends on.
- Bind every copied contract to parent repository, source commit, path, Git blob identity, and content SHA-256.
- Keep generation timestamps outside semantic snapshot identity.
- Live parent state outranks stale snapshot state for parent-owned semantics.
- Never refresh the baseline automatically after drift.
- Missing live evidence is `SOURCE_UNAVAILABLE`, never `NO_DRIFT`.
- A changed byte does not automatically imply semantic or breaking drift.
- Unknown impact produces `INT_DRIFT_CLASSIFICATION_UNRESOLVED` and requires review.
- Drift detection does not prove changed-parent compatibility.
- `BREAKING_DRIFT` is reserved for deterministically unsafe composition changes, not mere version movement.

## PR #3 compatibility discipline

- All committed battery fixtures are synthetic integration fixtures.
- `compatible` must always include a declared scope.
- PR #3 compatibility scope remains `pinned_parent_evidence_only`.
- Never infer current compatibility from a pinned compatibility report or a non-breaking drift class.
- Never infer compatibility from version adjacency.
- Unknown and conflict remain visible unless parent-owned evidence changes them.
- Material cross-mode inference without a declared bridge is blocked.
- Undeclared ARK capabilities are rejected.
- Compatibility reports are derived receivers, not parent authority.
- A report fingerprint proves report integrity only.

## Reference methodology discipline

`QSOLKCB/substratism` is a non-canonical reference, not a parent. Its useful pattern is fixture/receiver separation. Do not import its moral claims, scale, coefficients, or UI semantics into INT.

## Cryptographic language

SHA-256 digest match establishes byte equality relative to a compared digest. It does not establish author identity, original publication source, digital signature, claim truth, or trustworthiness.

## Failure discipline

Bootstrap failures include `INT_PARENT_PIN_INVALID`, `INT_PARENT_CONTRACT_INCOMPLETE`, `INT_CAPABILITY_REDEFINITION`, `INT_STATE_TIER_COUPLING_FORBIDDEN`, `INT_INTEGRITY_SEMANTICS_INVALID`, `INT_QBRAID_SPECIMEN_INVALID`, `INT_QBRAID_RECEIPT_COVERAGE_MISMATCH`, `INT_REFERENCE_METHODOLOGY_INVALID`, and `INT_RECEIVER_AUTHORITY_ESCALATION`.

PR #2 adds `INT_PARENT_DRIFT_DETECTED`, `INT_PARENT_SOURCE_UNAVAILABLE`, `INT_PARENT_SNAPSHOT_INVALID`, `INT_PARENT_RECEIPT_MISMATCH`, `INT_PARENT_CONTRACT_MISSING`, `INT_DRIFT_CLASSIFICATION_UNRESOLVED`, `INT_BREAKING_DRIFT`, and `INT_REVIEW_REQUIRED`.

PR #3 adds `INT_BATTERY_INDEX_INVALID`, `INT_BATTERY_CASE_INVALID`, `INT_BATTERY_EXPECTATION_FAILED`, `INT_COMPATIBILITY_REPORT_INVALID`, `INT_CAPABILITY_INVENTION`, `INT_AUTHORITY_ESCALATION`, `INT_PROVENANCE_LOSS`, `INT_CROSS_MODE_BRIDGE_REQUIRED`, and `INT_PARENT_FRESHNESS_UNTESTED`.

Unknowns fail closed. Contradiction is not unavailability.
