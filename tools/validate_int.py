#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")

EXPECTED_ENTRYPOINTS = {
    "human": "README.md",
    "ai": "README4AI.md",
    "agent": "AGENTS.md",
    "bootstrap": "ai/bootstrap.json",
    "parent_contracts": "ai/parent-contracts.json",
    "integration_contract": "ai/integration-contract.json",
    "integrity_semantics": "ai/integrity-semantics.json",
    "epistemic_recovery_policy": "ai/epistemic-recovery-policy.json",
    "reference_methodologies": "ai/reference-methodologies.json",
    "roadmap": "ROADMAP.md",
    "validator": "tools/validate_int.py",
}

EXPECTED_PARENT_IDENTITIES = {
    "substrate": {
        "protocol": "QSOL-SUBSTRATE",
        "pinned_commit": "60e8cfeefa859df375f9f4d2fdb735edb1249db8",
        "manifest": {
            "path": "ai/manifest.json",
            "git_blob_sha1": "bdc57ae303c2ce5b8498e3867d15d1804a59ba30",
            "schema_version": "1.0.0",
        },
        "contracts": {
            "ai/epistemic-contract.json": "6abd254957843f2a0d42066423a5689099f85b6c",
            "ai/mode-contract.json": "9c830b095f59bbd948bf9ea5a8b35127121a7d99",
        },
    },
    "ark": {
        "protocol": "QSOL-ARK",
        "pinned_commit": "f2bbf149abb3f8ccbfed158176873d813b66b546",
        "manifest": {
            "path": "manifest.json",
            "git_blob_sha1": "9016cf8e6641d48e639fb69cd5ad7f98a02840b7",
            "schema_version": "0.2.0",
        },
        "contracts": {
            "ai/recovery-tiers.json": "dc7ea8e37772e677ee09f0e3a1447c2700a74789",
            "ai/minimum-recoverable-substrate.json": "1a4860543488357321e1aad24ce36266769c5f39",
        },
    },
}

EXPECTED_COMPOSITION_RULES = {
    "preserve_parent_semantics_without_redefinition",
    "preserve_substrate_uncertainty_and_provenance_across_recovery",
    "recovery_success_does_not_upgrade_epistemic_state_or_claim_maturity",
    "substrate_state_does_not_force_a_fixed_ark_tier",
    "request_only_ark_capabilities_declared_by_the_parent_registry",
    "delegate_ark_tier_selection_to_ark_mrs",
    "do_not_treat_ark_tier_rank_as_capability_inheritance",
    "do_not_treat_hash_integrity_as_authorship_authentication_or_truth",
    "live_parent_drift_requires_explicit_compatibility_re_evaluation",
    "source_design_inputs_are_noncanonical_until_explicitly_promoted",
    "integration_receivers_are_derived_and_do_not_become_source_evidence",
}

EXPECTED_SUBSTRATE_FIELDS = {
    "epistemic_state",
    "claim_maturity",
    "scenario",
    "register",
    "mode_and_bridge_state",
    "provenance",
    "visibility",
}

EXPECTED_INTEGRITY_WORDING = {
    "sha256_match": "byte identity verified against the stated SHA-256 digest",
    "signature_absent": "no digital-signature claim may be made without signature evidence",
}

EXPECTED_REFERENCE_PATTERNS = {
    "separate_published_or_parent_fixtures_from_project_authored_receivers",
    "deterministic_projection_is_not_evidence_for_underlying_claim",
    "state_reconstruction_limitations_explicitly",
    "prefer_dependency_free_offline_inspection_surfaces_when_practical",
    "derived_visual_audio_or_report_receiver_must_not_redefine_source_semantics",
}

EXPECTED_REFERENCE_SOURCE_FILES = {
    "README.md": "b97737d6a6642e03d83e0fb456019b65a3dab893",
    "LICENSE": "fbf3c76b9815faca9dd7a7846e6de532d3c2f155",
}

EXPECTED_QBRAID_ARCHIVE = {
    "ARCHITECTURE.md",
    "ARK_REPORT.md",
    "IMPLEMENTATION_PLAN.md",
    "INDEX.md",
    "MANIFEST.txt",
    "README.md",
    "SHA256SUMS",
    "SUBSTRATE_REPORT.md",
    "VERIFICATION-CERTIFICATE.txt",
}
EXPECTED_QBRAID_RECEIPTS = {
    "ARCHITECTURE.md",
    "ARK_REPORT.md",
    "IMPLEMENTATION_PLAN.md",
    "INDEX.md",
    "README.md",
    "SUBSTRATE_REPORT.md",
}


