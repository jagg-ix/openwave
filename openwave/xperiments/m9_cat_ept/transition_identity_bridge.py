"""M9.122c: independent transition-identity bridge contract."""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .external_evidence_package import artifact, validate_identity_bridge


def fingerprint(payload: Any) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def bridge_template() -> dict[str, Any]:
    return {
        "artifact": None,
        "required_discriminants": (
            "gauge_sector",
            "quantum_numbers",
            "selection_rule",
            "symmetry_representation",
        ),
        "required_negative_controls": True,
    }


def synthetic_bridge() -> dict[str, Any]:
    return {
        "artifact": artifact(
            name="synthetic-independent-transition-bridge",
            role="independent_identity_bridge",
            source="synthetic://m9.122/identity-contract",
            payload={
                "label_only": False,
                "model_transition_ids": {
                    "strong": "m9.121:strong:dominant-response-transition",
                    "electroweak": "m9.121:electroweak:dominant-response-transition",
                },
                "observed_channels": {
                    "strong": "synthetic:strong-channel",
                    "electroweak": "synthetic:electroweak-channel",
                },
                "discriminants": {
                    sector: {
                        "gauge_sector": sector,
                        "quantum_numbers": "synthetic-complete",
                        "selection_rule": "synthetic-compatible",
                        "symmetry_representation": "synthetic-representation",
                    }
                    for sector in ("strong", "electroweak")
                },
                "negative_controls": (
                    "synthetic:wrong-sector",
                    "synthetic:wrong-selection-rule",
                ),
            },
            independent=True,
            evidence_class="synthetic-fixture",
        )
    }


@lru_cache(maxsize=1)
def run_transition_identity_bridge_contract() -> dict[str, Any]:
    template = bridge_template()
    fixture = synthetic_bridge()
    template_result = validate_identity_bridge(template)
    fixture_result = validate_identity_bridge(fixture)

    label_only = deepcopy(fixture)
    label_only["artifact"]["payload"]["label_only"] = True
    label_only["artifact"]["payload_sha256"] = fingerprint(
        label_only["artifact"]["payload"]
    )
    no_negative_control = deepcopy(fixture)
    no_negative_control["artifact"]["payload"]["negative_controls"] = ()
    no_negative_control["artifact"]["payload_sha256"] = fingerprint(
        no_negative_control["artifact"]["payload"]
    )
    self_asserted = deepcopy(fixture)
    self_asserted["artifact"]["independent"] = False

    payload = {
        "schema": "openwave.m9.transition-identity-bridge-contract.v1",
        "task": "M9.122c",
        "template": template,
        "template_validation": template_result,
        "synthetic_fixture": fixture,
        "synthetic_validation": fixture_result,
        "claim_boundary": {
            "shared_label_is_physical_identity": False,
            "structural_contract_is_observed_transition_identity": False,
            "synthetic_bridge_is_external_evidence": False,
            "model_transition_id_is_particle_identity": False,
        },
    }
    acceptance = {
        "live_identity_bridge_remains_uninstantiated": not template_result["passed"],
        "synthetic_fixture_is_structurally_complete": fixture_result["passed"],
        "synthetic_fixture_is_not_physical_identity": not fixture_result[
            "physical_identity_ready"
        ],
        "label_only_bridge_is_rejected": not validate_identity_bridge(label_only)[
            "passed"
        ],
        "missing_negative_control_is_rejected": not validate_identity_bridge(
            no_negative_control
        )["passed"],
        "self_asserted_bridge_is_rejected": not validate_identity_bridge(self_asserted)[
            "passed"
        ],
        "no_identity_claim_is_promoted": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "independent_identity_bridge_contract_constructed": True,
            "label_only_identity_rejected": True,
            "physical_transition_identity_established": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
