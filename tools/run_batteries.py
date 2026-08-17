#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import hashlib
import json
import importlib.util
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_COMPATIBILITY = {"compatible", "incompatible", "untested", "unknown"}
REQUIRED_CASE_IDS = {f"INT-BAT-{n:03d}" for n in range(1, 10)}
EXPECTED_CASE_PATHS = {
    "batteries/cases/capability-invention.json",
    "batteries/cases/conflict-preservation.json",
    "batteries/cases/cross-mode-boundary.json",
    "batteries/cases/perfect-hash-no-evidence-strength.json",
    "batteries/cases/provenance-retention.json",
    "batteries/cases/recovery-no-authority-escalation.json",
    "batteries/cases/satire-register-preservation.json",
    "batteries/cases/stale-parent.json",
    "batteries/cases/unknown-preservation.json",
}
EXPECTED_ARK_CAPABILITIES = [
    "inspect_canary", "carry_receipt", "verify_sha256", "verify_canary",
    "standalone_hash_implementation", "interactive_offline",
    "validate_archaeology_contracts", "validate_provenance_guards", "select_mrs",
    "model_reconstruction", "epistemic_classification", "recovery_scoring",
]
HASH_AUTHORITY_DIMENSIONS = (
    "epistemic_state", "claim_maturity", "authorship", "content_truth",
    "original_source", "digital_signature", "trustworthiness",
)
EXPECTED_CONTRACT_INVARIANTS = {
    "INTEGRATION_MUST_NOT_INCREASE_SEMANTIC_AUTHORITY",
    "PERFECT_PRESERVATION_MUST_NOT_INCREASE_EPISTEMIC_AUTHORITY",
    "AUTHORED_RECEIVER != SOURCE_EVIDENCE",
    "UNAVAILABLE != CONTRADICTED",
}
EXPECTED_CONTRACT_RULES = {
    "all_case_inputs_are_synthetic_integration_fixtures",
    "passing_a_battery_is_derived_compatibility_evidence_not_parent_truth",
    "compatible_is_scoped_to_exact_pinned_parent_evidence",
    "live_parent_compatibility_must_not_be_inferred_without_drift_check",
    "hash_success_must_not_strengthen_epistemic_state_claim_maturity_authorship_source_signature_truth_or_trust",
    "unknown_and_conflict_must_survive_recovery_unless_parent_evidence_changes_them",
    "cross_mode_inference_requires_declared_bridge",
    "requested_ark_capabilities_must_exist_in_the_pinned_parent_registry",
    "reports_must_bind_exact_parent_commits_and_contract_blob_identities",
    "version_adjacency_never_implies_compatibility",
}
EXPECTED_FAILURE_CODES = {
    "INT_BATTERY_INDEX_INVALID",
    "INT_BATTERY_CASE_INVALID",
    "INT_BATTERY_EXPECTATION_FAILED",
    "INT_COMPOSITION_CONTRACT_INVALID",
    "INT_COMPATIBILITY_REPORT_INVALID",
    "INT_CAPABILITY_INVENTION",
    "INT_AUTHORITY_ESCALATION",
    "INT_PROVENANCE_LOSS",
    "INT_CROSS_MODE_BRIDGE_REQUIRED",
    "INT_PARENT_FRESHNESS_UNTESTED",
}

def load(path: str | Path) -> dict:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    with p.open("r", encoding="utf-8") as fh:
        return json.load(fh)

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def json_sha256(path: str | Path) -> str:
    return hashlib.sha256(canonical_bytes(load(path))).hexdigest()

def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)

def get_path(document: dict, dotted: str) -> Any:
    cur: Any = document
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise ValueError("INT_BATTERY_CASE_INVALID")
        cur = cur[part]
    return cur

def parent_identity(parents: dict) -> dict:
    out = {}
    for name in ("substrate", "ark"):
        parent = parents["parents"][name]
        artifacts = [parent["manifest"], *parent.get("contracts", [])]
        out[name] = {
            "protocol": parent["protocol"],
            "repository": parent["repository"],
            "pinned_commit": parent["pinned_commit"],
            "artifacts": [
                {"path": a["path"], "git_blob_sha1": a["git_blob_sha1"]}
                for a in sorted(artifacts, key=lambda x: x["path"])
            ],
        }
    return out

