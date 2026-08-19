# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import evaluate_consumer as evaluator  # noqa: E402


class ConsumerEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index, cls.cases = evaluator.validate_index()
        cls.good_run = evaluator.load_json(
            "evaluations/runs/synthetic-conformant.json"
        )
        cls.bad_run = evaluator.load_json(
            "evaluations/runs/synthetic-adversarial.json"
        )
        cls.good_report = evaluator.evaluate_run(cls.good_run)
        cls.bad_report = evaluator.evaluate_run(cls.bad_run)

    @staticmethod
    def resign(report: dict) -> None:
        unsigned = dict(report)
        unsigned.pop("fingerprint_sha256", None)
        report["fingerprint_sha256"] = evaluator.canonical_sha256(
            unsigned
        )

    def test_index_binds_exact_parent_and_case_identity(self) -> None:
        self.assertEqual(
            self.index["parent_identity_sha256"],
            evaluator.canonical_sha256(
                self.index["parent_identity"]
            ),
        )
        self.assertEqual(len(self.cases), 7)
        self.assertEqual(
            [case["metric"] for case in self.cases],
            list(evaluator.METRIC_ORDER),
        )

    def test_conformant_reference_scores_every_positive_metric(
        self,
    ) -> None:
        self.assertEqual(
            self.good_report["summary"]["overall_score"],
            100,
        )
        self.assertEqual(
            self.good_report["summary"][
                "invented_history_penalty"
            ],
            0,
        )
        for metric in evaluator.POSITIVE_METRICS:
            self.assertEqual(
                self.good_report["metrics"][metric]["score"],
                100,
            )

    def test_adversarial_reference_is_penalized(self) -> None:
        self.assertEqual(
            self.bad_report["summary"]["overall_score"],
            0,
        )
        self.assertEqual(
            self.bad_report["metrics"][
                evaluator.PENALTY_METRIC
            ]["penalty"],
            100,
        )
        self.assertEqual(
            self.bad_report["summary"]["failed_cases"],
            7,
        )

    def test_synthetic_run_cannot_claim_execution(self) -> None:
        run = copy.deepcopy(self.good_run)
        run["claims_execution"] = True
        with self.assertRaisesRegex(
            evaluator.EvaluationFailure,
            "INT_CONSUMER_RUN_INVALID",
        ):
            evaluator.evaluate_run(run)

    def test_model_run_must_claim_execution(self) -> None:
        run = copy.deepcopy(self.good_run)
        run["execution_kind"] = "model_execution"
        run["claims_execution"] = False
        with self.assertRaisesRegex(
            evaluator.EvaluationFailure,
            "INT_CONSUMER_RUN_INVALID",
        ):
            evaluator.evaluate_run(run)

    def test_non_object_fixture_identity_is_typed_invalid(self) -> None:
        for invalid in (None, [], "not-an-object"):
            with self.subTest(value=invalid):
                run = copy.deepcopy(self.good_run)
                run["fixture_identity"] = invalid
                with self.assertRaisesRegex(
                    evaluator.EvaluationFailure,
                    "INT_CONSUMER_RUN_INVALID",
                ):
                    evaluator.evaluate_run(run)

    def test_missing_response_fails_that_metric_without_crashing(
        self,
    ) -> None:
        run = copy.deepcopy(self.good_run)
        run["responses"] = run["responses"][:-1]
        report = evaluator.evaluate_run(run)
        self.assertEqual(
            report["metrics"][evaluator.PENALTY_METRIC][
                "penalty"
            ],
            100,
        )
        self.assertEqual(
            report["case_results"][-1]["failures"][0]["code"],
            "INT_CONSUMER_RESPONSE_MISSING",
        )

    def test_run_with_wrong_fixture_identity_is_rejected(
        self,
    ) -> None:
        run = copy.deepcopy(self.good_run)
        run["fixture_identity"]["parent_identity_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            evaluator.EvaluationFailure,
            "INT_EVALUATION_IDENTITY_MISMATCH",
        ):
            evaluator.evaluate_run(run)

    def test_reports_are_canonical_and_fingerprinted(self) -> None:
        evaluator.validate_report(
            self.good_report,
            self.good_run,
        )
        self.assertEqual(
            evaluator.canonical_text(self.good_report),
            evaluator.canonical_text(
                copy.deepcopy(self.good_report)
            ),
        )
        self.assertNotIn(
            "generated_at",
            evaluator.canonical_text(self.good_report),
        )

    def test_report_tampering_is_detected(self) -> None:
        report = copy.deepcopy(self.good_report)
        report["summary"]["overall_score"] = 99
        with self.assertRaisesRegex(
            evaluator.EvaluationFailure,
            "INT_EVALUATION_REPORT_INVALID",
        ):
            evaluator.validate_report(report)

    def test_report_authority_escalation_is_rejected(self) -> None:
        report = copy.deepcopy(self.good_report)
        report["authority"][
            "report_is_parent_or_source_evidence"
        ] = True
        self.resign(report)
        with self.assertRaisesRegex(
            evaluator.EvaluationFailure,
            "INT_EVALUATION_REPORT_INVALID",
        ):
            evaluator.validate_report(report)

    def test_report_identity_must_match_validated_evidence(
        self,
    ) -> None:
        report = copy.deepcopy(self.good_report)
        report["evaluation_identity"]["parent_identity"] = {}
        report["evaluation_identity"][
            "parent_identity_sha256"
        ] = evaluator.canonical_sha256({})
        report["evaluation_identity"][
            "evaluation_index_sha256"
        ] = "0" * 64
        report["evaluation_identity"]["contract_sha256"] = "f" * 64
        self.resign(report)
        with self.assertRaisesRegex(
            evaluator.EvaluationFailure,
            "INT_EVALUATION_IDENTITY_MISMATCH",
        ):
            evaluator.validate_report(report)

    def test_report_rejects_out_of_range_case_derived_metric(
        self,
    ) -> None:
        report = copy.deepcopy(self.good_report)
        metric = evaluator.POSITIVE_METRICS[0]
        report["metrics"][metric]["score"] = 1000
        report["case_results"][0]["score"] = 1000
        report["summary"]["positive_score_sum"] = 1500
        report["summary"]["positive_score_average"] = 250
        report["summary"]["overall_score"] = 250
        self.resign(report)
        with self.assertRaisesRegex(
            evaluator.EvaluationFailure,
            "INT_EVALUATION_REPORT_INVALID",
        ):
            evaluator.validate_report(report)

    def test_report_rejects_fabricated_metric_shape_and_totals(
        self,
    ) -> None:
        metric = evaluator.POSITIVE_METRICS[0]
        mutations = (
            ("kind", "penalty"),
            ("passed_cases", 2),
            ("total_cases", 2),
            ("score", True),
        )
        for key, value in mutations:
            with self.subTest(field=key, value=value):
                report = copy.deepcopy(self.good_report)
                report["metrics"][metric][key] = value
                self.resign(report)
                with self.assertRaisesRegex(
                    evaluator.EvaluationFailure,
                    "INT_EVALUATION_REPORT_INVALID",
                ):
                    evaluator.validate_report(report)

    def test_comparison_requires_exact_fixture_and_parent_identity(
        self,
    ) -> None:
        comparison = evaluator.compare_reports(
            self.good_report,
            self.bad_report,
        )
        self.assertEqual(
            comparison["winner_by_overall_fixture_score"],
            "left",
        )

        right = copy.deepcopy(self.bad_report)
        right["evaluation_identity"]["parent_identity"]["ark"][
            "pinned_commit"
        ] = "f" * 40
        right["evaluation_identity"][
            "parent_identity_sha256"
        ] = evaluator.canonical_sha256(
            right["evaluation_identity"]["parent_identity"]
        )
        self.resign(right)

        with self.assertRaisesRegex(
            evaluator.EvaluationFailure,
            "INT_EVALUATION_IDENTITY_MISMATCH",
        ):
            evaluator.compare_reports(
                self.good_report,
                right,
            )

    def test_committed_reports_and_comparison_regenerate_exactly(
        self,
    ) -> None:
        good = evaluator.load_json(
            "evaluations/reports/synthetic-conformant.json"
        )
        bad = evaluator.load_json(
            "evaluations/reports/synthetic-adversarial.json"
        )
        comparison = evaluator.load_json(
            "evaluations/comparisons/"
            "synthetic-conformant-vs-adversarial.json"
        )
        evaluator.validate_report(good, self.good_run)
        evaluator.validate_report(bad, self.bad_run)
        evaluator.validate_comparison(
            comparison,
            good,
            bad,
        )


if __name__ == "__main__":
    unittest.main()
