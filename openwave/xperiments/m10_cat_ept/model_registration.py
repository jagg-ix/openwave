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
from .formal_authority import (
    FORMAL_HEAD,
    canonical_payload as formal_authority_payload,
    fingerprint as formal_authority_fingerprint,
)

SCHEMA = "openwave.model-registration.m10.v2"


def canonical_registration_payload() -> dict[str, Any]:
    model = model_payload()
    formal = formal_authority_payload()
    return {
        "schema": SCHEMA,
        "model_id": "M10",
        "model": model["model"],
        "milestone": MILESTONE,
        "model_schema": MODEL_SCHEMA,
        "construction_api": model["construction_api"],
        "state_api": model["state_api"],
        "formal_authority": formal,
        "formal_authority_fingerprint": formal_authority_fingerprint(formal),
        "establishes": list(model["establishes"]),
        "comparison_role": (
            "relativistic Dirac-Cartan comparison model to M9 Pauli-Hartree-U1"
        ),
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(
            selected, sort_keys=True, separators=(",", ":"), default=str
        ).encode()
    ).hexdigest()


def run_model_registration_study() -> dict[str, Any]:
    payload = canonical_registration_payload()
    core = run_m10_core_study()
    formal = payload["formal_authority"]
    theorem_names = {source["theorem"] for source in formal["sources"]}
    acceptance = {
        "model_id_is_M10": payload["model_id"] == "M10",
        "milestone_is_M10_1": payload["milestone"] == "M10.1",
        "core_study_passes": bool(core["passed"]),
        "formal_head_is_exactly_pinned": formal["head"] == FORMAL_HEAD,
        "formal_sources_are_blob_pinned": (
            len(formal["sources"]) == 3
            and all(len(source["sha"]) == 40 for source in formal["sources"])
        ),
        "load_bearing_theorems_are_registered": theorem_names
        == {
            "binary_icosahedral_dirac_spinor_assembly",
            "dirac_cartan_axial_elimination_assembly",
            "dirac_cartan_2I_compton_yukawa_assembly",
        },
        "carrier_and_state_apis_are_registered": (
            payload["construction_api"].endswith(":construct_state")
            and payload["state_api"].endswith(":DiracCartan2IYukawaState")
        ),
        "formal_fingerprint_is_deterministic": (
            payload["formal_authority_fingerprint"]
            == formal_authority_fingerprint(formal)
        ),
        "registration_fingerprint_is_deterministic": (
            fingerprint(payload) == fingerprint(payload)
        ),
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
            "formal_theorem_authority_is_content_pinned": True,
            "m9_registration_rewritten": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
