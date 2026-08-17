# Cross-Repo Composition Batteries and Compatibility Reports

PR #3 turns QSOL-INT's composition rules into deterministic executable paperwork.

## Scope

The batteries validate composition against the **exact pinned parent evidence** recorded by PR #1.

They do not claim that the current live heads of QSOL-SUBSTRATE and QSOL-ARK remain compatible. That requires PR #2 drift detection.

Therefore a valid report may say:

```text
pinned compatibility: compatible
live parent freshness: untested
```

This is deliberate.

## Run

```bash
python3 tools/run_batteries.py
python3 tools/run_batteries.py --json
python3 tools/run_batteries.py --write-report compatibility/reports/pinned-bootstrap.json
python3 tools/run_batteries.py --validate-report compatibility/reports/pinned-bootstrap.json
```

## Battery set

| ID | Battery | Required behavior |
|---|---|---|
| INT-BAT-001 | provenance retention | provenance and visibility survive recovery |
| INT-BAT-002 | unknown preservation | `unknown` remains `unknown` |
| INT-BAT-003 | conflict preservation | material conflict remains visible |
| INT-BAT-004 | satire/register preservation | `SATIRICAL` remains `SATIRICAL` |
| INT-BAT-005 | cross-mode boundary | material cross-domain inference without a bridge is blocked |
| INT-BAT-006 | recovery without authority escalation | successful recovery does not strengthen state or maturity |
| INT-BAT-007 | perfect hash without evidence escalation | digest success proves bytes, not authorship or truth |
| INT-BAT-008 | capability invention | undeclared ARK capability requests are rejected |
| INT-BAT-009 | stale-parent guard | live compatibility remains `untested` without drift evidence |

All case payloads are synthetic integration fixtures. They are tests of QSOL-INT behavior, not historical or empirical evidence.

## Compatibility states

Reports use exactly four compatibility states:

- `compatible`
- `incompatible`
- `untested`
- `unknown`

Version adjacency never implies compatibility.

`compatible` is always scoped. In PR #3 the scope is `pinned_parent_evidence_only`.

## Deterministic report identity

A compatibility report binds exact parent repositories, exact pinned parent commits, exact parent manifest/contract Git blob identities, exact battery index/version, all case results, and a SHA-256 fingerprint over canonical JSON.

The fingerprint is report integrity. It is not parent authorship, signature, or truth.

## PR #2 boundary

PR #3 deliberately does not implement `./int check-drift` or `./int explain-drift`.

Until PR #2 exists, current live-parent freshness is `untested`. This prevents a pinned compatibility result from silently becoming a claim about moving upstream repositories.

## Core invariant

> **Perfect preservation must never increase epistemic authority.**
