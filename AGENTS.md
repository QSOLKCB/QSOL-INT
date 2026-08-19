# QSOL-INT Agent Contract

MACHINE-FIRST OPERATING CONTRACT.

## Authority order

1. live parent repository state for parent-owned semantics;
2. pinned parent evidence when live access is unavailable;
3. QSOL-INT canonical integration contracts for composition semantics only;
4. source design inputs and reference methodologies;
5. derived reports, receivers, evaluations, adapter outputs, and prose projections.

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

## Drift discipline

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

## Compatibility discipline

- All committed battery fixtures are synthetic integration fixtures.
- `compatible` must always include a declared scope.
- Compatibility scope remains `pinned_parent_evidence_only` until changed parent evidence is evaluated explicitly.
- Never infer current compatibility from a pinned compatibility report or a non-breaking drift class.
- Never infer compatibility from version adjacency.
- Unknown and conflict remain visible unless parent-owned evidence changes them.
- Material cross-mode inference without a declared bridge is blocked.
- Undeclared ARK capabilities are rejected.
- Compatibility reports are derived receivers, not parent authority.
- A report fingerprint proves report integrity only.

## Consumer evaluation discipline

- Consumer evaluation cases are deterministic synthetic fixtures.
- Run manifests bind the exact evaluation index and pinned parent-evidence identity.
- A synthetic conformance run must set `claims_execution` to false.
- A model or agent execution run must declare execution explicitly; identity authentication remains a separate field.
- Provenance, unknown, conflict, register/satire, MRS, mode-boundary, and invented-history metrics measure fixture conformance only.
- Reports and comparisons remain derived and non-canonical.
- Comparisons fail closed unless fixture and parent-evidence identities match exactly.
- A higher fixture score does not establish general intelligence, truthfulness, safety, or broad model quality.

## Adapter discipline

- Generic JSON, OpenAI-compatible, and Ollama adapters translate transport only.
- Preserve messages and every semantic annotation exactly.
- Do not hide unknown, conflict, satire, drift, or review-required state.
- Known, retrieved, inferred, and conflicting claims require provenance.
- Conflict requires at least two source records.
- Material cross-mode inference without a declared bridge is blocked.
- Model identifiers are runtime placeholders, not INT facts.
- Never embed API keys.
- Adapter SHA-256 receipts establish compared serialization identity only.
- Adapter output must never become parent authority, source evidence, or proof of execution.

## Reference methodology discipline

`QSOLKCB/substratism` is a non-canonical reference, not a parent. Its useful pattern is fixture/receiver separation. Do not import its moral claims, scale, coefficients, or UI semantics into INT.

## Cryptographic language

SHA-256 digest match establishes byte equality relative to a compared digest. It does not establish author identity, original publication source, digital signature, claim truth, or trustworthiness.

## Failure discipline

Bootstrap failures include `INT_PARENT_PIN_INVALID`, `INT_PARENT_CONTRACT_INCOMPLETE`, `INT_CAPABILITY_REDEFINITION`, `INT_STATE_TIER_COUPLING_FORBIDDEN`, `INT_INTEGRITY_SEMANTICS_INVALID`, `INT_QBRAID_SPECIMEN_INVALID`, `INT_QBRAID_RECEIPT_COVERAGE_MISMATCH`, `INT_REFERENCE_METHODOLOGY_INVALID`, and `INT_RECEIVER_AUTHORITY_ESCALATION`.

Drift failures include `INT_PARENT_DRIFT_DETECTED`, `INT_PARENT_SOURCE_UNAVAILABLE`, `INT_PARENT_SNAPSHOT_INVALID`, `INT_PARENT_RECEIPT_MISMATCH`, `INT_PARENT_CONTRACT_MISSING`, `INT_DRIFT_CLASSIFICATION_UNRESOLVED`, `INT_BREAKING_DRIFT`, and `INT_REVIEW_REQUIRED`.

Compatibility failures include `INT_BATTERY_INDEX_INVALID`, `INT_BATTERY_CASE_INVALID`, `INT_BATTERY_EXPECTATION_FAILED`, `INT_COMPATIBILITY_REPORT_INVALID`, `INT_CAPABILITY_INVENTION`, `INT_AUTHORITY_ESCALATION`, `INT_PROVENANCE_LOSS`, `INT_CROSS_MODE_BRIDGE_REQUIRED`, and `INT_PARENT_FRESHNESS_UNTESTED`.

Evaluation failures include `INT_EVALUATION_INDEX_INVALID`, `INT_EVALUATION_CASE_INVALID`, `INT_EVALUATION_ASSERTION_FAILED`, `INT_CONSUMER_RUN_INVALID`, `INT_CONSUMER_RESPONSE_MISSING`, `INT_EVALUATION_IDENTITY_MISMATCH`, `INT_EVALUATION_REPORT_INVALID`, and `INT_EVALUATION_COMPARISON_INVALID`.

Adapter failures include `INT_ADAPTER_CONTRACT_INVALID`, `INT_ADAPTER_INDEX_INVALID`, `INT_ADAPTER_FIXTURE_INVALID`, `INT_ADAPTER_ENVELOPE_INVALID`, `INT_ADAPTER_PROVENANCE_REQUIRED`, `INT_ADAPTER_CONFLICT_PROVENANCE_INCOMPLETE`, `INT_CROSS_MODE_BRIDGE_REQUIRED`, `INT_ADAPTER_DRIFT_REVIEW_REQUIRED`, `INT_ADAPTER_SEMANTIC_LOSS`, `INT_ADAPTER_REPORT_INVALID`, and `INT_ADAPTER_UNKNOWN`.

Unknowns fail closed. Contradiction is not unavailability.
