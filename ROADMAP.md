# QSOL-INT Roadmap

QSOL-INT is the composition layer between QSOL-SUBSTRATE and QSOL-ARK.

Its constitutional rules are:

- **INTEGRATION_MUST_NOT_INCREASE_SEMANTIC_AUTHORITY**
- **AUTHORED_RECEIVER != SOURCE_EVIDENCE**
- **DRIFT_IS_NEVER_SILENTLY_ACCEPTED**
- **UNAVAILABLE != CONTRADICTED**

The core stays deliberately small:

```text
QSOL-SUBSTRATE  <---->  QSOL-INT  <---->  QSOL-ARK
epistemics              composition        recovery
```

Three core protocols; unlimited satellites.

The long-term QSOL-INT repository shape is:

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
- [x] Preserve tier-count, MRS, hash-language, receipt-coverage, and implementation-status discrepancies as findings.
- [x] Adopt the `substratism` fixture/receiver discipline as a non-canonical methodology reference.
- [x] Add human, AI, and agent entrypoints.
- [x] Add core JSON schemas.
- [x] Add stdlib-only local validator and regression tests.
- [x] Add CI for local contract validation.
- [x] Harden validation so canonical rule sets, artifact identities, entrypoints, preservation fields, source bindings, and approved methodology patterns fail closed when altered.

---

## PR #2 — Parent Snapshots and Drift Detection

### Goal

Make cross-repository semantic drift deterministic, inspectable, machine-readable, and fail-closed.

Primary commands:

```bash
./int check-drift
./int check-drift --json
./int explain-drift
```

The governing rule is:

> **Drift is never silently accepted.**

QSOL-INT may detect, compare, classify, explain, and constrain parent changes. It must not silently reinterpret or redefine QSOL-SUBSTRATE or QSOL-ARK semantics.

### Parent snapshots

- [ ] Add deterministic snapshots for the exact QSOL-SUBSTRATE machine contracts INT depends on.
- [ ] Add deterministic snapshots for the exact QSOL-ARK machine contracts INT depends on.
- [ ] Record parent repository URL, source commit, contract path, Git blob identity, and content SHA-256.
- [ ] Record snapshot schema/version and generation timestamp separately from semantic identity.
- [ ] Distinguish canonical parent machine contracts from explanatory prose.
- [ ] Keep snapshots minimal: copy only contracts INT actually depends on.
- [ ] Treat live parent repository state as higher authority than stale INT snapshots.
- [ ] Never silently refresh a baseline after drift is detected.

### Drift taxonomy

INT SHALL classify parent change as one or more of:

- `NO_DRIFT`
- `CONTENT_DRIFT`
- `SCHEMA_DRIFT`
- `SEMANTIC_DRIFT`
- `CAPABILITY_DRIFT`
- `AUTHORITY_DRIFT`
- `BREAKING_DRIFT`
- `SOURCE_UNAVAILABLE`

A changed byte is not automatically a breaking semantic change.

### Classification rules

- [ ] Documentation-only changes may be `CONTENT_DRIFT` with no integration impact.
- [ ] Schema changes trigger `SCHEMA_DRIFT`.
- [ ] Changes to parent contract meaning trigger `SEMANTIC_DRIFT`.
- [ ] Changes to ARK tier capabilities or implementation state trigger `CAPABILITY_DRIFT`.
- [ ] Changes affecting epistemic entitlement, provenance, public boundaries, canonicality, or parent authority trigger `AUTHORITY_DRIFT`.
- [ ] Changes making the current INT composition unsafe or invalid trigger `BREAKING_DRIFT`.
- [ ] Missing or unreachable parent evidence becomes `SOURCE_UNAVAILABLE`, never `NO_DRIFT`.
- [ ] Unknown integration impact requires explicit review rather than optimistic compatibility.

### `./int check-drift`

Default output should be deterministic and terse.

```text
QSOL-INT PARENT DRIFT CHECK

QSOL-SUBSTRATE
  expected commit: 60e8cfe...
  current commit:  60e8cfe...
  contracts:       MATCH
  status:          CLEAN

QSOL-ARK
  expected commit: f2bbf149...
  current commit:  a8132c4...
  changed:
    ai/recovery-tiers.json
    ai/minimum-recoverable-substrate.json

classification:
  CAPABILITY_DRIFT
  SEMANTIC_DRIFT

action:
  REVIEW_REQUIRED

result:
  INT_PARENT_DRIFT_DETECTED
```

