# SPDX-License-Identifier: Apache-2.0
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_int", ROOT / "tools" / "validate_int.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)


class IntBootstrapTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