def validate_index(index: dict) -> None:
    require(index.get("type") == "qsol-int-battery-index", "INT_BATTERY_INDEX_INVALID")
    require(index.get("protocol") == "QSOL-INT", "INT_BATTERY_INDEX_INVALID")
    require(index.get("scope") == "pinned_parent_evidence_only", "INT_BATTERY_INDEX_INVALID")
    cases = index.get("cases")
    require(isinstance(cases, list) and len(cases) == 9, "INT_BATTERY_INDEX_INVALID")
    require(len(cases) == len(set(cases)), "INT_BATTERY_INDEX_INVALID")
    require(set(cases) == EXPECTED_CASE_PATHS, "INT_BATTERY_INDEX_INVALID")
    receipts = index.get("case_sha256")
    require(isinstance(receipts, dict) and set(receipts) == EXPECTED_CASE_PATHS, "INT_BATTERY_INDEX_INVALID")
    for path, digest in receipts.items():
        require(isinstance(digest, str) and len(digest) == 64, "INT_BATTERY_INDEX_INVALID")
        require(json_sha256(path) == digest, "INT_BATTERY_INDEX_INVALID")
    ids = index.get("required_case_ids")
    require(isinstance(ids, list) and set(ids) == REQUIRED_CASE_IDS and len(ids) == len(set(ids)), "INT_BATTERY_INDEX_INVALID")
    require(index.get("contract") == "ai/composition-battery-contract.json", "INT_BATTERY_INDEX_INVALID")
    require(index.get("live_parent_freshness") == "untested", "INT_BATTERY_INDEX_INVALID")

def validate_composition_contract(contract: dict) -> None:
    require(isinstance(contract, dict), "INT_COMPOSITION_CONTRACT_INVALID")
    require(contract.get("type") == "qsol-int-composition-battery-contract", "INT_COMPOSITION_CONTRACT_INVALID")
    require(contract.get("protocol") == "QSOL-INT", "INT_COMPOSITION_CONTRACT_INVALID")
    require(contract.get("version") == "0.3.0", "INT_COMPOSITION_CONTRACT_INVALID")
    require(contract.get("status") == "implemented", "INT_COMPOSITION_CONTRACT_INVALID")
    require(contract.get("scope") == "pinned_parent_evidence_only", "INT_COMPOSITION_CONTRACT_INVALID")
    invariants = contract.get("core_invariants")
    require(isinstance(invariants, list) and len(invariants) == len(set(invariants)), "INT_COMPOSITION_CONTRACT_INVALID")
    require(set(invariants) == EXPECTED_CONTRACT_INVARIANTS, "INT_COMPOSITION_CONTRACT_INVALID")
    require(contract.get("compatibility_states") == ["compatible", "incompatible", "untested", "unknown"], "INT_COMPOSITION_CONTRACT_INVALID")
    require(contract.get("case_result_states") == ["pass", "fail"], "INT_COMPOSITION_CONTRACT_INVALID")
    require(contract.get("live_parent_freshness") == "untested_until_pr2", "INT_COMPOSITION_CONTRACT_INVALID")
    rules = contract.get("rules")
    require(isinstance(rules, list) and len(rules) == len(set(rules)), "INT_COMPOSITION_CONTRACT_INVALID")
    require(set(rules) == EXPECTED_CONTRACT_RULES, "INT_COMPOSITION_CONTRACT_INVALID")
    codes = contract.get("failure_codes")
    require(isinstance(codes, list) and len(codes) == len(set(codes)), "INT_COMPOSITION_CONTRACT_INVALID")
    require(set(codes) == EXPECTED_FAILURE_CODES, "INT_COMPOSITION_CONTRACT_INVALID")

def _load_parent_validator():
    validator_path = ROOT / "tools" / "validate_int.py"
    require(validator_path.is_file(), "INT_BATTERY_INDEX_INVALID")
    spec = importlib.util.spec_from_file_location("qsol_int_validate", validator_path)
    require(spec is not None and spec.loader is not None, "INT_BATTERY_INDEX_INVALID")
    validator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validator)
    return validator

def validate_battery_parents(parents: dict) -> None:
    validator = _load_parent_validator()
    validator.validate_parent_contracts(parents)
    ark = parents.get("parents", {}).get("ark", {})
    require(
        ark.get("observed_declared_capabilities") == EXPECTED_ARK_CAPABILITIES,
        "INT_CAPABILITY_REDEFINITION",
    )