def load(path: str) -> dict:
    with (ROOT / path).open("r", encoding="utf-8") as fh:
        return json.load(fh)


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def _validate_artifact(artifact: object, expected: dict, code: str) -> None:
    require(isinstance(artifact, dict), code)
    path = artifact.get("path", "")
    blob = artifact.get("git_blob_sha1", "")
    require(isinstance(path, str) and bool(path), code)
    require(HEX40.fullmatch(blob) is not None, code)
    require(path == expected["path"], code)
    require(blob == expected["git_blob_sha1"], code)
    if "schema_version" in expected:
        require(artifact.get("schema_version") == expected["schema_version"], code)


def validate_parent_contracts(data: dict | None = None) -> dict:
    if data is None:
        data = load("ai/parent-contracts.json")
    require(isinstance(data, dict), "INT_PARENT_CONTRACT_INCOMPLETE")
    parents = data.get("parents", {})
    require(isinstance(parents, dict) and set(parents) == {"substrate", "ark"}, "INT_PARENT_CONTRACT_INCOMPLETE")
    for name, expected in EXPECTED_PARENT_IDENTITIES.items():
        parent = parents[name]
        require(isinstance(parent, dict), "INT_PARENT_CONTRACT_INCOMPLETE")
        require(parent.get("protocol") == expected["protocol"], "INT_PARENT_CONTRACT_INCOMPLETE")
        pin = parent.get("pinned_commit", "")
        require(HEX40.fullmatch(pin) is not None, "INT_PARENT_PIN_INVALID")
        require(pin == expected["pinned_commit"], "INT_PARENT_PIN_INVALID")
        _validate_artifact(parent.get("manifest"), expected["manifest"], "INT_PARENT_CONTRACT_INCOMPLETE")
        contracts = parent.get("contracts", [])
        require(isinstance(contracts, list), "INT_PARENT_CONTRACT_INCOMPLETE")
        actual_contracts = {}
        for artifact in contracts:
            require(isinstance(artifact, dict), "INT_PARENT_CONTRACT_INCOMPLETE")
            path = artifact.get("path", "")
            blob = artifact.get("git_blob_sha1", "")
            require(isinstance(path, str) and bool(path), "INT_PARENT_CONTRACT_INCOMPLETE")
            require(HEX40.fullmatch(blob) is not None, "INT_PARENT_CONTRACT_INCOMPLETE")
            require(path not in actual_contracts, "INT_PARENT_CONTRACT_INCOMPLETE")
            actual_contracts[path] = blob
        require(actual_contracts == expected["contracts"], "INT_PARENT_CONTRACT_INCOMPLETE")

    ark = parents["ark"]
    ids = ark.get("observed_tier_ids", [])
    require(ids == ["T0", "T1", "T2", "T3", "T4", "T5"], "INT_PARENT_CONTRACT_INCOMPLETE")
    require(ark.get("observed_implemented_tiers", []) == ["T0", "T1", "T2", "T3", "T4"], "INT_PARENT_CONTRACT_INCOMPLETE")
    require("never infer or inherit undeclared capabilities" in ark.get("mrs_rule", ""), "INT_CAPABILITY_REDEFINITION")
    return data


def validate_integration(data: dict | None = None) -> dict:
    if data is None:
        data = load("ai/integration-contract.json")
    require(isinstance(data, dict), "INT_PARENT_CONTRACT_INCOMPLETE")
    require(data.get("core_invariant") == "INTEGRATION_MUST_NOT_INCREASE_SEMANTIC_AUTHORITY", "INT_PARENT_CONTRACT_INCOMPLETE")
    boundary = data.get("projection_boundary", {})
    require(isinstance(boundary, dict), "INT_RECEIVER_AUTHORITY_ESCALATION")
    require(boundary.get("receiver_is_source") is False and boundary.get("receiver_is_evidence") is False, "INT_RECEIVER_AUTHORITY_ESCALATION")
    rules = data.get("composition_rules", [])
    require(isinstance(rules, list) and len(rules) == len(set(rules)), "INT_PARENT_CONTRACT_INCOMPLETE")
    require(set(rules) == EXPECTED_COMPOSITION_RULES, "INT_PARENT_CONTRACT_INCOMPLETE")
    forbidden = set(data.get("forbidden", []))
    require("canonical_epistemic_to_fixed_tier_mapping" in forbidden, "INT_STATE_TIER_COUPLING_FORBIDDEN")
    require("integration_receiver_promoted_to_source" in forbidden, "INT_RECEIVER_AUTHORITY_ESCALATION")
    return data


