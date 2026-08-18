# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import drift


class DriftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index, cls.baseline = drift.validate_snapshot(
            ROOT / "snapshots" / "parents" / "index.json"
        )

    def provider(
        self,
        mutate=None,
        unavailable=None,
        missing=None,
        advance_commits=True,
    ):
        p = drift.build_fixture_from_snapshot(self.index, self.baseline)
        commits = dict(p.commits)
        artifacts = dict(p.artifacts)
        if advance_commits:
            for repo in commits:
                commits[repo] = (
                    "f" * 40 if commits[repo] != "f" * 40 else "e" * 40
                )
        if mutate:
            repo, path, fn = mutate
            artifacts[(repo, path)] = fn(artifacts[(repo, path)])
        return drift.FixtureProvider(
            commits,
            artifacts,
            unavailable=unavailable,
            missing=missing,
        )

    @staticmethod
    def json_mutator(fn):
        def mutate(data):
            value = json.loads(data.decode())
            fn(value)
            return (
                json.dumps(value, indent=2, ensure_ascii=False) + "\n"
            ).encode()

        return mutate

    def artifact(self, report, parent, path):
        for item in report["parents"]:
            if item["name"] == parent:
                for artifact in item["artifacts"]:
                    if artifact["path"] == path:
                        return artifact
        self.fail(f"missing artifact {parent}:{path}")

    def test_snapshot_receipts_and_git_blob_identities_validate(self):
        self.assertEqual(len(self.baseline), 6)
        self.assertTrue(
            self.index["semantic_identity"]["id"].startswith("sha256:")
        )

    def test_unchanged_contracts_are_no_drift_even_if_parent_commit_advanced(self):
        r = drift.check_drift(self.provider())
        self.assertEqual(r["outcome"], "INT_OK")
        self.assertEqual(r["summary"]["detected_classes"], [drift.NO_DRIFT])

    def test_documentation_or_format_only_change_is_content_drift(self):
        x = drift.classify_artifact(
            "substrate",
            "documentation",
            "docs/example.md",
            b'{"a":1}\n',
            b'{\n  "a": 1\n}\n',
        )
        self.assertEqual(x["primary_class"], drift.CONTENT_DRIFT)
        self.assertTrue(x["classification_resolved"])

    def test_schema_change_is_schema_drift(self):
        m = self.json_mutator(
            lambda v: v.__setitem__("schema_version", "9.0.0")
        )
        r = drift.check_drift(
            self.provider(
                mutate=("QSOLKCB/QSOL-ARK", "manifest.json", m)
            )
        )
        self.assertIn(
            drift.SCHEMA_DRIFT,
            self.artifact(r, "ark", "manifest.json")["detected_classes"],
        )
        self.assertEqual(r["outcome"], "INT_PARENT_DRIFT_DETECTED")

    def test_pointer_matching_does_not_classify_similar_field_names(self):
        def change(value):
            value["schema_version_notes"] = "not a schema version"
            value["authority_notes"] = "not an authority field"

        r = drift.check_drift(
            self.provider(
                mutate=(
                    "QSOLKCB/QSOL-ARK",
                    "manifest.json",
                    self.json_mutator(change),
                )
            )
        )
        artifact = self.artifact(r, "ark", "manifest.json")
        self.assertNotIn(drift.SCHEMA_DRIFT, artifact["detected_classes"])
        self.assertNotIn(drift.AUTHORITY_DRIFT, artifact["detected_classes"])
        self.assertFalse(artifact["classification_resolved"])
        self.assertEqual(
            r["outcome"], "INT_DRIFT_CLASSIFICATION_UNRESOLVED"
        )

    def test_semantic_change_is_semantic_drift(self):
        m = self.json_mutator(
            lambda v: v.__setitem__("failure", "ARK_MRS_REVIEW")
        )
        r = drift.check_drift(
            self.provider(
                mutate=(
                    "QSOLKCB/QSOL-ARK",
                    "ai/minimum-recoverable-substrate.json",
                    m,
                )
            )
        )
        a = self.artifact(
            r, "ark", "ai/minimum-recoverable-substrate.json"
        )
        self.assertEqual(a["primary_class"], drift.SEMANTIC_DRIFT)
        self.assertTrue(a["classification_resolved"])

    def test_ark_implementation_change_is_capability_drift(self):
        def change(value):
            value["tiers"][4]["implemented"] = False

        r = drift.check_drift(
            self.provider(
                mutate=(
                    "QSOLKCB/QSOL-ARK",
                    "ai/recovery-tiers.json",
                    self.json_mutator(change),
                )
            )
        )
        self.assertEqual(
            self.artifact(
                r, "ark", "ai/recovery-tiers.json"
            )["primary_class"],
            drift.CAPABILITY_DRIFT,
        )

    def test_epistemic_entitlement_change_is_authority_drift(self):
        def change(value):
            value["states"]["known"] = "changed entitlement semantics"

        r = drift.check_drift(
            self.provider(
                mutate=(
                    "QSOLKCB/QSOL-SUBSTRATE",
                    "ai/epistemic-contract.json",
                    self.json_mutator(change),
                )
            )
        )
        a = self.artifact(
            r, "substrate", "ai/epistemic-contract.json"
        )
        self.assertEqual(a["primary_class"], drift.AUTHORITY_DRIFT)
        self.assertIn(drift.SEMANTIC_DRIFT, a["detected_classes"])

    def test_structured_rules_shape_is_unresolved_not_exception(self):
        def change(value):
            value["rules"] = [
                {
                    "id": "never_promote_inferred_to_known_without_support",
                    "enabled": True,
                }
            ]

        r = drift.check_drift(
            self.provider(
                mutate=(
                    "QSOLKCB/QSOL-SUBSTRATE",
                    "ai/epistemic-contract.json",
                    self.json_mutator(change),
                )
            )
        )
        a = self.artifact(
            r, "substrate", "ai/epistemic-contract.json"
        )
        self.assertFalse(a["classification_resolved"])
        self.assertNotIn(drift.BREAKING_DRIFT, a["detected_classes"])
        self.assertEqual(
            r["outcome"], "INT_DRIFT_CLASSIFICATION_UNRESOLVED"
        )

    def test_reworded_ark_guard_is_unresolved_not_breaking(self):
        def change(value):
            value["ordering_rule"] = (
                "lower rank means fewer environmental assumptions; "
                "never implicitly inherit capabilities"
            )

        r = drift.check_drift(
            self.provider(
                mutate=(
                    "QSOLKCB/QSOL-ARK",
                    "ai/recovery-tiers.json",
                    self.json_mutator(change),
                )
            )
        )
        a = self.artifact(r, "ark", "ai/recovery-tiers.json")
        self.assertFalse(a["classification_resolved"])
        self.assertNotIn(drift.BREAKING_DRIFT, a["detected_classes"])
        self.assertEqual(a["primary_class"], drift.SEMANTIC_DRIFT)
        self.assertEqual(
            r["outcome"], "INT_DRIFT_CLASSIFICATION_UNRESOLVED"
        )

    def test_structured_guard_removal_is_breaking_drift(self):
        def change(value):
            value["resolution"]["no_authority_escalation"] = False

        r = drift.check_drift(
            self.provider(
                mutate=(
                    "QSOLKCB/QSOL-SUBSTRATE",
                    "ai/mode-contract.json",
                    self.json_mutator(change),
                )
            )
        )
        self.assertEqual(
            self.artifact(
                r, "substrate", "ai/mode-contract.json"
            )["primary_class"],
            drift.BREAKING_DRIFT,
        )
        self.assertEqual(r["outcome"], "INT_BREAKING_DRIFT")
        self.assertIn("INT_REVIEW_REQUIRED", r["status_codes"])

    def test_unknown_impact_is_unresolved_not_optimistically_compatible(self):
        m = self.json_mutator(
            lambda v: v.__setitem__("mystery_contract_switch", True)
        )
        r = drift.check_drift(
            self.provider(
                mutate=("QSOLKCB/QSOL-ARK", "manifest.json", m)
            )
        )
        self.assertFalse(
            self.artifact(
                r, "ark", "manifest.json"
            )["classification_resolved"]
        )
        self.assertEqual(
            r["outcome"], "INT_DRIFT_CLASSIFICATION_UNRESOLVED"
        )

    def test_missing_source_is_source_unavailable_never_no_drift(self):
        r = drift.check_drift(
            self.provider(unavailable={"QSOLKCB/QSOL-ARK"})
        )
        self.assertEqual(r["outcome"], "INT_PARENT_SOURCE_UNAVAILABLE")
        self.assertIn(
            drift.SOURCE_UNAVAILABLE,
            r["summary"]["detected_classes"],
        )
        self.assertIn("INT_REVIEW_REQUIRED", r["status_codes"])

    def test_only_unavailable_sources_do_not_claim_detected_drift(self):
        r = drift.check_drift(
            self.provider(
                unavailable={
                    "QSOLKCB/QSOL-ARK",
                    "QSOLKCB/QSOL-SUBSTRATE",
                }
            )
        )
        self.assertEqual(r["outcome"], "INT_PARENT_SOURCE_UNAVAILABLE")
        self.assertFalse(r["summary"]["drift_detected"])
        self.assertFalse(r["summary"]["classification_resolved"])
        self.assertTrue(r["summary"]["review_required"])
        self.assertEqual(
            r["summary"]["detected_classes"],
            [drift.SOURCE_UNAVAILABLE],
        )

    def test_unavailable_and_breaking_preserve_all_status_codes(self):
        def change(value):
            value["resolution"]["no_authority_escalation"] = False

        r = drift.check_drift(
            self.provider(
                mutate=(
                    "QSOLKCB/QSOL-SUBSTRATE",
                    "ai/mode-contract.json",
                    self.json_mutator(change),
                ),
                unavailable={"QSOLKCB/QSOL-ARK"},
            )
        )
        self.assertEqual(r["outcome"], "INT_PARENT_SOURCE_UNAVAILABLE")
        self.assertTrue(r["summary"]["drift_detected"])
        self.assertIn("INT_PARENT_SOURCE_UNAVAILABLE", r["status_codes"])
        self.assertIn("INT_BREAKING_DRIFT", r["status_codes"])
        self.assertIn("INT_PARENT_DRIFT_DETECTED", r["status_codes"])
        self.assertIn("INT_REVIEW_REQUIRED", r["status_codes"])

    def test_missing_required_contract_has_typed_outcome(self):
        r = drift.check_drift(
            self.provider(
                missing={
                    (
                        "QSOLKCB/QSOL-ARK",
                        "ai/recovery-tiers.json",
                    )
                }
            )
        )
        self.assertEqual(r["outcome"], "INT_PARENT_CONTRACT_MISSING")
        self.assertIn("INT_REVIEW_REQUIRED", r["status_codes"])

    def test_malformed_snapshot_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "index.json"
            bad.write_text("{")
            r = drift.check_drift(self.provider(), index_path=bad)
        self.assertEqual(r["outcome"], "INT_PARENT_SNAPSHOT_INVALID")

    def test_incomplete_snapshot_artifact_fails_before_live_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "snapshots", root / "snapshots")
            index_path = root / "snapshots" / "parents" / "index.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            del index["semantic_identity"]["payload"]["parents"][0][
                "artifacts"
            ][0]["semantic_role"]
            payload = index["semantic_identity"]["payload"]
            index["semantic_identity"]["id"] = (
                "sha256:" + drift.sha256_hex(drift.canonical_json_bytes(payload))
            )
            index_path.write_text(
                json.dumps(index, indent=2) + "\n", encoding="utf-8"
            )
            r = drift.check_drift(
                self.provider(), index_path=index_path
            )
        self.assertEqual(r["outcome"], "INT_PARENT_SNAPSHOT_INVALID")

    def test_snapshot_receipt_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "snapshots", root / "snapshots")
            target = (
                root
                / "snapshots"
                / "parents"
                / "ark"
                / "manifest.json"
            )
            target.write_bytes(target.read_bytes() + b" ")
            r = drift.check_drift(
                self.provider(),
                index_path=root / "snapshots" / "parents" / "index.json",
            )
        self.assertEqual(r["outcome"], "INT_PARENT_RECEIPT_MISMATCH")

    def test_canonical_json_report_is_byte_stable(self):
        r = drift.check_drift(self.provider(advance_commits=False))
        self.assertEqual(
            drift.canonical_report_text(r),
            drift.canonical_report_text(copy.deepcopy(r)),
        )
        self.assertNotIn(
            "generated_at", drift.canonical_report_text(r)
        )

    def test_all_declared_drift_classes_are_regressed(self):
        self.assertEqual(
            set(drift.TAXONOMY),
            {
                drift.NO_DRIFT,
                drift.CONTENT_DRIFT,
                drift.SCHEMA_DRIFT,
                drift.SEMANTIC_DRIFT,
                drift.CAPABILITY_DRIFT,
                drift.AUTHORITY_DRIFT,
                drift.BREAKING_DRIFT,
                drift.SOURCE_UNAVAILABLE,
            },
        )


if __name__ == "__main__":
    unittest.main()
