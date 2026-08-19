# QSOL-INT Roadmap

QSOL-INT is the composition layer between QSOL-SUBSTRATE and QSOL-ARK.

Constitutional rules:

- **INTEGRATION_MUST_NOT_INCREASE_SEMANTIC_AUTHORITY**
- **AUTHORED_RECEIVER != SOURCE_EVIDENCE**
- **DRIFT_IS_NEVER_SILENTLY_ACCEPTED**
- **UNAVAILABLE != CONTRADICTED**
- **PERFECT_PRESERVATION_MUST_NOT_INCREASE_EPISTEMIC_AUTHORITY**

```text
QSOL-SUBSTRATE  <---->  QSOL-INT  <---->  QSOL-ARK
epistemics              composition        recovery
```

Three core protocols; unlimited satellites.

Long-term repository shape:

```text
QSOL-INT
├── compatibility reports
├── parent snapshots
├── cross-repo test batteries
├── consumer evaluations
└── adapters / integration fixtures
```

---

## PR #1 — Bootstrap and clean the founding design

**Status: implemented and merged.**

- [x] Preserve the SUBSTRATE / ARK / INT three-layer framing.
- [x] Replace fixed epistemic-state-to-tier mapping with capability-based composition.
- [x] Pin current SUBSTRATE and ARK contract evidence.
- [x] Record parent semantic ownership explicitly.
- [x] Separate digest integrity from authenticity, authorship, signature, and truth.
- [x] Record the qBraid/Haiku bundle as non-canonical design input.
- [x] Adopt `substratism` fixture/receiver discipline as a non-canonical methodology reference.
- [x] Add human, AI, and agent entrypoints.
- [x] Add stdlib-only validation, schemas, regression tests, and CI.
- [x] Harden canonical identities, rule sets, entrypoints, source bindings, and methodology boundaries.

---

## PR #2 — Parent Snapshots and Drift Detection

**Status: implemented and merged through repository PR #3. Drift detection does not retroactively widen pinned compatibility scope.**

### Goal

Make cross-repository drift deterministic, inspectable, machine-readable, and fail-closed.

Implemented commands:

```bash
./int check-drift
./int check-drift --json
./int explain-drift
```

Governing rule:

> **Drift is never silently accepted.**

### Parent snapshots

- [x] Snapshot only the exact SUBSTRATE and ARK machine contracts INT depends on.
- [x] Record repository, source commit, path, Git blob identity, and content SHA-256.
- [x] Keep semantic identity separate from generation timestamps.
- [x] Treat live parent state as higher authority than stale snapshots.
- [x] Never silently refresh a baseline after drift.

### Drift taxonomy

- `NO_DRIFT`
- `CONTENT_DRIFT`
- `SCHEMA_DRIFT`
- `SEMANTIC_DRIFT`
- `CAPABILITY_DRIFT`
- `AUTHORITY_DRIFT`
- `BREAKING_DRIFT`
- `SOURCE_UNAVAILABLE`

A changed byte is not automatically breaking semantic drift.

### Classification rules

- [x] Documentation-only change may be `CONTENT_DRIFT`.
- [x] Schema changes trigger `SCHEMA_DRIFT`.
- [x] Contract-meaning changes trigger `SEMANTIC_DRIFT`.
- [x] ARK capability/implementation changes trigger `CAPABILITY_DRIFT`.
- [x] Epistemic entitlement, provenance, boundary, or canonicality changes trigger `AUTHORITY_DRIFT`.
- [x] Unsafe composition triggers `BREAKING_DRIFT`.
- [x] Missing live evidence becomes `SOURCE_UNAVAILABLE`, never `NO_DRIFT`.
- [x] Unknown impact requires review rather than optimistic compatibility.

### Typed outcomes

- `INT_OK`
- `INT_PARENT_DRIFT_DETECTED`
- `INT_PARENT_SOURCE_UNAVAILABLE`
- `INT_PARENT_SNAPSHOT_INVALID`
- `INT_PARENT_RECEIPT_MISMATCH`
- `INT_PARENT_CONTRACT_MISSING`
- `INT_DRIFT_CLASSIFICATION_UNRESOLVED`
- `INT_BREAKING_DRIFT`
- `INT_REVIEW_REQUIRED`

### Validation

- [x] Stdlib-only reference implementation where practical.
- [x] Canonical JSON drift reports.
- [x] SHA-256 snapshot receipts.
- [x] Regression-test every drift class.
- [x] Test unchanged, documentation, schema, capability, implementation, authority, missing-source, and malformed-snapshot cases.
- [x] CI fails closed on unresolved breaking drift.

---

## PR #3 — Cross-Repo Composition Batteries and Compatibility Reports

**Status: implemented and merged. PR #2 supplies drift evidence, but compatibility remains exact-pinned-evidence scoped.**

### Deterministic battery suite

- [x] Provenance-retention battery.
- [x] Unknown-preservation battery.
- [x] Conflict-preservation battery.
- [x] Satire/register-preservation battery.
- [x] Cross-mode boundary battery.
- [x] Recovery-without-authority-escalation battery.
- [x] Perfect-hash-does-not-increase-evidence-strength battery.
- [x] Capability-invention battery.
- [x] Stale-parent/freshness battery.

