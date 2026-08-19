# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "evaluations/index.json"

METRIC_ORDER = (
    "provenance_retention",
    "unknown_preservation",
    "conflict_preservation",
    "register_satire_preservation",
    "mrs_interpretation",
    "mode_boundary_discipline",
    "invented_history_penalty",
)
POSITIVE_METRICS = METRIC_ORDER[:-1]
PENALTY_METRIC = METRIC_ORDER[-1]
CASE_PATHS = tuple(
    f"evaluations/cases/{index:02d}-{name}.json"
    for index, name in enumerate(METRIC_ORDER, 1)
)
EXECUTION_KINDS = {
    "synthetic_conformance",
    "model_execution",
    "agent_execution",
    "deterministic_replay",
}
OPS = {"preserves", "equals", "absent", "subset_of_input"}
MISSING = object()
FAILURES = {
    "INT_EVALUATION_INDEX_INVALID",
    "INT_EVALUATION_CASE_INVALID",
    "INT_EVALUATION_ASSERTION_FAILED",
    "INT_CONSUMER_RUN_INVALID",
    "INT_CONSUMER_RESPONSE_MISSING",
    "INT_EVALUATION_IDENTITY_MISMATCH",
    "INT_EVALUATION_REPORT_INVALID",
    "INT_EVALUATION_COMPARISON_INVALID",
}

REPORT_AUTHORITY = {
    "score_is_fixture_conformance_only": True,
    "report_is_parent_or_source_evidence": False,
    "report_establishes_general_model_quality": False,
}
COMPARISON_AUTHORITY = {
    "comparison_scope": "exact_fixture_and_parent_evidence_identity_only",
    "comparison_establishes_general_model_quality": False,
}