def validate_policy(data: dict | None = None, parents: dict | None = None) -> dict:
    if data is None:
        data = load("ai/epistemic-recovery-policy.json")
    if parents is None:
        parents = validate_parent_contracts()
    require(isinstance(data, dict), "INT_PARENT_CONTRACT_INCOMPLETE")
    fields = data.get("substrate_fields_to_preserve", [])
    require(isinstance(fields, list) and len(fields) == len(set(fields)), "INT_PARENT_CONTRACT_INCOMPLETE")
    require(set(fields) == EXPECTED_SUBSTRATE_FIELDS, "INT_PARENT_CONTRACT_INCOMPLETE")
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
    if data is None:
        data = load("ai/integrity-semantics.json")
    require(isinstance(data, dict), "INT_INTEGRITY_SEMANTICS_INVALID")
    invariants = set(data.get("invariants", []))
    required = {
        "digest_match_does_not_prove_authorship",
        "digest_match_does_not_prove_original_source",
        "digest_match_does_not_prove_content_truth",
        "sha256_digest_is_not_a_digital_signature",
    }
    require(required.issubset(invariants), "INT_INTEGRITY_SEMANTICS_INVALID")
    require(data.get("required_wording") == EXPECTED_INTEGRITY_WORDING, "INT_INTEGRITY_SEMANTICS_INVALID")
    return data


def validate_qbraid(source: dict | None = None, findings: dict | None = None) -> dict:
    if source is None:
        source = load("specimens/qbraid-foundation/source-manifest.json")
    if findings is None:
        findings = load("specimens/qbraid-foundation/findings.json")
    require(isinstance(source, dict) and isinstance(findings, dict), "INT_QBRAID_SPECIMEN_INVALID")
    source_id = source.get("id")
    require(isinstance(source_id, str) and bool(source_id), "INT_QBRAID_SPECIMEN_INVALID")
    require(findings.get("source_id") == source_id, "INT_QBRAID_SPECIMEN_INVALID")
    require(source.get("canonical_or_derived") == "noncanonical_design_input", "INT_QBRAID_SPECIMEN_INVALID")
    require(source.get("source_bytes_copied") is False, "INT_QBRAID_SPECIMEN_INVALID")
    bundle = source.get("bundle", {})
    require(isinstance(bundle, dict), "INT_QBRAID_SPECIMEN_INVALID")
    require(bundle.get("filename") == "QSOL-INT-REPORT-BUNDLE-v1.0.0.zip", "INT_QBRAID_SPECIMEN_INVALID")
    require(bundle.get("observed_sha256") == "745a62a5360165f019ea4e2195eee5fac8c6f3eb9eeeb07916934611d253fd68", "INT_QBRAID_SPECIMEN_INVALID")
    require(HEX64.fullmatch(bundle.get("observed_sha256", "")) is not None, "INT_QBRAID_SPECIMEN_INVALID")
    archive = source.get("archive_entries", [])
    receipts = source.get("receipt_entries", [])
    require(isinstance(archive, list) and all(isinstance(x, str) and x for x in archive), "INT_QBRAID_SPECIMEN_INVALID")
    require(isinstance(receipts, list) and all(isinstance(x, str) and x for x in receipts), "INT_QBRAID_SPECIMEN_INVALID")
    require(len(archive) == len(set(archive)), "INT_QBRAID_SPECIMEN_INVALID")
    require(len(receipts) == len(set(receipts)), "INT_QBRAID_SPECIMEN_INVALID")
    require(len(archive) == bundle.get("archive_entry_count"), "INT_QBRAID_SPECIMEN_INVALID")
    require(len(receipts) == bundle.get("receipt_entry_count"), "INT_QBRAID_SPECIMEN_INVALID")
    archive_set = set(archive)
    receipt_set = set(receipts)
    require(receipt_set.issubset(archive_set), "INT_QBRAID_SPECIMEN_INVALID")
    require(receipt_set != archive_set, "INT_QBRAID_RECEIPT_COVERAGE_MISMATCH")
    require(archive_set == EXPECTED_QBRAID_ARCHIVE, "INT_QBRAID_SPECIMEN_INVALID")
    require(receipt_set == EXPECTED_QBRAID_RECEIPTS, "INT_QBRAID_SPECIMEN_INVALID")
    require(bundle.get("receipt_covers_all_archive_entries") is False, "INT_QBRAID_SPECIMEN_INVALID")
    finding_list = findings.get("findings", [])
    require(isinstance(finding_list, list) and len(finding_list) == 5, "INT_QBRAID_SPECIMEN_INVALID")
    require({x.get("id") for x in finding_list if isinstance(x, dict)} == {"QB-001", "QB-002", "QB-003", "QB-004", "QB-005"}, "INT_QBRAID_SPECIMEN_INVALID")
    require(findings.get("preserve_source_errors") is True, "INT_QBRAID_SPECIMEN_INVALID")
    return source


