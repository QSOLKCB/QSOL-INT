# SPDX-License-Identifier: Apache-2.0
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_int", ROOT / "tools" / "validate_int.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class IntBootstrapTests(unittest.TestCase):
    def assertCode(self, code, fn, *args, **kwargs):
        with self.assertRaisesRegex(ValueError, f"^{code}$"):
            fn(*args, **kwargs)

    def test_full_validation(self):
        mod.validate()

    def test_epistemic_state_never_forces_fixed_tier(self):
        policy = mod.load("ai/epistemic-recovery-policy.json")
        self.assertIs(policy["state_forces_fixed_ark_tier"], False)
        self.assertIs(policy["ark_selection"]["rank_is_not_execution_sequence"], True)

    def test_capability_examples_are_declared_by_ark(self):
        parents = mod.load("ai/parent-contracts.json")
        declared = set(parents["parents"]["ark"]["observed_declared_capabilities"])
        policy = mod.load("ai/epistemic-recovery-policy.json")
        for example in policy["current_capability_translation_examples"]:
            self.assertTrue(set(example["ark_capabilities"]).issubset(declared))

    def test_digest_semantics_do_not_claim_signature_or_truth(self):
        invariants = set(mod.load("ai/integrity-semantics.json")["invariants"])
        self.assertIn("sha256_digest_is_not_a_digital_signature", invariants)
        self.assertIn("digest_match_does_not_prove_content_truth", invariants)

    def test_qbraid_receipt_gap_is_preserved_as_evidence(self):
        source = mod.load("specimens/qbraid-foundation/source-manifest.json")
        self.assertEqual(source["bundle"]["archive_entry_count"], 9)
        self.assertEqual(source["bundle"]["receipt_entry_count"], 6)
        self.assertFalse(source["bundle"]["receipt_covers_all_archive_entries"])

    def test_substratism_receiver_rule_is_noncanonical_reference(self):
        ref = mod.load("ai/reference-methodologies.json")["references"][0]
        self.assertFalse(ref["canonical_for_int"])
        self.assertFalse(ref["parent_protocol"])
        self.assertEqual(ref["int_translation"]["invariant"], "AUTHORED_RECEIVER != SOURCE_EVIDENCE")

    def test_empty_supplied_contracts_fail_closed(self):
        self.assertCode("INT_PARENT_CONTRACT_INCOMPLETE", mod.validate_parent_contracts, {})
        self.assertCode("INT_PARENT_CONTRACT_INCOMPLETE", mod.validate_integration, {})
        self.assertCode("INT_PARENT_CONTRACT_INCOMPLETE", mod.validate_policy, {})
        self.assertCode("INT_INTEGRITY_SEMANTICS_INVALID", mod.validate_integrity, {})
        self.assertCode(
            "INT_QBRAID_SPECIMEN_INVALID",
            mod.validate_qbraid,
            {},
            mod.load("specimens/qbraid-foundation/findings.json"),
        )
        self.assertCode("INT_REFERENCE_METHODOLOGY_INVALID", mod.validate_references, {})

    def test_parent_artifact_identities_are_bound(self):
        parents = mod.load("ai/parent-contracts.json")
        broken_manifest = copy.deepcopy(parents)
        broken_manifest["parents"]["substrate"]["manifest"]["git_blob_sha1"] = "broken"
        self.assertCode("INT_PARENT_CONTRACT_INCOMPLETE", mod.validate_parent_contracts, broken_manifest)

        wrong_but_well_formed = copy.deepcopy(parents)
        wrong_but_well_formed["parents"]["ark"]["contracts"][0]["git_blob_sha1"] = "0" * 40
        self.assertCode("INT_PARENT_CONTRACT_INCOMPLETE", mod.validate_parent_contracts, wrong_but_well_formed)

    def test_qbraid_findings_are_bound_to_source(self):
        source = mod.load("specimens/qbraid-foundation/source-manifest.json")
        findings = mod.load("specimens/qbraid-foundation/findings.json")
        findings["source_id"] = "source.unrelated"
        self.assertCode("INT_QBRAID_SPECIMEN_INVALID", mod.validate_qbraid, source, findings)

    def test_composition_rules_cannot_be_removed(self):
        contract = mod.load("ai/integration-contract.json")
        contract["composition_rules"].remove("recovery_success_does_not_upgrade_epistemic_state_or_claim_maturity")
        self.assertCode("INT_PARENT_CONTRACT_INCOMPLETE", mod.validate_integration, contract)

    def test_substrate_preservation_fields_are_mandatory(self):
        policy = mod.load("ai/epistemic-recovery-policy.json")
        policy["substrate_fields_to_preserve"].remove("provenance")
        self.assertCode("INT_PARENT_CONTRACT_INCOMPLETE", mod.validate_policy, policy)

    def test_required_cryptographic_wording_is_canonical(self):
        integrity = mod.load("ai/integrity-semantics.json")
        integrity["required_wording"]["sha256_match"] = "SHA-256 proves authorship and truth"
        self.assertCode("INT_INTEGRITY_SEMANTICS_INVALID", mod.validate_integrity, integrity)

    def test_manifest_entrypoints_are_validated(self):
        manifest = mod.load("manifest.json")
        manifest["entrypoints"]["integration_contract"] = "ai/does-not-exist.json"
        self.assertCode("INT_MANIFEST_ENTRYPOINT_INVALID", mod.validate, manifest)

    def test_reference_patterns_are_allowlisted(self):
        refs = mod.load("ai/reference-methodologies.json")
        refs["references"][0]["adopted_patterns"] = ["import_moral_claims_as_int_truth"]
        self.assertCode("INT_REFERENCE_METHODOLOGY_INVALID", mod.validate_references, refs)

    def test_qbraid_receipt_coverage_uses_declared_failure_code(self):
        source = mod.load("specimens/qbraid-foundation/source-manifest.json")
        findings = mod.load("specimens/qbraid-foundation/findings.json")
        source["receipt_entries"] = list(source["archive_entries"])
        source["bundle"]["receipt_entry_count"] = len(source["receipt_entries"])
        self.assertCode(
            "INT_QBRAID_RECEIPT_COVERAGE_MISMATCH",
            mod.validate_qbraid,
            source,
            findings,
        )

    def test_qbraid_duplicate_archive_and_receipts_fail(self):
        findings = mod.load("specimens/qbraid-foundation/findings.json")

        source = mod.load("specimens/qbraid-foundation/source-manifest.json")
        source["archive_entries"][-1] = source["archive_entries"][0]
        self.assertCode("INT_QBRAID_SPECIMEN_INVALID", mod.validate_qbraid, source, findings)

        source = mod.load("specimens/qbraid-foundation/source-manifest.json")
        source["receipt_entries"][-1] = source["receipt_entries"][0]
        self.assertCode("INT_QBRAID_SPECIMEN_INVALID", mod.validate_qbraid, source, findings)


if __name__ == "__main__":
    unittest.main()