def _case_base(case: dict) -> None:
    require(isinstance(case, dict), "INT_BATTERY_CASE_INVALID")
    require(case.get("id") in REQUIRED_CASE_IDS, "INT_BATTERY_CASE_INVALID")
    require(case.get("synthetic") is True, "INT_BATTERY_CASE_INVALID")
    require(case.get("expected", {}).get("result") == "pass", "INT_BATTERY_CASE_INVALID")
    require(isinstance(case.get("fixture"), dict), "INT_BATTERY_CASE_INVALID")

def evaluate_case(case: dict, parents: dict) -> dict:
    _case_base(case)
    rule = case.get("rule")
    fixture = case["fixture"]
    observed = {"decision": "allow", "failure_code": None}

    if rule == "preserve_paths":
        before = fixture.get("before", {})
        after = fixture.get("after", {})
        paths = fixture.get("paths", [])
        require(isinstance(paths, list) and paths, "INT_BATTERY_CASE_INVALID")
        ok = all(get_path(before, p) == get_path(after, p) for p in paths)
        if not ok:
            code = "INT_PROVENANCE_LOSS" if case.get("battery") == "provenance_retention" else "INT_BATTERY_EXPECTATION_FAILED"
            observed = {"decision": "reject", "failure_code": code}

    elif rule == "cross_mode_bridge":
        material = fixture.get("material_cross_domain_inference") is True
        bridges = fixture.get("declared_bridges")
        require(isinstance(bridges, list), "INT_BATTERY_CASE_INVALID")
        if material and not bridges:
            observed = {"decision": "block", "failure_code": "INT_CROSS_MODE_BRIDGE_REQUIRED"}
        ok = observed["decision"] == case["expected"].get("decision") and observed["failure_code"] == case["expected"].get("failure_code")

    elif rule == "recovery_authority":
        before = fixture.get("before", {}).get("claim", {})
        after = fixture.get("after", {}).get("claim", {})
        recovery = fixture.get("recovery", {})
        require(recovery.get("success") is True, "INT_BATTERY_CASE_INVALID")
        ok = before.get("epistemic_state") == after.get("epistemic_state") and before.get("claim_maturity") == after.get("claim_maturity")
        if not ok:
            observed = {"decision": "reject", "failure_code": "INT_AUTHORITY_ESCALATION"}

    elif rule == "hash_authority":
        before = fixture.get("before", {}).get("claim", {})
        after = fixture.get("after", {}).get("claim", {})
        require(fixture.get("integrity", {}).get("sha256_match") is True, "INT_BATTERY_CASE_INVALID")
        require(set(before) == set(HASH_AUTHORITY_DIMENSIONS), "INT_BATTERY_CASE_INVALID")
        require(set(after) == set(HASH_AUTHORITY_DIMENSIONS), "INT_BATTERY_CASE_INVALID")
        ok = all(before[k] == after[k] for k in HASH_AUTHORITY_DIMENSIONS)
        if not ok:
            observed = {"decision": "reject", "failure_code": "INT_AUTHORITY_ESCALATION"}

    elif rule == "capability_guard":
        requested = fixture.get("requested_capabilities")
        require(isinstance(requested, list) and requested, "INT_BATTERY_CASE_INVALID")
        declared = set(parents["parents"]["ark"]["observed_declared_capabilities"])
        invented = sorted(set(requested) - declared)
        if invented:
            observed = {"decision": "reject", "failure_code": "INT_CAPABILITY_INVENTION", "invented_capabilities": invented}
        ok = observed["decision"] == case["expected"].get("decision") and observed["failure_code"] == case["expected"].get("failure_code")

    elif rule == "parent_freshness_guard":
        checked = fixture.get("live_parent_freshness_checked")
        require(checked is False, "INT_BATTERY_CASE_INVALID")
        observed = {"compatibility": "untested", "requires_review": True, "failure_code": "INT_PARENT_FRESHNESS_UNTESTED"}
        ok = observed["compatibility"] == case["expected"].get("compatibility") and observed["requires_review"] is case["expected"].get("requires_review") and observed["failure_code"] == case["expected"].get("failure_code")

    else:
        raise ValueError("INT_BATTERY_CASE_INVALID")

    result = "pass" if ok else "fail"
    if result == "fail" and observed.get("failure_code") is None:
        observed = {"decision": "reject", "failure_code": "INT_BATTERY_EXPECTATION_FAILED"}
    return {"id": case["id"], "battery": case["battery"], "result": result, "observed": observed}

