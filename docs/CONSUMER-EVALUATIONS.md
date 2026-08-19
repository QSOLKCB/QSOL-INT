# Consumer Evaluations

QSOL-INT consumer evaluations measure one narrow thing: whether a structured consumer run preserves the integration rules encoded by the exact committed fixtures and pinned parent evidence.

They do not measure general intelligence, factual truth, safety in every domain, or broad model quality.

## Commands

```bash
./int validate-evaluations
./int evaluate --run evaluations/runs/synthetic-conformant.json
./int evaluate --run evaluations/runs/synthetic-conformant.json --json
./int compare-evaluations \
  --left evaluations/reports/synthetic-conformant.json \
  --right evaluations/reports/synthetic-adversarial.json
```

The implementation is standard-library only:

```bash
python3 tools/evaluate_consumer.py validate-evaluations
python3 tools/evaluate_consumer.py evaluate --run <run.json> --output <report.json>
python3 tools/evaluate_consumer.py compare-evaluations --left <a.json> --right <b.json>
```

## Identity binding

Every run must declare:

- the canonical SHA-256 of `evaluations/index.json`;
- the canonical SHA-256 of the exact pinned parent evidence identity;
- an execution kind;
- whether execution is actually claimed;
- a subject identity whose authentication status remains explicit.

Comparisons fail closed unless both reports use byte-identical fixture and parent-evidence identities.

## Metrics

Positive scores range from 0 to 100:

- provenance retention;
- unknown preservation;
- conflict preservation;
- register and satire preservation;
- MRS interpretation;
- mode-boundary discipline.

The invented-history penalty ranges from 0 to 100, where lower is better.

The overall score is the integer average of the six positive scores minus the invented-history penalty, clamped at zero. The formula is deterministic and intentionally simple.

## Synthetic reference runs

`evaluations/runs/synthetic-conformant.json` and `evaluations/runs/synthetic-adversarial.json` are authored conformance fixtures. They set:

```text
execution_kind = synthetic_conformance
claims_execution = false
```

They do not claim that a model or agent actually ran. Their committed reports and comparison are deterministic regression artifacts.

## Authority boundary

Consumer inputs, run manifests, scores, reports, comparisons, and fingerprints are derived INT artifacts. They do not become QSOL-SUBSTRATE evidence, QSOL-ARK execution receipts, or proof of a model's general capability.
