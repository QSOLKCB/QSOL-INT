# Adapters and Integration Fixtures

QSOL-INT adapters translate one canonical integration envelope into transport templates. They do not redefine truth, provenance, epistemic state, claim maturity, register, scenario, mode boundaries, ARK capabilities, or parent drift.

## Commands

```bash
./int validate-adapters
./int adapt --adapter generic --input adapters/fixtures/valid.json
./int adapt --adapter openai --input adapters/fixtures/unknown.json --json
./int adapt --adapter ollama --input adapters/fixtures/drift.json --json
```

The standard-library implementation is `tools/adapt.py`.

## Canonical envelope

An adapter envelope contains:

- messages;
- epistemic state;
- claim maturity;
- scenario;
- register;
- provenance;
- mode and bridge state;
- drift and review state.

Known, retrieved, inferred, and conflicting claims require provenance. Conflict requires at least two source records. Material cross-domain inference without a declared bridge is blocked. Any non-`NO_DRIFT` status must remain review-required.

## Implemented adapters

### Generic JSON

Preserves messages and the complete `qsol_int` annotation object in a deterministic JSON payload.

### OpenAI-compatible template

Emits a request template with:

- `REPLACE_WITH_EXACT_MODEL_ID` as an explicit runtime placeholder;
- a developer message containing the canonical annotation JSON;
- the original messages unchanged;
- SHA-256 serialization receipts in metadata;
- no API key.

This is a transport template, not a claim that a particular SDK or hosted endpoint was invoked.

### Ollama template

Emits a request template with:

- `REPLACE_WITH_EXACT_MODEL_TAG` as an explicit runtime placeholder;
- the canonical annotation JSON in the system context;
- the original messages unchanged;
- no claim that a local model was created or run.

## Fixture matrix

The committed fixture suite covers:

- valid;
- invalid;
- unknown;
- conflict;
- satire;
- cross-mode;
- missing provenance;
- parent drift.

Each fixture is checked against all three adapters. `adapters/reports/conformance.json` contains 24 deterministic adapter-fixture results and remains a derived, non-canonical artifact.

## Receipt semantics

Adapter hashes establish serialization identity relative to the compared bytes. They do not establish truth, authorship, original source, signature, trustworthiness, current-parent compatibility, or execution.