def run() -> dict:
    index = load("batteries/index.json")
    validate_index(index)
    contract = load(index["contract"])
    validate_composition_contract(contract)
    parents = load("ai/parent-contracts.json")
    validate_battery_parents(parents)

    results = []
    seen = set()
    for path in index["cases"]:
        case = load(path)
        require(case.get("id") not in seen, "INT_BATTERY_INDEX_INVALID")
        seen.add(case.get("id"))
        results.append(evaluate_case(case, parents))

    require(seen == REQUIRED_CASE_IDS, "INT_BATTERY_INDEX_INVALID")
    passed = sum(r["result"] == "pass" for r in results)
    failed = len(results) - passed
    compatibility = "compatible" if failed == 0 else "incompatible"
    report = {
        "type": "qsol-int-compatibility-report",
        "protocol": "QSOL-INT",
        "version": "0.3.0",
        "scope": "pinned_parent_evidence_only",
        "compatibility": compatibility,
        "live_parent_freshness": "untested",
        "parents": parent_identity(parents),
        "battery": {
            "version": index["version"],
            "index": "batteries/index.json",
            "index_sha256": json_sha256("batteries/index.json"),
            "contract": index["contract"],
            "contract_sha256": json_sha256(index["contract"]),
            "case_count": len(results),
        },
        "case_results": results,
        "summary": {"passed": passed, "failed": failed, "requires_live_drift_check_for_current_parent_claim": True},
    }
    report["fingerprint_sha256"] = hashlib.sha256(canonical_bytes(report)).hexdigest()
    return report

def validate_report(report: dict) -> None:
    require(isinstance(report, dict), "INT_COMPATIBILITY_REPORT_INVALID")
    require(report.get("type") == "qsol-int-compatibility-report", "INT_COMPATIBILITY_REPORT_INVALID")
    require(report.get("protocol") == "QSOL-INT", "INT_COMPATIBILITY_REPORT_INVALID")
    require(report.get("scope") == "pinned_parent_evidence_only", "INT_COMPATIBILITY_REPORT_INVALID")
    require(report.get("compatibility") in ALLOWED_COMPATIBILITY, "INT_COMPATIBILITY_REPORT_INVALID")
    require(report.get("live_parent_freshness") == "untested", "INT_COMPATIBILITY_REPORT_INVALID")

    # Reports are derived evidence. Never trust their caller-supplied case results,
    # summaries, parent identity, hashes, or compatibility label: regenerate all of it.
    expected = run()
    require(report == expected, "INT_COMPATIBILITY_REPORT_INVALID")

def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic QSOL-INT cross-repo composition batteries.")
    parser.add_argument("--json", action="store_true", help="emit canonical machine JSON")
    parser.add_argument("--write-report", metavar="PATH", help="write the canonical report to PATH")
    parser.add_argument("--validate-report", metavar="PATH", help="validate an existing compatibility report and exit")
    args = parser.parse_args()

    if args.validate_report:
        validate_report(load(args.validate_report))
        print("INT_COMPATIBILITY_REPORT_OK")
        return 0

    report = run()
    validate_report(report)
    payload = canonical_bytes(report).decode("utf-8") + "\n"
    if args.write_report:
        path = Path(args.write_report)
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    if args.json:
        print(payload, end="")
    else:
        print("QSOL-INT COMPOSITION BATTERIES")
        print(f"scope: {report['scope']}")
        print(f"pinned compatibility: {report['compatibility']}")
        print(f"live parent freshness: {report['live_parent_freshness']}")
        print(f"cases: {report['summary']['passed']}/{report['battery']['case_count']} pass")
        print("current-parent compatibility: NOT CLAIMED (PR #2 drift check required)")
        print(f"fingerprint: {report['fingerprint_sha256']}")
    return 0 if report["compatibility"] == "compatible" else 1

if __name__ == "__main__":
    raise SystemExit(main())
