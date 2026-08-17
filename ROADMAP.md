# QSOL-INT Roadmap

QSOL-INT is built around two rules:

- **INTEGRATION_MUST_NOT_INCREASE_SEMANTIC_AUTHORITY**
- **AUTHORED_RECEIVER != SOURCE_EVIDENCE**

## PR #1 — Bootstrap and clean the founding design

- [x] Preserve the SUBSTRATE / ARK / INT three-layer framing.
- [x] Replace fixed epistemic-state-to-tier mapping with capability-based composition.
- [x] Pin current SUBSTRATE and ARK contract evidence.
- [x] Record parent semantic ownership explicitly.
- [x] Separate digest integrity from authenticity, authorship, signature, and truth.
- [x] Record the qBraid/Haiku bundle as non-canonical design input.
- [x] Preserve tier-count, MRS, hash-language, receipt-coverage, and implementation-status discrepancies as findings.
- [x] Adopt the `substratism` fixture/receiver discipline as a non-canonical methodology reference.
- [x] Add `AUTHORED_RECEIVER != SOURCE_EVIDENCE` to the integration boundary.
- [x] Add human, AI, and agent entrypoints.
- [x] Add core JSON schemas.
- [x] Add stdlib-only local validator and regression tests.
- [x] Add CI for local contract validation.

## PR #2 — Parent snapshot and drift tooling

- [ ] Deterministically snapshot selected public parent contracts with repository, commit, path, Git blob identity, and content SHA-256.
- [ ] Add live-vs-pinned comparison with typed `INT_PARENT_DRIFT`.
- [ ] Separate harmless additive changes from compatibility-relevant changes.
- [ ] Detect SUBSTRATE epistemic/maturity/scenario/register/mode/source-policy changes.
- [ ] Detect ARK tier/implementation/capability/MRS changes.
- [ ] Produce canonical JSON drift reports.
- [ ] Preserve offline validation when network access is absent.

## PR #3 — Composition validator and specimens

- [ ] Preserve SUBSTRATE annotations and provenance closure across recovery.
- [ ] Validate requested recovery capabilities against ARK.
- [ ] Delegate tier selection to ARK MRS semantics.
- [ ] Verify recovery never strengthens epistemic state or maturity.
- [ ] Add source-fixture vs INT-authored-receiver specimens.
- [ ] Add mixed-state, cross-mode, receipt, authority-escalation, capability-invention, and stale-parent tests.

## PR #4 — Compatibility matrix and release discipline

- [ ] Bind compatibility records to exact parent commits and contract hashes.
- [ ] Separate `compatible`, `incompatible`, `untested`, and `unknown`.
- [ ] Never infer compatibility from version adjacency.
- [ ] Add deterministic release manifests, checksums, and clean-room verification.

## PR #5 — T5 integration after ARK implements T5

- [ ] Do not implement or emulate T5 ahead of ARK.
- [ ] Consume ARK's real model-reconstruction contract when it exists.
- [ ] Preserve SUBSTRATE annotations through staged reconstruction.
- [ ] Score integration-specific failures separately from ARK recovery score.

## Future

As ARK gains cultural, ancient-system, and ancient-network preservation layers, INT should compose them with SUBSTRATE provenance/mode policy without turning reconstruction or authored receivers into canonical historical fact.

## Deferred

Remote service; database dependency; vector DB as canonical INT state; model-specific latent canonical state; automatic mutation of parent repos; any claim that a hash alone authenticates a person or organization.
