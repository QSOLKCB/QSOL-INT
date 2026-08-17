# qBraid / Haiku Founding Design Review

The supplied report bundle gave QSOL-INT its useful three-layer framing: SUBSTRATE asks what is known and why; ARK asks whether it survives; INT asks how the two compose.

The report is retained as non-canonical design input rather than imported as truth.

## Byte observation

Observed bundle SHA-256: `745a62a5360165f019ea4e2195eee5fac8c6f3eb9eeeb07916934611d253fd68`.

This establishes byte identity against the supplied digest. It is not a digital signature and does not independently authenticate an author.

## Preserved findings

1. T0-T5 contains six tier IDs, although the report calls them five tiers.
2. ARK MRS is capability-based; tier rank is not a mandatory execution sequence and capabilities are not inherited implicitly.
3. SHA-256 digest matching does not prove authorship, origin, signature, trustworthiness, or claim truth.
4. The ZIP contains 9 files while internal `SHA256SUMS` covers 6, despite verification prose saying all 9 should verify.
5. “Phase 1 complete / production ready” is treated as design-report language, not repository implementation evidence.

The mistakes stay recorded because exposing exactly this kind of cross-system overclaim is QSOL-INT's job.