### `./int check-drift --json`

Machine output must not require prose parsing.

```json
{
  "status": "INT_PARENT_DRIFT_DETECTED",
  "parent": "QSOL-ARK",
  "drift_classes": [
    "CAPABILITY_DRIFT",
    "SEMANTIC_DRIFT"
  ],
  "breaking": false,
  "requires_review": true,
  "changed_contracts": [
    "ai/recovery-tiers.json"
  ]
}
```

### `./int explain-drift`

The explanation command reports why a detected change may matter without gaining authority over the parent contract.

```text
WHY THIS MATTERS

Parent:
  QSOL-ARK

Contract:
  ai/recovery-tiers.json

Change:
  T5 implementation state changed

Old:
  implemented=false

New:
  implemented=true

Potential integration effect:
  MRS requests for model_reconstruction may now resolve where they previously failed closed.

Authority effect:
  NONE

Capability effect:
  YES

Recommended action:
  re-run compatibility battery
```

### Typed outcomes

Planned machine-visible statuses:

- `INT_OK`
- `INT_PARENT_DRIFT_DETECTED`
- `INT_PARENT_SOURCE_UNAVAILABLE`
- `INT_PARENT_SNAPSHOT_INVALID`
- `INT_PARENT_RECEIPT_MISMATCH`
- `INT_PARENT_CONTRACT_MISSING`
- `INT_DRIFT_CLASSIFICATION_UNRESOLVED`
- `INT_BREAKING_DRIFT`
- `INT_REVIEW_REQUIRED`

Unavailable evidence is not contradictory evidence.

### Validation

- [ ] Stdlib-only reference implementation where practical.
- [ ] Deterministic canonical JSON drift reports.
- [ ] SHA-256 receipts for parent snapshots.
- [ ] Regression test every drift class.
- [ ] Test documentation-only changes.
- [ ] Test schema-only changes.
- [ ] Test ARK capability changes.
- [ ] Test ARK implementation-state changes.
- [ ] Test SUBSTRATE epistemic-rule changes.
- [ ] Test SUBSTRATE public-boundary changes.
- [ ] Test missing parent source.
- [ ] Test malformed parent snapshot.
- [ ] Test unchanged parent state.
- [ ] CI must fail closed on unresolved breaking drift.

---

## PR #3 — Cross-Repo Composition Batteries and Compatibility Reports

- [ ] Provenance-retention battery.
- [ ] Unknown-preservation battery.
- [ ] Conflict-preservation battery.
- [ ] Satire/register-preservation battery.
- [ ] Cross-mode boundary battery.
- [ ] Recovery-without-authority-escalation battery.
- [ ] Perfect-hash-does-not-increase-evidence-strength battery.
- [ ] Capability-invention and stale-parent batteries.
- [ ] Composition validator over exact parent snapshots.
- [ ] Compatibility reports bound to exact parent commits and contract hashes.
- [ ] Distinguish `compatible`, `incompatible`, `untested`, and `unknown`.
- [ ] Never infer compatibility from adjacent versions.

Core invariant:

> **Perfect preservation must never increase epistemic authority.**

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
- [ ] Consumer comparisons require exact fixture and parent-snapshot identity.
- [ ] Consumer reports remain derived and non-canonical.

---

## PR #5 — Adapters and Integration Fixtures

- [ ] Generic JSON adapter.
- [ ] OpenAI adapter.
- [ ] Ollama adapter.
- [ ] Additional adapters only when they preserve canonical INT semantics.
- [ ] Valid fixtures.
- [ ] Invalid fixtures.
- [ ] Unknown fixtures.
- [ ] Conflict fixtures.
- [ ] Satire fixtures.
- [ ] Cross-mode fixtures.
- [ ] Missing-provenance fixtures.
- [ ] Drift fixtures.

Adapters translate transport. They do not redefine truth.

---

## Future / ARK-gated work

When ARK implements T5, INT may consume ARK's real model-reconstruction contract. INT must not implement, emulate, or silently invent T5 ahead of ARK.

As ARK gains computer-cultural, ancient-system, and ancient-network preservation layers, INT should compose them with SUBSTRATE provenance and mode policy without turning reconstructions, emulators, or authored receivers into canonical historical fact.

---

## Deferred

Remote service; database dependency; vector DB as canonical INT state; model-specific latent canonical state; automatic mutation of parent repositories; silent baseline updates; any claim that a hash alone authenticates a person or organization.
