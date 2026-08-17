# QSOL-INT

**QSOL-SUBSTRATE knows. QSOL-ARK survives. QSOL-INT makes sure the handoff does not lie.**

QSOL-INT is the vendor-neutral integration layer between:

- **QSOL-SUBSTRATE** — public context, epistemic state, provenance, modes, source policy, and claim entitlement;
- **QSOL-ARK** — deterministic recovery, constrained-environment verification, Minimum Recoverable Substrate (MRS), and future model reconstruction;
- **QSOL-INT** — composition rules that preserve each parent's authority while detecting drift, overclaiming, and integration breakage.

QSOL-INT is **not** a third knowledge base and does not redefine either parent protocol.

## Core composition rule

A SUBSTRATE epistemic state does **not** directly select an ARK tier. INT preserves SUBSTRATE annotations, derives only task-required recovery capabilities, and delegates tier selection to ARK MRS. ARK ranks are not a mandatory execution sequence and capabilities are never invented or inherited implicitly.

## Two invariants

```text
INTEGRATION_MUST_NOT_INCREASE_SEMANTIC_AUTHORITY
AUTHORED_RECEIVER != SOURCE_EVIDENCE
```

The second invariant is adopted methodologically from `QSOLKCB/substratism`, whose deterministic visual/sonification receivers explicitly remain explanatory projections rather than evidence for the underlying research claim. In INT, parent contracts are source fixtures; INT mappings, visualizations, reports, scores, and reconstructions are authored receivers unless a parent contract says otherwise.

`substratism` is a reference methodology only — **not** a parent protocol and not canonical INT authority.

## Integrity is not authenticity

QSOL-INT separates digest match, integrity, provenance, authorship, authentication/signature, and content truth. SHA-256 alone does not prove authorship, original source, signature, trustworthiness, or truth.

## Founding qBraid specimen

The supplied qBraid/Haiku bundle is retained as non-canonical design input. Its observed master SHA-256 is:

`745a62a5360165f019ea4e2195eee5fac8c6f3eb9eeeb07916934611d253fd68`

PR #1 preserves five useful discrepancies as machine-readable findings: T0-T5 miscounted as five tiers; sequential-ladder semantics stronger than ARK MRS; SHA-256 overclaiming; 9 archive entries versus 6 internal receipts; and design-report implementation status presented more strongly than repository evidence supported.

## Parent pins at bootstrap

- QSOL-SUBSTRATE `main`: `60e8cfeefa859df375f9f4d2fdb735edb1249db8`
- QSOL-ARK `main`: `f2bbf149abb3f8ccbfed158176873d813b66b546`
- methodology reference `substratism`: `7ba38cf90ca52298aed3819b30f4098f49b36813`

Pins are offline evidence, not eternal authority. Live parent state may supersede stale pins.

## Validate

```sh
python3 tools/validate_int.py
python3 -m unittest discover -s tests -v
```

Local bootstrap validation is standard-library only and requires no network access.

See `README4AI.md`, `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/QBRAID-REVIEW.md`, `docs/SUBSTRATISM-REFERENCE.md`, and `ROADMAP.md`.
