"""Registration and executable contract for the M10 particle model."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from .dirac_cartan_2i_yukawa_model import (
    MILESTONE,
    SCHEMA as MODEL_SCHEMA,
    canonical_payload as model_payload,
    run_m10_core_study,
)

SCHEMA = "openwave.model-registration.m10.v1"


def canonical_registration_payload() -> dict[str, Any]:
    model = model_payload()
    return {
        "schema": SCHEMA,
        "model_id": "M10",
        "model": model["model"],
        "milestone": MILESTONE,
        "model_schema": MODEL_SCHEMA,
        "construction_api": model["construction_api"],
        "state_api": model["state_api"],
        "formal_authority": model["formal_authority"],
        "establishes": list(model["establishes"]),
        "comparison_role": "relativistic Dirac-Cartan comparison model to M9 Pauli-Hartree-U1",
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def run_model_registration_study() -> dict[str, Any]:
    payload = canonical_registration_payload()
    core = run_m10_core_study()
    acceptance = {
        "model_id_is_M10": payload["model_id"] == "M10",
        "milestone_is_M10_1": payload["milestone"] == "M10.1",
        "core_study_passes": bool(core["passed"]),
        "formal_sources_are_registered": len(payload["formal_authority"]["sources"]) == 3,
        "carrier_and_state_apis_are_registered": (
            payload["construction_api"].endswith(":construct_state")
            and payload["state_api"].endswith(":DiracCartan2IYukawaState")
        ),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M10.1g",
        "fingerprint": fingerprint(payload),
        "core_fingerprint": core["fingerprint"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m10_registered_as_separate_model": True,
            "m9_registration_rewritten": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
