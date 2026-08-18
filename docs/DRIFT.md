# Parent snapshots and drift detection

QSOL-INT compares the exact parent-owned machine contracts it depends on against live QSOL-SUBSTRATE and QSOL-ARK state.

## Commands

```sh
./int check-drift
./int check-drift --json
./int explain-drift
```

`check-drift` reads the committed snapshot receipt, validates every copied contract against both its Git blob identity and its SHA-256 receipt, resolves each parent `main` ref to a live commit, and fetches only the machine contracts declared in `snapshots/parents/index.json`.

No command refreshes the baseline. A baseline change is an explicit repository change requiring review.

## Authority

```text
live parent state > committed parent snapshot > INT composition rules > derived report
```

The snapshot is last-known evidence. It is not a way to overrule a newer parent contract. Missing live evidence is `SOURCE_UNAVAILABLE`, never `NO_DRIFT`.

Generation metadata is excluded from semantic snapshot identity. The snapshot ID is SHA-256 over canonical JSON containing only parent repository, source commit, source ref, paths, semantic roles, Git blob identities, SHA-256 content receipts, and snapshot paths.

A digest proves compared-byte identity only. It does not prove authorship, signature, provenance, canonicality, or truth.

## Drift taxonomy

- `NO_DRIFT`: exact contract bytes match.
- `CONTENT_DRIFT`: bytes changed without a classified schema/semantic/capability/authority impact, including representation-only changes.
- `SCHEMA_DRIFT`: `$schema` or `schema_version` changed.
- `SEMANTIC_DRIFT`: contract meaning changed.
- `CAPABILITY_DRIFT`: ARK capability, tier implementation, or MRS capability surface changed.
- `AUTHORITY_DRIFT`: epistemic entitlement, provenance, boundary, authority, or canonicality changed.
- `BREAKING_DRIFT`: a known fail-closed composition guard was weakened or removed.
- `SOURCE_UNAVAILABLE`: live parent evidence could not be established.

An artifact may expose multiple detected classes. `primary_class` is the highest-impact deterministic classification, while `detected_classes` retains the other applicable classes. A changed byte is therefore not automatically breaking semantic drift.

Unknown impact is not guessed into compatibility. It produces `INT_DRIFT_CLASSIFICATION_UNRESOLVED` plus review-required status.

## Typed outcomes

The CLI emits the requested INT outcomes: `INT_OK`, `INT_PARENT_DRIFT_DETECTED`, `INT_PARENT_SOURCE_UNAVAILABLE`, `INT_PARENT_SNAPSHOT_INVALID`, `INT_PARENT_RECEIPT_MISMATCH`, `INT_PARENT_CONTRACT_MISSING`, `INT_DRIFT_CLASSIFICATION_UNRESOLVED`, `INT_BREAKING_DRIFT`, and `INT_REVIEW_REQUIRED` as a status code when drift requires review.

Non-zero process status means the live state was not accepted as an unchanged compatible baseline.

## Determinism and CI

Machine reports use sorted, compact canonical JSON and contain no generation timestamp. Live commit identity is evidence, not a clock value.

CI does not depend on live GitHub availability. It validates snapshot receipts and runs deterministic regression tests for every drift class, malformed snapshots, receipt mismatch, missing contracts, source unavailability, implementation drift, and unresolved impact. Breaking and unresolved cases are asserted to fail closed.

PR #3 compatibility remains scoped to exact pinned parent evidence. PR #2 can prove that live parents differ from that evidence; it does not automatically prove the changed parents compatible.
