# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "adapters/index.json"
PARENT_PATH = ROOT / "ai/parent-contracts.json"

ADAPTERS = ("generic", "openai", "ollama")
FIXTURES = (
    "valid",
    "unknown",
    "conflict",
    "satire",
    "cross-mode",
    "missing-provenance",
    "drift",
    "invalid",
)
FIXTURE_PATHS = tuple(f"adapters/fixtures/{name}.json" for name in FIXTURES)
ANNOTATIONS = {
    "epistemic_state",
    "claim_maturity",
    "scenario",
    "register",
    "provenance",
    "mode",
    "drift",
}
DRIFT = {
    "NO_DRIFT",
    "CONTENT_DRIFT",
    "SCHEMA_DRIFT",
    "SEMANTIC_DRIFT",
    "CAPABILITY_DRIFT",
    "AUTHORITY_DRIFT",
    "BREAKING_DRIFT",
    "SOURCE_UNAVAILABLE",
}
FAILURES = {
    "INT_ADAPTER_CONTRACT_INVALID",
    "INT_ADAPTER_INDEX_INVALID",
    "INT_ADAPTER_FIXTURE_INVALID",
    "INT_ADAPTER_ENVELOPE_INVALID",
    "INT_ADAPTER_PROVENANCE_REQUIRED",
    "INT_ADAPTER_CONFLICT_PROVENANCE_INCOMPLETE",
    "INT_CROSS_MODE_BRIDGE_REQUIRED",
    "INT_ADAPTER_DRIFT_REVIEW_REQUIRED",
    "INT_ADAPTER_SEMANTIC_LOSS",
    "INT_ADAPTER_REPORT_INVALID",
    "INT_ADAPTER_UNKNOWN",
}


class AdapterFailure(ValueError):
    def __init__(self, code: str, message: str, decision: str = "reject"):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.decision = decision


def require(ok: bool, code: str, message: str, decision: str = "reject") -> None:
    if not ok:
        raise AdapterFailure(code, message, decision)


