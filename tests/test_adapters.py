# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import adapt  # noqa: E402


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index, cls.fixtures = adapt.validate_index()
        cls.by_kind = {
            Path(path).stem: fixture
            for path, fixture, _ in cls.fixtures
        }

    def test_fixture_matrix_covers_every_required_case(self) -> None:
        self.assertEqual(
            set(self.by_kind),
            {
                "valid",
                "invalid",
                "unknown",
                "conflict",
                "satire",
                "cross-mode",
                "missing-provenance",
                "drift",
            },
        )
        self.assertEqual(self.index["adapters"], list(adapt.ADAPTERS))

    def test_all_three_adapters_preserve_valid_semantics(self) -> None:
        fixture = self.by_kind["valid"]
        for adapter in adapt.ADAPTERS:
            with self.subTest(adapter=adapter):
                output = adapt.process(adapter, fixture)
                self.assertEqual(output["decision"], "allow")
                adapt.validate_output(output, fixture)
                self.assertEqual(
                    output["semantic_receipt"]["annotations"],
                    fixture["annotations"],
                )

    def test_unknown_remains_unknown(self) -> None:
        fixture = self.by_kind["unknown"]
        for adapter in adapt.ADAPTERS:
            output = adapt.process(adapter, fixture)
            self.assertEqual(
                output["semantic_receipt"]["annotations"][
                    "epistemic_state"
                ],
                "unknown",
            )

    def test_conflict_remains_visible_with_both_sources(self) -> None:
        fixture = self.by_kind["conflict"]
        output = adapt.process("generic", fixture)
        annotations = output["semantic_receipt"]["annotations"]
        self.assertEqual(annotations["epistemic_state"], "conflict")
        self.assertEqual(len(annotations["provenance"]), 2)

    def test_conflict_requires_distinct_provenance_records(self) -> None:
        fixture = copy.deepcopy(self.by_kind["conflict"])
        repeated = copy.deepcopy(
            fixture["annotations"]["provenance"][0]
        )
        fixture["annotations"]["provenance"] = [
            repeated,
            copy.deepcopy(repeated),
        ]
        output = adapt.process("generic", fixture)
        self.assertEqual(output["decision"], "reject")
        self.assertEqual(
            output["failure_code"],
            "INT_ADAPTER_CONFLICT_PROVENANCE_INCOMPLETE",
        )

    def test_satire_register_is_not_rewritten_as_fact(self) -> None:
        fixture = self.by_kind["satire"]
        output = adapt.process("openai", fixture)
        annotations = output["semantic_receipt"]["annotations"]
        self.assertEqual(annotations["register"], "SATIRICAL")
        self.assertEqual(annotations["epistemic_state"], "fiction")

    def test_cross_mode_without_bridge_is_blocked(self) -> None:
        output = adapt.process("ollama", self.by_kind["cross-mode"])
        self.assertEqual(output["decision"], "block")
        self.assertEqual(
            output["failure_code"],
            "INT_CROSS_MODE_BRIDGE_REQUIRED",
        )

    def test_material_cross_domain_without_secondary_is_blocked(self) -> None:
        fixture = copy.deepcopy(self.by_kind["valid"])
        fixture["annotations"]["mode"].update(
            {
                "material_cross_domain": True,
                "secondary": [],
                "bridges": [],
            }
        )
        output = adapt.process("ollama", fixture)
        self.assertEqual(output["decision"], "block")
        self.assertEqual(
            output["failure_code"],
            "INT_CROSS_MODE_BRIDGE_REQUIRED",
        )

    def test_missing_provenance_is_rejected(self) -> None:
        output = adapt.process(
            "generic",
            self.by_kind["missing-provenance"],
        )
        self.assertEqual(output["decision"], "reject")
        self.assertEqual(
            output["failure_code"],
            "INT_ADAPTER_PROVENANCE_REQUIRED",
        )

    def test_drift_warning_remains_review_required(self) -> None:
        fixture = self.by_kind["drift"]
        output = adapt.process("ollama", fixture)
        drift = output["semantic_receipt"]["annotations"]["drift"]
        self.assertEqual(drift["status"], "AUTHORITY_DRIFT")
        self.assertTrue(drift["review_required"])

    def test_malformed_envelope_is_rejected_with_typed_code(self) -> None:
        output = adapt.process("generic", self.by_kind["invalid"])
        self.assertEqual(output["decision"], "reject")
        self.assertEqual(
            output["failure_code"],
            "INT_ADAPTER_ENVELOPE_INVALID",
        )

    def test_empty_message_role_is_rejected(self) -> None:
        fixture = copy.deepcopy(self.by_kind["valid"])
        fixture["messages"][0]["role"] = ""
        output = adapt.process("generic", fixture)
        self.assertEqual(output["decision"], "reject")
        self.assertEqual(
            output["failure_code"],
            "INT_ADAPTER_ENVELOPE_INVALID",
        )

    def test_semantic_receipt_tampering_is_detected(self) -> None:
        fixture = self.by_kind["valid"]
        original = copy.deepcopy(fixture)
        output = adapt.process("generic", fixture)
        output["semantic_receipt"]["annotations"][
            "epistemic_state"
        ] = "unknown"
        self.assertEqual(fixture, original)
        with self.assertRaisesRegex(
            adapt.AdapterFailure,
            "INT_ADAPTER_SEMANTIC_LOSS",
        ):
            adapt.validate_output(output, fixture)

    def test_transport_payload_is_detached_from_source_fixture(self) -> None:
        fixture = self.by_kind["valid"]
        original = copy.deepcopy(fixture)
        output = adapt.process("generic", fixture)
        output["transport"]["payload"]["messages"][0][
            "content"
        ] = "tampered"
        self.assertEqual(fixture, original)
        with self.assertRaisesRegex(
            adapt.AdapterFailure,
            "INT_ADAPTER_SEMANTIC_LOSS",
        ):
            adapt.validate_output(output, fixture)

    def test_conformance_report_is_complete_and_fingerprinted(self) -> None:
        report = adapt.conformance_report()
        self.assertEqual(report["summary"]["total"], 24)
        self.assertEqual(report["summary"]["passed"], 24)
        self.assertEqual(report["summary"]["failed"], 0)
        adapt.validate_report(report)

    def test_committed_conformance_report_regenerates_exactly(self) -> None:
        report = adapt.load_json(
            "adapters/reports/conformance.json",
            "INT_ADAPTER_REPORT_INVALID",
        )
        adapt.validate_report(report)

    def test_unknown_adapter_is_rejected(self) -> None:
        output = adapt.process("telepathy", self.by_kind["valid"])
        self.assertEqual(
            output["failure_code"],
            "INT_ADAPTER_UNKNOWN",
        )


if __name__ == "__main__":
    unittest.main()
