# QSOL-INT Architecture

QSOL-INT composes two independent parent protocols without becoming an authority over either one.

```text
QSOL-SUBSTRATE                         QSOL-ARK
(epistemics / provenance)              (recovery / portability)
        |                                   |
        +----------------+------------------+
                         |
                         v
                     QSOL-INT
              composition / compatibility
                         |
                         v
               auditable integration result
```

## Semantic ownership

QSOL-SUBSTRATE owns epistemic states, claim maturity, scenario/register annotation, modes/bridges, source policy, evidence entitlement, and public-boundary semantics.

QSOL-ARK owns recovery tiers, explicit tier capabilities, implementation flags, Minimum Recoverable Substrate selection, and recovery behavior.

QSOL-INT owns only cross-protocol composition, compatibility evidence, drift detection, and integration-specific validation.

## Correct recovery composition

A SUBSTRATE state such as `known`, `unknown`, or `fiction` is semantic evidence. It is not an ARK capability request. Fixed mappings such as `known -> T1` are forbidden.

Instead: preserve SUBSTRATE annotations; identify the task requirement; translate only requirements that correspond to capabilities explicitly declared by ARK; delegate selection to ARK MRS; perform INT-specific checks separately; never upgrade claim entitlement because recovery succeeded.

Example: an `unknown` claim may still have its exact record bytes verified with `verify_sha256`. Successful byte verification does not change `unknown` into `known`.

## Parent freshness

Online, live parent repository state owns parent semantics. Offline, pinned snapshots are last-known evidence and must retain commit identity. Material live-versus-pinned divergence becomes drift and requires compatibility re-evaluation.

## Integration receivers

Borrowing a useful discipline from the `substratism` reference implementation, INT distinguishes **source fixtures** from **authored receivers**. A visualization, mapping, score, reconstruction, or deterministic transformation may explain parent evidence but does not become parent evidence.

`AUTHORED_RECEIVER != SOURCE_EVIDENCE`
