# QSOL-INT

**QSOL-SUBSTRATE knows. QSOL-ARK survives. QSOL-INT makes sure the handoff does not lie.**

QSOL-INT is the vendor-neutral integration layer between:

- **QSOL-SUBSTRATE**: public context, epistemic state, provenance, modes, source policy, and claim entitlement;
- **QSOL-ARK**: deterministic recovery, constrained-environment verification, Minimum Recoverable Substrate (MRS), and future model reconstruction;
- **QSOL-INT**: composition rules that preserve each parent's authority while detecting drift, overclaiming, transport loss, and integration breakage.

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

`QSOLKCB/substratism` is a reference methodology only, not a parent protocol and not canonical INT authority. Its useful pattern is fixture/receiver separation: deterministic project-authored projections remain explanations rather than evidence for the underlying source claim.

## Integrity is not authenticity

QSOL-INT separates digest match, integrity, provenance, authorship, authentication/signature, and content truth. SHA-256 alone does not prove authorship, original source, signature, trustworthiness, or truth.

## Parent snapshots and live drift

INT keeps byte-exact copies of only the SUBSTRATE and ARK machine contracts it currently depends on. Every snapshot artifact records parent repository, source commit, contract path, Git blob identity, and content SHA-256. Aggregate semantic snapshot identity excludes generation timestamps.

The snapshot is last-known evidence, not superior authority. Live parent state wins for parent-owned semantics, and drift never refreshes the baseline automatically.

```bash
./int check-drift
./int check-drift --json
./int explain-drift
```

Drift classes are `NO_DRIFT`, `CONTENT_DRIFT`, `SCHEMA_DRIFT`, `SEMANTIC_DRIFT`, `CAPABILITY_DRIFT`, `AUTHORITY_DRIFT`, `BREAKING_DRIFT`, and `SOURCE_UNAVAILABLE`. A changed byte is not automatically breaking semantic drift. Unknown impact produces review-required unresolved classification rather than optimistic compatibility.

See `docs/DRIFT.md` for outcome codes and classification details.

## Parent pins at bootstrap

- QSOL-SUBSTRATE `main`: `60e8cfeefa859df375f9f4d2fdb735edb1249db8`
- QSOL-ARK `main`: `f2bbf149abb3f8ccbfed158176873d813b66b546`
- methodology reference `substratism`: `7ba38cf90ca52298aed3819b30f4098f49b36813`

Pins are offline evidence, not eternal authority. Live parent state may supersede stale pins.

## Cross-repo composition batteries

```bash
python3 tools/run_batteries.py
python3 tools/run_batteries.py --json
python3 tools/run_batteries.py --validate-report compatibility/reports/pinned-bootstrap.json
```

The deterministic battery suite covers provenance retention; unknown preservation; conflict preservation; satire/register preservation; cross-mode bridge discipline; recovery without authority escalation; perfect-hash without evidence escalation; ARK capability invention; and stale-parent/freshness discipline.

The committed compatibility report remains intentionally scoped:

```text
pinned compatibility: compatible
current-parent compatibility: NOT CLAIMED
```

Drift detection does not automatically establish compatibility with changed parent contracts. The committed compatibility report is a derived integration artifact, fingerprinted over canonical JSON and bound to exact parent commits and Git blob identities.

## Consumer evaluations

Consumer evaluations score structured run manifests against seven deterministic synthetic fixtures:

```bash
./int validate-evaluations
./int evaluate --run evaluations/runs/synthetic-conformant.json
./int evaluate --run evaluations/runs/synthetic-conformant.json --json
./int compare-evaluations \
  --left evaluations/reports/synthetic-conformant.json \
  --right evaluations/reports/synthetic-adversarial.json
```

The metrics are provenance retention, unknown preservation, conflict preservation, register/satire preservation, MRS interpretation, mode-boundary discipline, and an invented-history penalty. Comparisons fail closed unless fixture and parent-evidence identities match exactly.

The committed reference runs are authored synthetic conformance objects. They set `claims_execution: false` and do not claim that a model or agent ran. Reports, comparisons, and scores are derived/non-canonical and measure fixture conformance only.

See `docs/CONSUMER-EVALUATIONS.md`.

## Transport adapters

INT implements generic JSON, OpenAI-compatible, and Ollama transport templates:

```bash
./int validate-adapters
./int adapt --adapter generic --input adapters/fixtures/valid.json
./int adapt --adapter openai --input adapters/fixtures/unknown.json --json
./int adapt --adapter ollama --input adapters/fixtures/drift.json --json
```

Every adapter preserves messages and the full semantic annotation object. Unknown, conflict, satire, cross-mode boundaries, missing provenance, and drift remain visible and fail closed where required. Model identifiers remain explicit runtime placeholders and no API keys are embedded.

`adapters/reports/conformance.json` is a deterministic 24-result matrix over three adapters and eight fixture kinds. Adapter receipts prove serialization identity only.

See `docs/ADAPTERS.md`.

## Founding qBraid specimen

The supplied qBraid/Haiku bundle remains non-canonical design input. Its observed master SHA-256 is:

`745a62a5360165f019ea4e2195eee5fac8c6f3eb9eeeb07916934611d253fd68`

Its preserved discrepancies remain useful integration test material rather than canonical truth.

## Validate

```sh
python3 tools/validate_int.py
python3 tools/drift.py validate-snapshot --json
python3 tools/run_batteries.py
python3 tools/run_batteries.py --validate-report compatibility/reports/pinned-bootstrap.json
python3 tools/evaluate_consumer.py validate-evaluations
python3 tools/evaluate_consumer.py evaluate \
  --run evaluations/runs/synthetic-conformant.json \
  --validate-report evaluations/reports/synthetic-conformant.json
python3 tools/adapt.py validate-adapters \
  --validate-report adapters/reports/conformance.json
python3 -m unittest discover -s tests -v
```

Local validation is standard-library only and requires no network access. Live drift checks use public GitHub parent state and fail closed when that evidence is unavailable.

See `README4AI.md`, `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/COMPOSITION-BATTERIES.md`, `docs/DRIFT.md`, `docs/CONSUMER-EVALUATIONS.md`, `docs/ADAPTERS.md`, `docs/QBRAID-REVIEW.md`, `docs/SUBSTRATISM-REFERENCE.md`, and `ROADMAP.md`.
