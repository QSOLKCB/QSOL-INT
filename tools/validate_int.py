#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def load(path: str) -> dict:
    with (ROOT / path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def validate_parent_contracts(data: dict | None = None) -> dict:
    data = data or load("ai/parent-contracts.json")
    parents = data.get("parents", {})
    require(set(parents) == {"substrate", "ark"}, "INT_PARENT_CONTRACT_INCOMPLETE")
    for parent in parents.values():
        require(HEX40.fullmatch(parent.get("pinned_commit", "")) is not None, "INT_PARENT_PIN_INVALID")
    ark = parents["ark"]
    ids = ark.get("observed_tier_ids", [])
    require(ids == ["T0", "T1", "T2", "T3", "T4", "T5"], "INT_PARENT_CONTRACT_INCOMPLETE")
    require(set(ark.get("observed_implemented_tiers", [])).issubset(set(ids)), "INT_PARENT_CONTRACT_INCOMPLETE")
    require("never infer or inherit undeclared capabilities" in ark.get("mrs_rule", ""), "INT_CAPABILITY_REDEFINITION")
    return data


def validate_integration(data: dict | None = None) -> dict:
    data = data or load("ai/integration-contract.json")
    require(data.get("core_invariant") == "INTEGRATION_MUST_NOT_INCREASE_SEMANTIC_AUTHORITY", "INT_PARENT_CONTRACT_INCOMPLETE")
    boundary = data.get("projection_boundary", {})
    require(boundary.get("receiver_is_source") is False and boundary.get("receiver_is_evidence") is False, "INT_RECEIVER_AUTHORITY_ESCALATION")
    forbidden = set(data.get("forbidden", []))
    require("canonical_epistemic_to_fixed_tier_mapping" in forbidden, "INT_STATE_TIER_COUPLING_FORBIDDEN")
    require("integration_receiver_promoted_to_source" in forbidden, "INT_RECEIVER_AUTHORITY_ESCALATION")
    return data


def validate_policy(data: dict | None = None, parents: dict | None = None) -> dict:
    data = data or load("ai/epistemic-recovery-policy.json")
    parents = parents or validate_parent_contracts()
    require(data.get("state_forces_fixed_ark_tier") is False, "INT_STATE_TIER_COUPLING_FORBIDDEN")
    selection = data.get("ark_selection", {})
    require(selection.get("capability_inheritance") is False, "INT_CAPABILITY_REDEFINITION")
    require(selection.get("rank_is_not_execution_sequence") is True, "INT_CAPABILITY_REDEFINITION")
    declared = set(parents["parents"]["ark"]["observed_declared_capabilities"])
    for example in data.get("current_capability_translation_examples", []):
        caps = example.get("ark_capabilities", [])
        require(bool(caps) and set(caps).issubset(declared), "INT_CAPABILITY_REDEFINITION")
        if "model_reconstruction" in caps:
            require(example.get("current_result") == "ARK_MRS_UNAVAILABLE", "INT_CAPABILITY_REDEFINITION")
    return data


def validate_integrity(data: dict | None = None) -> dict:
    data = data or load("ai/integrity-semantics.json")
    invariants = set(data.get("invariants", []))
    required = {"digest_match_does_not_prove_authorship", "digest_match_does_not_prove_original_source", "digest_match_does_not_prove_content_truth", "sha256_digest_is_not_a_digital_signature"}
    require(required.issubset(invariants), "INT_INTEGRITY_SEMANTICS_INVALID")
    return data


def validate_qbraid(source: dict | None = None, findings: dict | None = None) -> dict:
    source = source or load("specimens/qbraid-foundation/source-manifest.json")
    findings = findings or load("specimens/qbraid-foundation/findings.json")
    require(source.get("canonical_or_derived") == "noncanonical_design_input", "INT_QBRAID_SPECIMEN_INVALID")
    require(source.get("source_bytes_copied") is False, "INT_QBRAID_SPECIMEN_INVALID")
    require(HEX64.fullmatch(source.get("bundle", {}).get("observed_sha256", "")) is not None, "INT_QBRAID_SPECIMEN_INVALID")
    archive = source.get("archive_entries", [])
    receipts = source.get("receipt_entries", [])
    require(len(archive) == source["bundle"].get("archive_entry_count"), "INT_QBRAID_SPECIMEN_INVALID")
    require(len(receipts) == source["bundle"].get("receipt_entry_count"), "INT_QBRAID_SPECIMEN_INVALID")
    require(set(receipts).issubset(set(archive)), "INT_QBRAID_SPECIMEN_INVALID")
    require(set(receipts) != set(archive), "INT_QBRAID_RECEIPT_COVERAGE_MISMATCH_EXPECTED")
    require(source["bundle"].get("receipt_covers_all_archive_entries") is False, "INT_QBRAID_SPECIMEN_INVALID")
    require({x.get("id") for x in findings.get("findings", [])} == {"QB-001","QB-002","QB-003","QB-004","QB-005"}, "INT_QBRAID_SPECIMEN_INVALID")
    require(findings.get("preserve_source_errors") is True, "INT_QBRAID_SPECIMEN_INVALID")
    return source


def validate_references(data: dict | None = None) -> dict:
    data = data or load("ai/reference-methodologies.json")
    refs = data.get("references", [])
    require(len(refs) == 1, "INT_REFERENCE_METHODOLOGY_INVALID")
    ref = refs[0]
    require(ref.get("id") == "reference.substratism_viz", "INT_REFERENCE_METHODOLOGY_INVALID")
    require(ref.get("canonical_for_int") is False and ref.get("parent_protocol") is False, "INT_REFERENCE_METHODOLOGY_INVALID")
    require(ref.get("license") == "MIT", "INT_REFERENCE_METHODOLOGY_INVALID")
    require(HEX40.fullmatch(ref.get("pinned_commit", "")) is not None, "INT_REFERENCE_METHODOLOGY_INVALID")
    require(ref.get("int_translation", {}).get("invariant") == "AUTHORED_RECEIVER != SOURCE_EVIDENCE", "INT_RECEIVER_AUTHORITY_ESCALATION")
    return data


def validate() -> None:
    manifest = load("manifest.json")
    require(manifest.get("protocol") == "QSOL-INT", "INT_PARENT_CONTRACT_INCOMPLETE")
    parents = validate_parent_contracts()
    validate_integration()
    validate_policy(parents=parents)
    validate_integrity()
    source = validate_qbraid()
    refs = validate_references()
    print("QSOL_INT_OK " f"parents={len(parents['parents'])} " f"ark_tiers={len(parents['parents']['ark']['observed_tier_ids'])} " f"qbraid_archive={source['bundle']['archive_entry_count']} " f"qbraid_receipts={source['bundle']['receipt_entry_count']} " f"references={len(refs['references'])}")


if __name__ == "__main__":
    validate()
