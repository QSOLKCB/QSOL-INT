# QSOL-INT

**QSOL-SUBSTRATE knows. QSOL-ARK survives. QSOL-INT makes sure the handoff does not lie.**

QSOL-INT is the vendor-neutral integration layer between:

- **QSOL-SUBSTRATE** — public context, epistemic state, provenance, modes, source policy, and claim entitlement;
- **QSOL-ARK** — deterministic recovery, constrained-environment verification, Minimum Recoverable Substrate (MRS), and future model reconstruction;
- **QSOL-INT** — composition rules that preserve each parent's authority while detecting drift, overclaiming, and integration breakage.

QSOL-INT is **not** a third knowledge base and does not redefine either parent protocol.

## Core composition rule

A SUBSTRATE epistemic state does **not** directly select an ARK tier. INT preserves SUBSTRATE annotations, derives only task-required recovery capabilities, and delegates tier selection to ARK MRS. ARK ranks are not a mandatory execution sequence and capabilities are never invented or inherited implicitly.

## Constitutional invariants

```text
INTEGRATION_MUST_NOT_INCREASE_SEMANTIC_AUTHORITY
AUTHORED_RECEIVER != SOURCE_EVIDENCE
DRIFT_IS_NEVER_SILENTLY_ACCEPTED
UNAVAILABLE != CONTRADICTED
PERFECT_PRESERVATION_MUST_NOT_INCREASE_EPISTEMIC_AUTHORITY
```

`QSOLKCB/substratism` is a reference methodology only — **not** a parent protocol and not canonical INT authority. Its useful pattern is fixture/receiver separation: deterministic project-authored projections remain explanations rather than evidence for the underlying source claim.

## Integrity is not authenticity

QSOL-INT separates digest match, integrity, provenance, authorship, authentication/signature, and content truth. SHA-256 alone does not prove authorship, original source, signature, trustworthiness, or truth.

## Parent pins at bootstrap

- QSOL-SUBSTRATE `main`: `60e8cfeefa859df375f9f4d2fdb735edb1249db8`
- QSOL-ARK `main`: `f2bbf149abb3f8ccbfed158176873d813b66b546`
- methodology reference `substratism`: `7ba38cf90ca52298aed3819b30f4098f49b36813`

Pins are offline evidence, not eternal authority. Live parent state may supersede stale pins.

## PR #3 — cross-repo composition batteries

PR #3 makes the integration rules executable.

```bash
python3 tools/run_batteries.py
python3 tools/run_batteries.py --json
python3 tools/run_batteries.py --validate-report compatibility/reports/pinned-bootstrap.json
```

The deterministic battery suite covers provenance retention; unknown preservation; conflict preservation; satire/register preservation; cross-mode bridge discipline; recovery without authority escalation; perfect-hash without evidence escalation; ARK capability invention; and stale-parent/freshness discipline.

A successful PR #3 report is intentionally scoped:

```text
pinned compatibility: compatible
live parent freshness: untested
current-parent compatibility: NOT CLAIMED
```

PR #2 remains responsible for live drift detection. PR #3 does not counterfeit that evidence.

The committed compatibility report is a **derived integration artifact**, fingerprinted over canonical JSON and bound to exact parent commits and Git blob identities.

## Founding qBraid specimen

The supplied qBraid/Haiku bundle remains non-canonical design input. Its observed master SHA-256 is:

`745a62a5360165f019ea4e2195eee5fac8c6f3eb9eeeb07916934611d253fd68`

Its preserved discrepancies remain useful integration test material rather than canonical truth.

## Validate

```sh
python3 tools/validate_int.py
python3 tools/run_batteries.py
python3 tools/run_batteries.py --validate-report compatibility/reports/pinned-bootstrap.json
python3 -m unittest discover -s tests -v
```

Local validation is standard-library only and requires no network access.

See `README4AI.md`, `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/COMPOSITION-BATTERIES.md`, `docs/QBRAID-REVIEW.md`, `docs/SUBSTRATISM-REFERENCE.md`, and `ROADMAP.md`.