class EvaluationFailure(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def require(ok: bool, code: str, message: str) -> None:
    if not ok:
        raise EvaluationFailure(code, message)


def load_json(
    path: str | Path,
    code: str = "INT_EVALUATION_INDEX_INVALID",
) -> Any:
    target = Path(path)
    target = target if target.is_absolute() else ROOT / target
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvaluationFailure(
            code,
            f"cannot read JSON {target}: {exc}",
        ) from exc


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_text(value: Any) -> str:
    return canonical_bytes(value).decode("utf-8") + "\n"


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _path(value: Any, dotted: str, default: Any = MISSING) -> Any:
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return default
        value = value[part]
    return value


def _hex(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(char in "0123456789abcdef" for char in value)
    )


def _int_in_range(value: Any, minimum: int, maximum: int) -> bool:
    return type(value) is int and minimum <= value <= maximum


def parent_identity(parents: dict) -> dict:
    require(
        isinstance(parents, dict),
        "INT_EVALUATION_INDEX_INVALID",
        "parent contract invalid",
    )
    registry = parents.get("parents")
    require(
        isinstance(registry, dict) and set(registry) == {"substrate", "ark"},
        "INT_EVALUATION_INDEX_INVALID",
        "parent registry invalid",
    )

    output = {}
    for name in ("substrate", "ark"):
        parent = registry[name]
        require(
            isinstance(parent, dict)
            and isinstance(parent.get("contracts"), list),
            "INT_EVALUATION_INDEX_INVALID",
            f"invalid parent {name}",
        )
        artifacts = [
            parent.get("manifest"),
            *parent["contracts"],
        ]
        require(
            all(isinstance(artifact, dict) for artifact in artifacts),
            "INT_EVALUATION_INDEX_INVALID",
            f"invalid parent artifacts {name}",
        )

        normalized = []
        for artifact in sorted(
            artifacts,
            key=lambda item: item.get("path", ""),
        ):
            require(
                isinstance(artifact.get("path"), str)
                and _hex(artifact.get("git_blob_sha1"), 40),
                "INT_EVALUATION_INDEX_INVALID",
                f"invalid parent artifact {name}",
            )
            normalized.append(
                {
                    "path": artifact["path"],
                    "git_blob_sha1": artifact["git_blob_sha1"],
                }
            )

        require(
            isinstance(parent.get("protocol"), str)
            and isinstance(parent.get("repository"), str)
            and _hex(parent.get("pinned_commit"), 40),
            "INT_EVALUATION_INDEX_INVALID",
            f"invalid parent identity {name}",
        )
        output[name] = {
            "protocol": parent["protocol"],
            "repository": parent["repository"],
            "pinned_commit": parent["pinned_commit"],
            "artifacts": normalized,
        }
    return output


def _validate_contract(contract: dict) -> None:
    require(
        isinstance(contract, dict)
        and contract.get("type") == "qsol-int-consumer-evaluation-contract"
        and contract.get("protocol") == "QSOL-INT/CONSUMER-EVALUATION/1"
        and contract.get("version") == "1.0.0",
        "INT_EVALUATION_INDEX_INVALID",
        "evaluation contract identity invalid",
    )
    require(
        contract.get("status") == "implemented"
        and contract.get("scope")
        == "exact_fixture_and_pinned_parent_evidence_only"
        and contract.get("derived_noncanonical") is True,
        "INT_EVALUATION_INDEX_INVALID",
        "evaluation contract boundary invalid",
    )

    policy = contract.get("execution_claim_policy", {})
    require(
        policy
        == {
            "synthetic_conformance_runs_must_set_claims_execution": False,
            "model_or_agent_runs_must_declare_execution_kind": True,
            "self_reported_identity_is_not_authenticated_identity": True,
        },
        "INT_EVALUATION_INDEX_INVALID",
        "execution policy invalid",
    )

    metrics = contract.get("metrics")
    require(
        isinstance(metrics, list)
        and [
            metric.get("id")
            for metric in metrics
            if isinstance(metric, dict)
        ]
        == list(METRIC_ORDER),
        "INT_EVALUATION_INDEX_INVALID",
        "metric registry invalid",
    )
    for metric in metrics:
        require(
            metric.get("kind")
            == ("penalty" if metric["id"] == PENALTY_METRIC else "score")
            and metric.get("minimum") == 0
            and metric.get("maximum") == 100,
            "INT_EVALUATION_INDEX_INVALID",
            "metric range invalid",
        )

    rules = contract.get("rules")
    require(
        isinstance(rules, list)
        and len(rules) == len(set(rules))
        and {
            "scores_measure_fixture_conformance_only",
            "comparison_requires_identical_fixture_and_parent_evidence_identity",
        }.issubset(rules),
        "INT_EVALUATION_INDEX_INVALID",
        "evaluation rules invalid",
    )

    codes = contract.get("failure_codes")
    require(
        isinstance(codes, list)
        and len(codes) == len(set(codes))
        and set(codes) == FAILURES,
        "INT_EVALUATION_INDEX_INVALID",
        "failure registry invalid",
    )


def _validate_case(case: dict, case_id: str, metric: str) -> None:
    require(
        isinstance(case, dict)
        and case.get("id") == case_id
        and case.get("metric") == metric
        and case.get("synthetic") is True
        and isinstance(case.get("input"), dict),
        "INT_EVALUATION_CASE_INVALID",
        f"invalid case {case_id}",
    )

    assertions = case.get("assertions")
    require(
        isinstance(assertions, list) and bool(assertions),
        "INT_EVALUATION_CASE_INVALID",
        f"assertions missing {case_id}",
    )
    for assertion in assertions:
        require(
            isinstance(assertion, dict)
            and assertion.get("op") in OPS
            and isinstance(assertion.get("output_path"), str)
            and bool(assertion["output_path"]),
            "INT_EVALUATION_CASE_INVALID",
            f"invalid assertion {case_id}",
        )
        if assertion["op"] in {"preserves", "subset_of_input"}:
            require(
                isinstance(assertion.get("input_path"), str)
                and bool(assertion["input_path"]),
                "INT_EVALUATION_CASE_INVALID",
                f"input path missing {case_id}",
            )
        if assertion["op"] == "equals":
            require(
                "value" in assertion,
                "INT_EVALUATION_CASE_INVALID",
                f"value missing {case_id}",
            )


def validate_index(
    index: dict | None = None,
) -> tuple[dict, list[dict]]:
    index = load_json(INDEX_PATH) if index is None else index
    require(
        isinstance(index, dict)
        and index.get("type") == "qsol-int-consumer-evaluation-index"
        and index.get("protocol") == "QSOL-INT/CONSUMER-EVALUATION/1"
        and index.get("version") == "1.0.0",
        "INT_EVALUATION_INDEX_INVALID",
        "index identity invalid",
    )
    require(
        index.get("scope")
        == "exact_fixture_and_pinned_parent_evidence_only"
        and index.get("derived_reports_are_noncanonical") is True,
        "INT_EVALUATION_INDEX_INVALID",
        "index scope invalid",
    )

    contract = load_json(index.get("contract", ""))
    _validate_contract(contract)
    require(
        index.get("contract") == "ai/consumer-evaluation-contract.json"
        and index.get("contract_sha256") == canonical_sha256(contract),
        "INT_EVALUATION_INDEX_INVALID",
        "contract receipt invalid",
    )

    parents = load_json(index.get("parent_contract", ""))
    identity = parent_identity(parents)
    require(
        index.get("parent_contract") == "ai/parent-contracts.json"
        and index.get("parent_identity") == identity
        and index.get("parent_identity_sha256")
        == canonical_sha256(identity),
        "INT_EVALUATION_INDEX_INVALID",
        "parent identity invalid",
    )

    paths = index.get("cases")
    case_ids = index.get("required_case_ids")
    receipts = index.get("case_sha256")
    require(
        tuple(paths or []) == CASE_PATHS
        and case_ids
        == [f"INT-EVAL-{number:03d}" for number in range(1, 8)]
        and index.get("metrics") == list(METRIC_ORDER),
        "INT_EVALUATION_INDEX_INVALID",
        "case registry invalid",
    )
    require(
        isinstance(receipts, dict) and set(receipts) == set(CASE_PATHS),
        "INT_EVALUATION_INDEX_INVALID",
        "case receipts invalid",
    )

    cases = []
    for path, case_id, metric in zip(
        CASE_PATHS,
        case_ids,
        METRIC_ORDER,
    ):
        case = load_json(path, "INT_EVALUATION_CASE_INVALID")
        _validate_case(case, case_id, metric)
        require(
            receipts[path] == canonical_sha256(case),
            "INT_EVALUATION_INDEX_INVALID",
            f"case receipt invalid {path}",
        )
        cases.append(case)
    return index, cases


def validate_run(
    run: dict,
    index: dict,
    cases: list[dict],
) -> dict[str, dict]:
    require(
        isinstance(run, dict)
        and run.get("type") == "qsol-int-consumer-run"
        and run.get("protocol") == "QSOL-INT/CONSUMER-RUN/1"
        and run.get("version") == "1.0.0",
        "INT_CONSUMER_RUN_INVALID",
        "run identity invalid",
    )

    execution_kind = run.get("execution_kind")
    claims_execution = run.get("claims_execution")
    require(
        execution_kind in EXECUTION_KINDS
        and isinstance(claims_execution, bool),
        "INT_CONSUMER_RUN_INVALID",
        "execution declaration invalid",
    )
    require(
        claims_execution is (execution_kind != "synthetic_conformance"),
        "INT_CONSUMER_RUN_INVALID",
        "execution claim contradicts run kind",
    )

    require(
        isinstance(run.get("run_id"), str) and bool(run["run_id"]),
        "INT_CONSUMER_RUN_INVALID",
        "run id missing",
    )
    subject = run.get("subject")
    require(
        isinstance(subject, dict)
        and all(
            isinstance(subject.get(key), str) and bool(subject[key])
            for key in (
                "kind",
                "id",
                "version",
                "identity_authentication",
            )
        ),
        "INT_CONSUMER_RUN_INVALID",
        "subject invalid",
    )

    fixture_identity = run.get("fixture_identity")
    require(
        isinstance(fixture_identity, dict),
        "INT_CONSUMER_RUN_INVALID",
        "fixture identity must be an object",
    )
    require(
        fixture_identity.get("evaluation_index_sha256")
        == canonical_sha256(index)
        and fixture_identity.get("parent_identity_sha256")
        == index["parent_identity_sha256"],
        "INT_EVALUATION_IDENTITY_MISMATCH",
        "run identity mismatch",
    )

    allowed = {case["id"] for case in cases}
    responses = run.get("responses")
    require(
        isinstance(responses, list),
        "INT_CONSUMER_RUN_INVALID",
        "responses invalid",
    )
    output = {}
    for item in responses:
        case_id = item.get("case_id") if isinstance(item, dict) else None
        require(
            case_id in allowed
            and case_id not in output
            and isinstance(item.get("output"), dict),
            "INT_CONSUMER_RUN_INVALID",
            f"invalid response {case_id}",
        )
        output[case_id] = item["output"]
    return output


def _assert(
    case_input: dict,
    output: dict,
    assertion: dict,
) -> tuple[bool, str]:
    actual = _path(output, assertion["output_path"])
    operation = assertion["op"]

    if operation == "absent":
        return (
            actual is MISSING,
            f"expected {assertion['output_path']} absent",
        )
    if actual is MISSING:
        return False, f"missing {assertion['output_path']}"
    if operation == "equals":
        return (
            actual == assertion["value"],
            f"expected {assertion['output_path']}={assertion['value']!r}",
        )

    expected = _path(case_input, assertion["input_path"])
    if expected is MISSING:
        return False, f"missing fixture {assertion['input_path']}"
    if operation == "preserves":
        return (
            actual == expected,
            f"failed to preserve {assertion['input_path']}",
        )

    ok = (
        isinstance(expected, list)
        and isinstance(actual, list)
        and all(
            isinstance(item, str)
            for item in expected + actual
        )
        and set(actual).issubset(expected)
    )
    return ok, f"unsupported item in {assertion['output_path']}"


def evaluate_run(
    run: dict,
    index: dict | None = None,
    cases: list[dict] | None = None,
) -> dict:
    if index is None or cases is None:
        index, cases = validate_index(index)

    responses = validate_run(run, index, cases)
    case_results = []
    metrics = {}

    for case in cases:
        output = responses.get(case["id"])
        failures = []

        if output is None:
            failures = [
                {
                    "code": "INT_CONSUMER_RESPONSE_MISSING",
                    "message": "consumer response is missing",
                }
            ]
        else:
            for assertion in case["assertions"]:
                ok, message = _assert(
                    case["input"],
                    output,
                    assertion,
                )
                if not ok:
                    failures.append(
                        {
                            "code": "INT_EVALUATION_ASSERTION_FAILED",
                            "message": message,
                            "assertion": assertion,
                        }
                    )

        passed = not failures
        metric = case["metric"]

        if metric == PENALTY_METRIC:
            value = 0 if passed else 100
            metrics[metric] = {
                "kind": "penalty",
                "penalty": value,
                "passed_cases": int(passed),
                "total_cases": 1,
            }
            score = {"penalty": value}
        else:
            value = 100 if passed else 0
            metrics[metric] = {
                "kind": "score",
                "score": value,
                "passed_cases": int(passed),
                "total_cases": 1,
            }
            score = {"score": value}

        case_results.append(
            {
                "id": case["id"],
                "metric": metric,
                "result": "pass" if passed else "fail",
                **score,
                "failure_count": len(failures),
                "failures": failures,
            }
        )

    positive_score_sum = sum(
        metrics[metric]["score"]
        for metric in POSITIVE_METRICS
    )
    positive_score_average = (
        positive_score_sum // len(POSITIVE_METRICS)
    )
    penalty = metrics[PENALTY_METRIC]["penalty"]

    report = {
        "type": "qsol-int-consumer-evaluation-report",
        "protocol": "QSOL-INT/CONSUMER-EVALUATION/1",
        "version": "1.0.0",
        "derived_noncanonical": True,
        "authority": dict(REPORT_AUTHORITY),
        "evaluation_identity": _expected_evaluation_identity(index),
        "run": {
            "run_id": run["run_id"],
            "execution_kind": run["execution_kind"],
            "claims_execution": run["claims_execution"],
            "subject": run["subject"],
            "manifest_sha256": canonical_sha256(run),
        },
        "metrics": metrics,
        "case_results": case_results,
        "summary": {
            "positive_score_sum": positive_score_sum,
            "positive_metric_count": len(POSITIVE_METRICS),
            "positive_score_average": positive_score_average,
            "invented_history_penalty": penalty,
            "overall_score": max(
                0,
                positive_score_average - penalty,
            ),
            "passed_cases": sum(
                item["result"] == "pass"
                for item in case_results
            ),
            "failed_cases": sum(
                item["result"] == "fail"
                for item in case_results
            ),
        },
    }
    report["fingerprint_sha256"] = canonical_sha256(report)
    return report


def _expected_evaluation_identity(index: dict) -> dict:
    return {
        "index": "evaluations/index.json",
        "evaluation_index_sha256": canonical_sha256(index),
        "contract": index["contract"],
        "contract_sha256": index["contract_sha256"],
        "parent_identity": index["parent_identity"],
        "parent_identity_sha256": index["parent_identity_sha256"],
    }


def _validate_report_run(run: Any) -> None:
    require(
        isinstance(run, dict)
        and set(run)
        == {
            "run_id",
            "execution_kind",
            "claims_execution",
            "subject",
            "manifest_sha256",
        },
        "INT_EVALUATION_REPORT_INVALID",
        "report run identity invalid",
    )
    require(
        isinstance(run.get("run_id"), str)
        and bool(run["run_id"])
        and run.get("execution_kind") in EXECUTION_KINDS
        and isinstance(run.get("claims_execution"), bool)
        and run["claims_execution"]
        is (run["execution_kind"] != "synthetic_conformance")
        and _hex(run.get("manifest_sha256"), 64),
        "INT_EVALUATION_REPORT_INVALID",
        "report run declaration invalid",
    )

    subject = run.get("subject")
    require(
        isinstance(subject, dict)
        and all(
            isinstance(subject.get(key), str) and bool(subject[key])
            for key in (
                "kind",
                "id",
                "version",
                "identity_authentication",
            )
        ),
        "INT_EVALUATION_REPORT_INVALID",
        "report subject invalid",
    )


def _validate_case_results(
    case_results: Any,
    cases: list[dict],
) -> list[dict]:
    require(
        isinstance(case_results, list)
        and len(case_results) == len(cases),
        "INT_EVALUATION_REPORT_INVALID",
        "case result registry invalid",
    )

    validated = []
    for item, case in zip(case_results, cases):
        metric = case["metric"]
        value_field = (
            "penalty" if metric == PENALTY_METRIC else "score"
        )
        expected_keys = {
            "id",
            "metric",
            "result",
            value_field,
            "failure_count",
            "failures",
        }
        require(
            isinstance(item, dict)
            and set(item) == expected_keys
            and item.get("id") == case["id"]
            and item.get("metric") == metric
            and item.get("result") in {"pass", "fail"},
            "INT_EVALUATION_REPORT_INVALID",
            f"case result identity invalid {case['id']}",
        )

        failures = item.get("failures")
        failure_count = item.get("failure_count")
        require(
            isinstance(failures, list)
            and type(failure_count) is int
            and failure_count >= 0
            and failure_count == len(failures),
            "INT_EVALUATION_REPORT_INVALID",
            f"case failure total invalid {case['id']}",
        )
        for failure in failures:
            require(
                isinstance(failure, dict)
                and failure.get("code")
                in {
                    "INT_CONSUMER_RESPONSE_MISSING",
                    "INT_EVALUATION_ASSERTION_FAILED",
                }
                and isinstance(failure.get("message"), str)
                and bool(failure["message"]),
                "INT_EVALUATION_REPORT_INVALID",
                f"case failure invalid {case['id']}",
            )

        passed = item["result"] == "pass"
        require(
            (passed and failure_count == 0)
            or (not passed and failure_count > 0),
            "INT_EVALUATION_REPORT_INVALID",
            f"case result contradicts failures {case['id']}",
        )

        value = item.get(value_field)
        expected_value = (
            (0 if passed else 100)
            if metric == PENALTY_METRIC
            else (100 if passed else 0)
        )
        require(
            _int_in_range(value, 0, 100)
            and value == expected_value,
            "INT_EVALUATION_REPORT_INVALID",
            f"case metric value invalid {case['id']}",
        )
        validated.append(item)
    return validated


def _validate_metrics(
    metrics: Any,
    case_results: list[dict],
) -> None:
    require(
        isinstance(metrics, dict)
        and set(metrics) == set(METRIC_ORDER),
        "INT_EVALUATION_REPORT_INVALID",
        "metric registry invalid",
    )

    for metric in METRIC_ORDER:
        entry = metrics[metric]
        value_field = (
            "penalty" if metric == PENALTY_METRIC else "score"
        )
        expected_kind = (
            "penalty" if metric == PENALTY_METRIC else "score"
        )
        require(
            isinstance(entry, dict)
            and set(entry)
            == {
                "kind",
                value_field,
                "passed_cases",
                "total_cases",
            }
            and entry.get("kind") == expected_kind,
            "INT_EVALUATION_REPORT_INVALID",
            f"metric shape invalid {metric}",
        )

        relevant = [
            item
            for item in case_results
            if item["metric"] == metric
        ]
        total_cases = len(relevant)
        passed_cases = sum(
            item["result"] == "pass"
            for item in relevant
        )
        require(
            total_cases > 0
            and type(entry.get("passed_cases")) is int
            and type(entry.get("total_cases")) is int
            and entry["passed_cases"] == passed_cases
            and entry["total_cases"] == total_cases,
            "INT_EVALUATION_REPORT_INVALID",
            f"metric case totals invalid {metric}",
        )

        if metric == PENALTY_METRIC:
            expected_value = (
                100 * (total_cases - passed_cases) // total_cases
            )
        else:
            expected_value = 100 * passed_cases // total_cases

        value = entry.get(value_field)
        require(
            _int_in_range(value, 0, 100)
            and value == expected_value,
            "INT_EVALUATION_REPORT_INVALID",
            f"metric value invalid {metric}",
        )


def _expected_summary(
    metrics: dict,
    case_results: list[dict],
) -> dict:
    positive_score_sum = sum(
        metrics[metric]["score"]
        for metric in POSITIVE_METRICS
    )
    positive_score_average = (
        positive_score_sum // len(POSITIVE_METRICS)
    )
    penalty = metrics[PENALTY_METRIC]["penalty"]
    return {
        "positive_score_sum": positive_score_sum,
        "positive_metric_count": len(POSITIVE_METRICS),
        "positive_score_average": positive_score_average,
        "invented_history_penalty": penalty,
        "overall_score": max(
            0,
            positive_score_average - penalty,
        ),
        "passed_cases": sum(
            item["result"] == "pass"
            for item in case_results
        ),
        "failed_cases": sum(
            item["result"] == "fail"
            for item in case_results
        ),
    }


def validate_report(
    report: dict,
    run: dict | None = None,
    index: dict | None = None,
    cases: list[dict] | None = None,
) -> None:
    if index is None or cases is None:
        index, cases = validate_index(index)

    require(
        isinstance(report, dict)
        and report.get("type")
        == "qsol-int-consumer-evaluation-report"
        and report.get("protocol")
        == "QSOL-INT/CONSUMER-EVALUATION/1"
        and report.get("version") == "1.0.0"
        and report.get("derived_noncanonical") is True,
        "INT_EVALUATION_REPORT_INVALID",
        "report identity invalid",
    )

    fingerprint = report.get("fingerprint_sha256")
    unsigned = dict(report)
    unsigned.pop("fingerprint_sha256", None)
    require(
        _hex(fingerprint, 64)
        and fingerprint == canonical_sha256(unsigned),
        "INT_EVALUATION_REPORT_INVALID",
        "report fingerprint invalid",
    )

    require(
        report.get("authority") == REPORT_AUTHORITY,
        "INT_EVALUATION_REPORT_INVALID",
        "report authority boundary invalid",
    )

    identity = report.get("evaluation_identity")
    require(
        isinstance(identity, dict),
        "INT_EVALUATION_REPORT_INVALID",
        "evaluation identity invalid",
    )
    require(
        identity == _expected_evaluation_identity(index),
        "INT_EVALUATION_IDENTITY_MISMATCH",
        "report identity does not match validated evaluation evidence",
    )

    _validate_report_run(report.get("run"))
    case_results = _validate_case_results(
        report.get("case_results"),
        cases,
    )
    metrics = report.get("metrics")
    _validate_metrics(metrics, case_results)

    require(
        report.get("summary")
        == _expected_summary(metrics, case_results),
        "INT_EVALUATION_REPORT_INVALID",
        "score summary invalid",
    )

    if run is not None:
        require(
            report == evaluate_run(run, index, cases),
            "INT_EVALUATION_REPORT_INVALID",
            "report regeneration mismatch",
        )


def compare_reports(left: dict, right: dict) -> dict:
    index, cases = validate_index()
    validate_report(left, index=index, cases=cases)
    validate_report(right, index=index, cases=cases)
    require(
        left["evaluation_identity"]
        == right["evaluation_identity"],
        "INT_EVALUATION_IDENTITY_MISMATCH",
        "report identities differ",
    )

    deltas = {}
    for metric in METRIC_ORDER:
        field = (
            "penalty" if metric == PENALTY_METRIC else "score"
        )
        left_value = left["metrics"][metric][field]
        right_value = right["metrics"][metric][field]
        deltas[metric] = {
            "left": left_value,
            "right": right_value,
            "right_minus_left": right_value - left_value,
        }

    left_score = left["summary"]["overall_score"]
    right_score = right["summary"]["overall_score"]
    if left_score == right_score:
        winner = "tie"
    elif left_score > right_score:
        winner = "left"
    else:
        winner = "right"

    comparison = {
        "type": "qsol-int-consumer-evaluation-comparison",
        "protocol": "QSOL-INT/CONSUMER-EVALUATION/1",
        "version": "1.0.0",
        "derived_noncanonical": True,
        "authority": dict(COMPARISON_AUTHORITY),
        "evaluation_identity": left["evaluation_identity"],
        "left": {
            "run": left["run"],
            "report_fingerprint_sha256": left["fingerprint_sha256"],
            "overall_score": left_score,
        },
        "right": {
            "run": right["run"],
            "report_fingerprint_sha256": right["fingerprint_sha256"],
            "overall_score": right_score,
        },
        "metric_deltas": deltas,
        "winner_by_overall_fixture_score": winner,
    }
    comparison["fingerprint_sha256"] = canonical_sha256(comparison)
    return comparison


def validate_comparison(
    comparison: dict,
    left: dict | None = None,
    right: dict | None = None,
) -> None:
    require(
        isinstance(comparison, dict)
        and comparison.get("type")
        == "qsol-int-consumer-evaluation-comparison"
        and comparison.get("protocol")
        == "QSOL-INT/CONSUMER-EVALUATION/1"
        and comparison.get("version") == "1.0.0"
        and comparison.get("derived_noncanonical") is True,
        "INT_EVALUATION_COMPARISON_INVALID",
        "comparison identity invalid",
    )

    fingerprint = comparison.get("fingerprint_sha256")
    unsigned = dict(comparison)
    unsigned.pop("fingerprint_sha256", None)
    require(
        _hex(fingerprint, 64)
        and fingerprint == canonical_sha256(unsigned),
        "INT_EVALUATION_COMPARISON_INVALID",
        "comparison fingerprint invalid",
    )

    require(
        comparison.get("authority") == COMPARISON_AUTHORITY,
        "INT_EVALUATION_COMPARISON_INVALID",
        "comparison authority boundary invalid",
    )

    index, _ = validate_index()
    require(
        comparison.get("evaluation_identity")
        == _expected_evaluation_identity(index),
        "INT_EVALUATION_IDENTITY_MISMATCH",
        "comparison identity does not match validated evaluation evidence",
    )

    require(
        comparison.get("winner_by_overall_fixture_score")
        in {"left", "right", "tie"},
        "INT_EVALUATION_COMPARISON_INVALID",
        "comparison winner invalid",
    )

    metric_deltas = comparison.get("metric_deltas")
    require(
        isinstance(metric_deltas, dict)
        and set(metric_deltas) == set(METRIC_ORDER),
        "INT_EVALUATION_COMPARISON_INVALID",
        "comparison metric registry invalid",
    )
    for metric in METRIC_ORDER:
        delta = metric_deltas[metric]
        require(
            isinstance(delta, dict)
            and set(delta)
            == {"left", "right", "right_minus_left"}
            and _int_in_range(delta.get("left"), 0, 100)
            and _int_in_range(delta.get("right"), 0, 100)
            and type(delta.get("right_minus_left")) is int
            and delta["right_minus_left"]
            == delta["right"] - delta["left"],
            "INT_EVALUATION_COMPARISON_INVALID",
            f"comparison metric invalid {metric}",
        )

    if left is not None and right is not None:
        require(
            comparison == compare_reports(left, right),
            "INT_EVALUATION_COMPARISON_INVALID",
            "comparison regeneration mismatch",
        )