def load_json(path: str | Path, code: str = "INT_ADAPTER_INDEX_INVALID") -> Any:
    target = Path(path)
    target = target if target.is_absolute() else ROOT / target
    try:
        return json.loads(target.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AdapterFailure(code, f"cannot read JSON {target}: {exc}") from exc


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


def _hex(value: Any, length: int) -> bool:
    return (
        isinstance(value, str)
        and len(value) == length
        and all(char in "0123456789abcdef" for char in value)
    )


def _contract(contract: dict) -> None:
    require(
        isinstance(contract, dict)
        and contract.get("type") == "qsol-int-adapter-contract"
        and contract.get("protocol") == "QSOL-INT/ADAPTER/1"
        and contract.get("version") == "1.0.0"
        and contract.get("status") == "implemented",
        "INT_ADAPTER_CONTRACT_INVALID",
        "contract identity invalid",
    )
    require(
        contract.get("adapters") == list(ADAPTERS)
        and set(
            contract.get("canonical_envelope", {}).get(
                "required_annotations", []
            )
        )
        == ANNOTATIONS,
        "INT_ADAPTER_CONTRACT_INVALID",
        "adapter registry invalid",
    )
    authority = contract.get("authority", {})
    require(
        authority
        == {
            "adapters_are_transport_only": True,
            "adapter_output_is_source_evidence": False,
            "adapter_may_redefine_parent_semantics": False,
            "runtime_model_identity_is_configuration_not_int_fact": True,
        },
        "INT_ADAPTER_CONTRACT_INVALID",
        "authority boundary invalid",
    )
    rules = contract.get("rules")
    require(
        isinstance(rules, list)
        and len(rules) == len(set(rules))
        and {
            "messages_and_annotations_are_preserved_exactly",
            "material_cross_mode_inference_requires_a_declared_bridge",
            "transport_templates_embed_no_api_keys",
            "adapter_receipts_prove_serialization_identity_not_truth_authorship_or_compatibility",
        }.issubset(rules),
        "INT_ADAPTER_CONTRACT_INVALID",
        "rules invalid",
    )
    codes = contract.get("failure_codes")
    require(
        isinstance(codes, list)
        and len(codes) == len(set(codes))
        and set(codes) == FAILURES,
        "INT_ADAPTER_CONTRACT_INVALID",
        "failure registry invalid",
    )


def validate_index(index: dict | None = None):
    index = load_json(INDEX_PATH) if index is None else index
    require(
        isinstance(index, dict)
        and index.get("type") == "qsol-int-adapter-fixture-index"
        and index.get("protocol") == "QSOL-INT/ADAPTER/1"
        and index.get("version") == "1.0.0",
        "INT_ADAPTER_INDEX_INVALID",
        "index identity invalid",
    )
    require(
        index.get("adapters") == list(ADAPTERS)
        and index.get("derived_reports_are_noncanonical") is True,
        "INT_ADAPTER_INDEX_INVALID",
        "index boundary invalid",
    )

    contract = load_json(
        index.get("contract", ""),
        "INT_ADAPTER_CONTRACT_INVALID",
    )
    _contract(contract)
    require(
        index.get("contract") == "ai/adapter-contract.json"
        and index.get("contract_sha256") == canonical_sha256(contract),
        "INT_ADAPTER_INDEX_INVALID",
        "contract receipt invalid",
    )

    paths = index.get("fixtures")
    receipts = index.get("fixture_sha256")
    expected = index.get("expected")
    require(
        tuple(paths or []) == FIXTURE_PATHS
        and set(index.get("required_fixture_kinds", [])) == set(FIXTURES),
        "INT_ADAPTER_INDEX_INVALID",
        "fixture registry invalid",
    )
    require(
        isinstance(receipts, dict)
        and set(receipts) == set(paths)
        and isinstance(expected, dict)
        and set(expected) == set(paths),
        "INT_ADAPTER_INDEX_INVALID",
        "fixture metadata invalid",
    )

    fixtures = []
    for path in paths:
        fixture = load_json(path, "INT_ADAPTER_FIXTURE_INVALID")
        require(
            receipts[path] == canonical_sha256(fixture),
            "INT_ADAPTER_INDEX_INVALID",
            f"fixture receipt invalid {path}",
        )
        outcome = expected[path]
        require(
            isinstance(outcome, dict)
            and outcome.get("decision") in {"allow", "block", "reject"}
            and "failure_code" in outcome,
            "INT_ADAPTER_INDEX_INVALID",
            f"fixture outcome invalid {path}",
        )
        fixtures.append((path, fixture, outcome))
    return index, fixtures


def _registries():
    substrate = (
        load_json(PARENT_PATH, "INT_ADAPTER_CONTRACT_INVALID")
        .get("parents", {})
        .get("substrate", {})
    )
    values = tuple(
        set(substrate.get(key, []))
        for key in (
            "observed_epistemic_states",
            "observed_claim_maturity_states",
            "observed_scenario_states",
            "observed_register_states",
        )
    )
    require(
        all(values),
        "INT_ADAPTER_CONTRACT_INVALID",
        "parent registries missing",
    )
    return values


def validate_envelope(envelope: dict) -> None:
    require(
        isinstance(envelope, dict)
        and envelope.get("type") == "qsol-int-adapter-envelope"
        and envelope.get("protocol") == "QSOL-INT/ADAPTER/1"
        and envelope.get("version") == "1.0.0"
        and isinstance(envelope.get("id"), str)
        and bool(envelope["id"]),
        "INT_ADAPTER_ENVELOPE_INVALID",
        "envelope identity invalid",
    )

    messages = envelope.get("messages")
    require(
        isinstance(messages, list) and bool(messages),
        "INT_ADAPTER_ENVELOPE_INVALID",
        "messages missing",
    )
    for message in messages:
        require(
            isinstance(message, dict)
            and isinstance(message.get("role"), str)
            and bool(message["role"])
            and isinstance(message.get("content"), str),
            "INT_ADAPTER_ENVELOPE_INVALID",
            "message invalid",
        )

    annotations = envelope.get("annotations")
    require(
        isinstance(annotations, dict) and ANNOTATIONS.issubset(annotations),
        "INT_ADAPTER_ENVELOPE_INVALID",
        "annotations missing",
    )

    states, maturity, scenarios, registers = _registries()
    require(
        annotations.get("epistemic_state") in states
        and annotations.get("claim_maturity") in maturity
        and annotations.get("scenario") in scenarios
        and annotations.get("register") in registers,
        "INT_ADAPTER_ENVELOPE_INVALID",
        "annotation value invalid",
    )

    provenance = annotations.get("provenance")
    require(
        isinstance(provenance, list),
        "INT_ADAPTER_ENVELOPE_INVALID",
        "provenance invalid",
    )
    for source in provenance:
        require(
            isinstance(source, dict)
            and isinstance(source.get("source_id"), str)
            and bool(source["source_id"])
            and isinstance(source.get("locator"), str)
            and bool(source["locator"]),
            "INT_ADAPTER_ENVELOPE_INVALID",
            "source invalid",
        )

    if annotations["epistemic_state"] in {
        "known",
        "retrieved",
        "inferred",
        "conflict",
    }:
        require(
            bool(provenance),
            "INT_ADAPTER_PROVENANCE_REQUIRED",
            "provenance required",
        )

    if annotations["epistemic_state"] == "conflict":
        distinct_provenance = {
            (source["source_id"], source["locator"])
            for source in provenance
        }
        require(
            len(distinct_provenance) >= 2,
            "INT_ADAPTER_CONFLICT_PROVENANCE_INCOMPLETE",
            "conflict needs two distinct sources",
        )

    mode = annotations.get("mode")
    require(
        isinstance(mode, dict)
        and isinstance(mode.get("primary"), str)
        and bool(mode["primary"])
        and isinstance(mode.get("secondary"), list)
        and all(isinstance(value, str) for value in mode["secondary"])
        and isinstance(mode.get("bridges"), list)
        and all(isinstance(value, str) for value in mode["bridges"])
        and isinstance(mode.get("material_cross_domain"), bool),
        "INT_ADAPTER_ENVELOPE_INVALID",
        "mode invalid",
    )
    if mode["material_cross_domain"] and not mode["bridges"]:
        raise AdapterFailure(
            "INT_CROSS_MODE_BRIDGE_REQUIRED",
            "cross-mode bridge missing",
            "block",
        )

    drift = annotations.get("drift")
    require(
        isinstance(drift, dict)
        and drift.get("status") in DRIFT
        and isinstance(drift.get("review_required"), bool),
        "INT_ADAPTER_ENVELOPE_INVALID",
        "drift invalid",
    )
    if drift["status"] != "NO_DRIFT":
        require(
            drift["review_required"] is True,
            "INT_ADAPTER_DRIFT_REVIEW_REQUIRED",
            "drift must remain review-required",
        )


def _instructions(annotations: dict) -> str:
    return (
        "QSOL-INT/ADAPTER/1 transport annotations follow. "
        "They are metadata, not source evidence, and must not be reclassified.\n"
        + canonical_bytes(annotations).decode("utf-8")
    )


def process(adapter: str, envelope: dict) -> dict:
    if adapter not in ADAPTERS:
        return {
            "type": "qsol-int-adapter-output",
            "protocol": "QSOL-INT/ADAPTER/1",
            "version": "1.0.0",
            "adapter": adapter,
            "decision": "reject",
            "failure_code": "INT_ADAPTER_UNKNOWN",
            "error": f"unknown adapter {adapter}",
            "transport": None,
        }

    try:
        validate_envelope(envelope)
    except AdapterFailure as exc:
        return {
            "type": "qsol-int-adapter-output",
            "protocol": "QSOL-INT/ADAPTER/1",
            "version": "1.0.0",
            "adapter": adapter,
            "decision": exc.decision,
            "failure_code": exc.code,
            "error": exc.message,
            "transport": None,
        }

    annotations = copy.deepcopy(envelope["annotations"])
    messages = copy.deepcopy(envelope["messages"])
    envelope_sha256 = canonical_sha256(envelope)
    annotations_sha256 = canonical_sha256(annotations)
    receipt = {
        "source_envelope_sha256": envelope_sha256,
        "messages_sha256": canonical_sha256(messages),
        "annotations_sha256": annotations_sha256,
        "annotations": annotations,
        "transport_only": True,
        "fact_redefinition": False,
        "digest_proves_truth_or_authorship": False,
    }

    if adapter == "generic":
        transport = {
            "kind": "generic_json",
            "payload": {
                "messages": messages,
                "qsol_int": annotations,
            },
        }
    elif adapter == "openai":
        transport = {
            "kind": "openai_compatible_request_template",
            "model": "REPLACE_WITH_EXACT_MODEL_ID",
            "messages": [
                {
                    "role": "developer",
                    "content": _instructions(annotations),
                },
                *messages,
            ],
            "metadata": {
                "qsol_int_envelope_sha256": envelope_sha256,
                "qsol_int_annotations_sha256": annotations_sha256,
                "qsol_int_transport_only": "true",
            },
        }
    else:
        transport = {
            "kind": "ollama_request_template",
            "model": "REPLACE_WITH_EXACT_MODEL_TAG",
            "system": _instructions(annotations),
            "messages": messages,
            "options": {},
        }

    return {
        "type": "qsol-int-adapter-output",
        "protocol": "QSOL-INT/ADAPTER/1",
        "version": "1.0.0",
        "adapter": adapter,
        "decision": "allow",
        "failure_code": None,
        "source_envelope_id": envelope["id"],
        "semantic_receipt": receipt,
        "transport": transport,
    }


def validate_output(output: dict, envelope: dict) -> None:
    require(
        isinstance(output, dict)
        and output.get("type") == "qsol-int-adapter-output"
        and output.get("protocol") == "QSOL-INT/ADAPTER/1"
        and output.get("version") == "1.0.0"
        and output.get("decision") == "allow"
        and output.get("failure_code") is None
        and output.get("source_envelope_id") == envelope.get("id"),
        "INT_ADAPTER_SEMANTIC_LOSS",
        "output identity invalid",
    )

    adapter = output.get("adapter")
    require(
        adapter in ADAPTERS,
        "INT_ADAPTER_SEMANTIC_LOSS",
        "adapter invalid",
    )

    receipt = output.get("semantic_receipt")
    require(
        isinstance(receipt, dict)
        and receipt.get("source_envelope_sha256") == canonical_sha256(envelope)
        and receipt.get("messages_sha256")
        == canonical_sha256(envelope["messages"])
        and receipt.get("annotations_sha256")
        == canonical_sha256(envelope["annotations"])
        and receipt.get("annotations") == envelope["annotations"],
        "INT_ADAPTER_SEMANTIC_LOSS",
        "semantic receipt invalid",
    )
    require(
        receipt.get("transport_only") is True
        and receipt.get("fact_redefinition") is False
        and receipt.get("digest_proves_truth_or_authorship") is False,
        "INT_ADAPTER_SEMANTIC_LOSS",
        "authority boundary invalid",
    )

    transport = output.get("transport")
    annotations_text = canonical_bytes(envelope["annotations"]).decode("utf-8")
    require(
        isinstance(transport, dict),
        "INT_ADAPTER_SEMANTIC_LOSS",
        "transport missing",
    )

    if adapter == "generic":
        require(
            transport
            == {
                "kind": "generic_json",
                "payload": {
                    "messages": envelope["messages"],
                    "qsol_int": envelope["annotations"],
                },
            },
            "INT_ADAPTER_SEMANTIC_LOSS",
            "generic semantics changed",
        )
    elif adapter == "openai":
        require(
            set(transport) == {"kind", "model", "messages", "metadata"}
            and transport.get("kind") == "openai_compatible_request_template"
            and transport.get("model") == "REPLACE_WITH_EXACT_MODEL_ID",
            "INT_ADAPTER_SEMANTIC_LOSS",
            "OpenAI shape invalid",
        )
        messages = transport.get("messages")
        require(
            isinstance(messages, list)
            and messages[1:] == envelope["messages"]
            and messages[0].get("role") == "developer"
            and annotations_text in messages[0].get("content", ""),
            "INT_ADAPTER_SEMANTIC_LOSS",
            "OpenAI semantics changed",
        )
        require(
            transport.get("metadata")
            == {
                "qsol_int_envelope_sha256": canonical_sha256(envelope),
                "qsol_int_annotations_sha256": canonical_sha256(
                    envelope["annotations"]
                ),
                "qsol_int_transport_only": "true",
            },
            "INT_ADAPTER_SEMANTIC_LOSS",
            "OpenAI metadata invalid",
        )
    else:
        require(
            set(transport)
            == {"kind", "model", "system", "messages", "options"}
            and transport.get("kind") == "ollama_request_template"
            and transport.get("model") == "REPLACE_WITH_EXACT_MODEL_TAG"
            and transport.get("messages") == envelope["messages"]
            and annotations_text in transport.get("system", "")
            and transport.get("options") == {},
            "INT_ADAPTER_SEMANTIC_LOSS",
            "Ollama semantics changed",
        )
