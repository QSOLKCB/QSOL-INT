# PR #3 Agent Rules

Machine-facing constraints for cross-repo composition evaluation:

1. Battery fixtures are synthetic integration tests, not source evidence.
2. `compatible` is meaningless without its declared scope.
3. PR #3 compatibility is scoped to `pinned_parent_evidence_only`.
4. Live parent freshness remains `untested` until PR #2 drift tooling exists.
5. Never infer compatibility from version adjacency.
6. Never strengthen epistemic state or claim maturity because recovery or hashing succeeded.
7. Preserve provenance, visibility, unknown, conflict, register, and scenario annotations when a fixture requires them.
8. Block material cross-mode inference when no bridge is declared.
9. Reject requested ARK capabilities absent from the pinned registry.
10. Compatibility reports are derived receivers and never become parent authority.
11. Report fingerprinting proves report-byte identity against the report contents only.
12. If parent identity cannot be established exactly, do not emit `compatible`.