def validate_references(data: dict | None = None) -> dict:
    if data is None:
        data = load("ai/reference-methodologies.json")
    require(isinstance(data, dict), "INT_REFERENCE_METHODOLOGY_INVALID")
    refs = data.get("references", [])
    require(isinstance(refs, list) and len(refs) == 1, "INT_REFERENCE_METHODOLOGY_INVALID")
    ref = refs[0]
    require(ref.get("id") == "reference.substratism_viz", "INT_REFERENCE_METHODOLOGY_INVALID")
    require(ref.get("canonical_for_int") is False and ref.get("parent_protocol") is False, "INT_REFERENCE_METHODOLOGY_INVALID")
    require(ref.get("license") == "MIT", "INT_REFERENCE_METHODOLOGY_INVALID")
    require(ref.get("pinned_commit") == "7ba38cf90ca52298aed3819b30f4098f49b36813", "INT_REFERENCE_METHODOLOGY_INVALID")
    patterns = ref.get("adopted_patterns", [])
    require(isinstance(patterns, list) and len(patterns) == len(set(patterns)), "INT_REFERENCE_METHODOLOGY_INVALID")
    require(set(patterns) == EXPECTED_REFERENCE_PATTERNS, "INT_REFERENCE_METHODOLOGY_INVALID")
    source_files = ref.get("source_files", [])
    require(isinstance(source_files, list), "INT_REFERENCE_METHODOLOGY_INVALID")
    actual_source_files = {}
    for artifact in source_files:
        require(isinstance(artifact, dict), "INT_REFERENCE_METHODOLOGY_INVALID")
        path = artifact.get("path", "")
        blob = artifact.get("git_blob_sha1", "")
        require(isinstance(path, str) and bool(path), "INT_REFERENCE_METHODOLOGY_INVALID")
        require(HEX40.fullmatch(blob) is not None, "INT_REFERENCE_METHODOLOGY_INVALID")
        require(path not in actual_source_files, "INT_REFERENCE_METHODOLOGY_INVALID")
        actual_source_files[path] = blob
    require(actual_source_files == EXPECTED_REFERENCE_SOURCE_FILES, "INT_REFERENCE_METHODOLOGY_INVALID")
    require(ref.get("int_translation", {}).get("invariant") == "AUTHORED_RECEIVER != SOURCE_EVIDENCE", "INT_RECEIVER_AUTHORITY_ESCALATION")
    return data


def validate(manifest: dict | None = None) -> None:
    if manifest is None:
        manifest = load("manifest.json")
    require(isinstance(manifest, dict), "INT_MANIFEST_ENTRYPOINT_INVALID")
    require(manifest.get("protocol") == "QSOL-INT", "INT_PARENT_CONTRACT_INCOMPLETE")
    entrypoints = manifest.get("entrypoints", {})
    require(entrypoints == EXPECTED_ENTRYPOINTS, "INT_MANIFEST_ENTRYPOINT_INVALID")
    for path in entrypoints.values():
        require((ROOT / path).is_file(), "INT_MANIFEST_ENTRYPOINT_INVALID")
    require((ROOT / entrypoints["validator"]).resolve() == Path(__file__).resolve(), "INT_MANIFEST_ENTRYPOINT_INVALID")

    # Load contracts through manifest-declared entrypoints so a successful
    # validation proves that machine consumers and the validator use the same files.
    load(entrypoints["bootstrap"])
    parents = validate_parent_contracts(load(entrypoints["parent_contracts"]))
    validate_integration(load(entrypoints["integration_contract"]))
    validate_policy(load(entrypoints["epistemic_recovery_policy"]), parents=parents)
    validate_integrity(load(entrypoints["integrity_semantics"]))
    source = validate_qbraid()
    refs = validate_references(load(entrypoints["reference_methodologies"]))
    print(
        "QSOL_INT_OK "
        f"parents={len(parents['parents'])} "
        f"ark_tiers={len(parents['parents']['ark']['observed_tier_ids'])} "
        f"qbraid_archive={source['bundle']['archive_entry_count']} "
        f"qbraid_receipts={source['bundle']['receipt_entry_count']} "
        f"references={len(refs['references'])}"
    )


if __name__ == "__main__":
    validate()
