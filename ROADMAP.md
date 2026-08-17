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

**Status: planned. PR #3 must not pretend this exists.**

### Goal

Make cross-repository drift deterministic, inspectable, machine-readable, and fail-closed.

Planned commands:

```bash
./int check-drift
./int check-drift --json
./int explain-drift
```

Governing rule:

> **Drift is never silently accepted.**

### Parent snapshots

- [ ] Snapshot only the exact SUBSTRATE and ARK machine contracts INT depends on.
- [ ] Record repository, source commit, path, Git blob identity, and content SHA-256.
- [ ] Keep semantic identity separate from generation timestamps.
- [ ] Treat live parent state as higher authority than stale snapshots.
- [ ] Never silently refresh a baseline after drift.

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

- [ ] Documentation-only change may be `CONTENT_DRIFT`.
- [ ] Schema changes trigger `SCHEMA_DRIFT`.
- [ ] Contract-meaning changes trigger `SEMANTIC_DRIFT`.
- [ ] ARK capability/implementation changes trigger `CAPABILITY_DRIFT`.
- [ ] Epistemic entitlement, provenance, boundary, or canonicality changes trigger `AUTHORITY_DRIFT`.
- [ ] Unsafe composition triggers `BREAKING_DRIFT`.
- [ ] Missing live evidence becomes `SOURCE_UNAVAILABLE`, never `NO_DRIFT`.
- [ ] Unknown impact requires review rather than optimistic compatibility.

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

- [ ] Stdlib-only reference implementation where practical.
- [ ] Canonical JSON drift reports.
- [ ] SHA-256 snapshot receipts.
- [ ] Regression-test every drift class.
- [ ] Test unchanged, documentation, schema, capability, implementation, authority, missing-source, and malformed-snapshot cases.
- [ ] CI fails closed on unresolved breaking drift.

---

## PR #3 — Cross-Repo Composition Batteries and Compatibility Reports

**Status: implemented in this PR.**

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
- [x] Scope PR #3 compatibility to `pinned_parent_evidence_only`.
- [x] Explicitly mark `live_parent_freshness` as `untested` until PR #2 exists.

Core invariant:

> **Perfect preservation must never increase epistemic authority.**

PR #3 result semantics:

```text
pinned compatibility: compatible
live parent freshness: untested
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

- [ ] Deterministic consumer evaluation inputs.
- [ ] Model/agent run manifests.
- [ ] Provenance-retention score.
- [ ] Unknown-preservation score.
- [ ] Conflict-preservation score.
- [ ] Register/satire-preservation score.
- [ ] MRS-interpretation score.
- [ ] Mode-boundary-discipline score.
- [ ] Invented-history penalty.
- [ ] Consumer comparisons require exact fixture and parent-evidence identity.
- [ ] Reports remain derived and non-canonical.

---

## PR #5 — Adapters and Integration Fixtures

- [ ] Generic JSON adapter.
- [ ] OpenAI adapter.
- [ ] Ollama adapter.
- [ ] Additional adapters only when canonical INT semantics survive transport.
- [ ] Valid, invalid, unknown, conflict, satire, cross-mode, missing-provenance, and drift fixtures.

Adapters translate transport. They do not redefine truth.

---

## Future / ARK-gated work

When ARK implements T5, INT may consume ARK's real model-reconstruction contract. INT must not implement, emulate, or silently invent T5 ahead of ARK.

As ARK gains computer-cultural, ancient-system, and ancient-network preservation layers, INT should compose them with SUBSTRATE provenance and mode policy without turning reconstructions, emulators, or authored receivers into canonical historical fact.

---

## Deferred

Remote service; database dependency; vector DB as canonical INT state; model-specific latent canonical state; automatic mutation of parent repositories; silent baseline updates; any claim that a hash alone authenticates a person or organization.