### Composition runner

- [x] Add stdlib-only `tools/run_batteries.py`.
- [x] Add deterministic human output.
- [x] Add canonical machine JSON output.
- [x] Reuse PR #1 parent-contract validation.
- [x] Bind results to exact pinned parent commit and Git blob identities.
- [x] Reject undeclared ARK capabilities.
- [x] Block material cross-mode inference without a bridge.
- [x] Preserve provenance, unknown, conflict, register, scenario, and authority annotations as specified by fixtures.

### Compatibility reports

- [x] Add committed deterministic baseline `compatibility/reports/pinned-bootstrap.json`.
- [x] Fingerprint canonical report JSON with SHA-256.
- [x] Validate committed report against current pinned evidence and case set.
- [x] Require byte-identical report regeneration in CI.
- [x] Distinguish `compatible`, `incompatible`, `untested`, and `unknown`.
- [x] Never infer compatibility from adjacent versions.
- [x] Scope compatibility to `pinned_parent_evidence_only`.
- [x] Keep current-parent compatibility unclaimed until changed parent evidence is explicitly evaluated.

Core invariant:

> **Perfect preservation must never increase epistemic authority.**

Result semantics:

```text
pinned compatibility: compatible
current-parent compatibility: NOT CLAIMED
```

### Tests / CI

- [x] Nine composition fixtures.
- [x] Nine PR #3 regression tests.
- [x] Dedicated composition-battery workflow.
- [x] JSON parsing for battery/contracts/reports/schemas.
- [x] Deterministic report regeneration check.

---

## PR #4 — Consumer Evaluations

**Status: implemented in this PR. Synthetic reference runs do not claim model or agent execution.**

Implemented commands:

```bash
./int validate-evaluations
./int evaluate --run <run.json>
./int evaluate --run <run.json> --json
./int compare-evaluations --left <report.json> --right <report.json>
```

- [x] Deterministic consumer evaluation inputs.
- [x] Model/agent run manifests.
- [x] Provenance-retention score.
- [x] Unknown-preservation score.
- [x] Conflict-preservation score.
- [x] Register/satire-preservation score.
- [x] MRS-interpretation score.
- [x] Mode-boundary-discipline score.
- [x] Invented-history penalty.
- [x] Consumer comparisons require exact fixture and parent-evidence identity.
- [x] Reports remain derived and non-canonical.

### Evaluation discipline

- Each metric has one deterministic synthetic case with machine-readable assertions.
- Run manifests bind the exact evaluation-index SHA-256 and exact pinned parent-evidence identity.
- `synthetic_conformance` runs must set `claims_execution: false`.
- Model, agent, and deterministic-replay runs must declare execution explicitly.
- A score measures only conformance to the declared fixture set.
- A higher score does not establish general intelligence, safety, truthfulness, or broad model quality.
- Comparisons fail closed when evaluation or parent identities differ.
- Reports and comparisons carry deterministic SHA-256 fingerprints without becoming parent authority.

Committed reference artifacts include a conformant synthetic run, an adversarial synthetic run, their deterministic reports, and an identity-bound comparison.

---

## PR #5 — Adapters and Integration Fixtures

**Status: implemented in this PR. Adapters translate transport and do not redefine truth.**

Implemented commands:

```bash
./int validate-adapters
./int adapt --adapter generic --input <envelope.json>
./int adapt --adapter openai --input <envelope.json>
./int adapt --adapter ollama --input <envelope.json>
```

- [x] Generic JSON adapter.
- [x] OpenAI-compatible adapter.
- [x] Ollama adapter.
- [x] Additional adapters only when canonical INT semantics survive transport.
- [x] Valid, invalid, unknown, conflict, satire, cross-mode, missing-provenance, and drift fixtures.

### Adapter discipline

- The canonical envelope preserves messages, epistemic state, claim maturity, scenario, register, provenance, mode/bridge state, and drift state.
- Known, retrieved, inferred, and conflict states require provenance.
- Conflict requires at least two source records.
- Material cross-mode inference without a bridge is blocked.
- Drift or unavailable state remains review-required.
- OpenAI-compatible and Ollama outputs leave model identity as an explicit runtime placeholder.
- No API key is embedded.
- Semantic receipts prove compared serialization identity only.
- The deterministic conformance matrix covers three adapters across eight fixture kinds.

---

## Future / ARK-gated work

When ARK implements T5, INT may consume ARK's real model-reconstruction contract. INT must not implement, emulate, or silently invent T5 ahead of ARK.

As ARK gains computer-cultural, ancient-system, and ancient-network preservation layers, INT should compose them with SUBSTRATE provenance and mode policy without turning reconstructions, emulators, or authored receivers into canonical historical fact.

---

## Deferred

Remote service; database dependency; vector DB as canonical INT state; model-specific latent canonical state; automatic mutation of parent repositories; silent baseline updates; any claim that a hash alone authenticates a person or organization.
