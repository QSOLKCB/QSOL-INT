# SPDX-License-Identifier: Apache-2.0
import copy
import hashlib
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("run_batteries", ROOT / "tools" / "run_batteries.py")
mod = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(mod)

class CompositionBatteryTests(unittest.TestCase):
    def test_all_nine_cases_pass(self):
        report = mod.run()
        self.assertEqual(report["compatibility"], "compatible")
        self.assertEqual(report["live_parent_freshness"], "untested")
        self.assertEqual(report["summary"]["passed"], 9)
        self.assertEqual(report["summary"]["failed"], 0)

    def test_report_validates_and_is_fingerprinted(self):
        report = mod.run()
        mod.validate_report(report)
        self.assertEqual(len(report["fingerprint_sha256"]), 64)

    def test_current_parent_compatibility_is_not_claimed(self):
        report = mod.run()
        self.assertTrue(report["summary"]["requires_live_drift_check_for_current_parent_claim"])
        self.assertEqual(report["scope"], "pinned_parent_evidence_only")

    def test_capability_invention_is_rejected(self):
        parents = mod.load("ai/parent-contracts.json")
        case = mod.load("batteries/cases/capability-invention.json")
        result = mod.evaluate_case(case, parents)
        self.assertEqual(result["result"], "pass")
        self.assertEqual(result["observed"]["decision"], "reject")
        self.assertEqual(result["observed"]["failure_code"], "INT_CAPABILITY_INVENTION")
        self.assertIn("teleport_semantic_state", result["observed"]["invented_capabilities"])

    def test_stale_parent_guard_is_untested_not_compatible(self):
        parents = mod.load("ai/parent-contracts.json")
        case = mod.load("batteries/cases/stale-parent.json")
        result = mod.evaluate_case(case, parents)
        self.assertEqual(result["observed"]["compatibility"], "untested")
        self.assertTrue(result["observed"]["requires_review"])

    def test_perfect_hash_does_not_upgrade_unknown(self):
        parents = mod.load("ai/parent-contracts.json")
        case = mod.load("batteries/cases/perfect-hash-no-evidence-strength.json")
        self.assertEqual(mod.evaluate_case(case, parents)["result"], "pass")

    def test_cross_mode_without_bridge_is_blocked(self):
        parents = mod.load("ai/parent-contracts.json")
        case = mod.load("batteries/cases/cross-mode-boundary.json")
        result = mod.evaluate_case(case, parents)
        self.assertEqual(result["observed"]["decision"], "block")
        self.assertEqual(result["observed"]["failure_code"], "INT_CROSS_MODE_BRIDGE_REQUIRED")

    def test_report_parent_identity_is_exact(self):
        report = mod.run()
        bad = copy.deepcopy(report)
        bad["parents"]["ark"]["pinned_commit"] = "0" * 40
        unsigned = dict(bad)
        unsigned.pop("fingerprint_sha256", None)
        bad["fingerprint_sha256"] = hashlib.sha256(mod.canonical_bytes(unsigned)).hexdigest()
        with self.assertRaisesRegex(ValueError, "INT_COMPATIBILITY_REPORT_INVALID"):
            mod.validate_report(bad)

    def test_report_fingerprint_detects_mutation(self):
        report = mod.run()
        report["compatibility"] = "unknown"
        with self.assertRaisesRegex(ValueError, "INT_COMPATIBILITY_REPORT_INVALID"):
            mod.validate_report(report)

    def test_report_case_results_are_recomputed(self):
        report = mod.run()
        bad = copy.deepcopy(report)
        bad["case_results"][0] = {
            "id": "INT-BAT-008",
            "battery": "totally_legit_paperwork",
            "result": "pass",
            "observed": {"decision": "allow", "failure_code": None},
        }
        unsigned = dict(bad)
        unsigned.pop("fingerprint_sha256", None)
        bad["fingerprint_sha256"] = hashlib.sha256(mod.canonical_bytes(unsigned)).hexdigest()
        with self.assertRaisesRegex(ValueError, "INT_COMPATIBILITY_REPORT_INVALID"):
            mod.validate_report(bad)

    def test_empty_composition_contract_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "INT_COMPOSITION_CONTRACT_INVALID"):
            mod.validate_composition_contract({})

    def test_ark_capability_registry_is_exactly_bound(self):
        parents = mod.load("ai/parent-contracts.json")
        bad = copy.deepcopy(parents)
        bad["parents"]["ark"]["observed_declared_capabilities"].append("time_travel")
        with self.assertRaisesRegex(ValueError, "INT_CAPABILITY_REDEFINITION"):
            mod.validate_battery_parents(bad)

    def test_hash_battery_checks_every_authority_dimension(self):
        parents = mod.load("ai/parent-contracts.json")
        case = mod.load("batteries/cases/perfect-hash-no-evidence-strength.json")
        bad = copy.deepcopy(case)
        bad["fixture"]["after"]["claim"]["content_truth"] = "verified"
        result = mod.evaluate_case(bad, parents)
        self.assertEqual(result["result"], "fail")
        self.assertEqual(result["observed"]["failure_code"], "INT_AUTHORITY_ESCALATION")

    def test_hash_battery_rejects_undeclared_authority_fields(self):
        parents = mod.load("ai/parent-contracts.json")
        case = mod.load("batteries/cases/perfect-hash-no-evidence-strength.json")
        bad = copy.deepcopy(case)
        bad["fixture"]["after"]["claim"]["divine_truth"] = True
        with self.assertRaisesRegex(ValueError, "INT_BATTERY_CASE_INVALID"):
            mod.evaluate_case(bad, parents)

if __name__ == "__main__":
    unittest.main()
