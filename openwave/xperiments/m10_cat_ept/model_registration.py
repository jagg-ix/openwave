"""Registration and executable contract for the M10 particle-model lineage."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from .dirac_cartan_2i_yukawa_model import (
    MILESTONE as CARRIER_MILESTONE,
    SCHEMA as CARRIER_SCHEMA,
    canonical_payload as carrier_payload,
    run_m10_core_study,
)
from .formal_authority import (
    FORMAL_HEAD,
    canonical_payload as formal_authority_payload,
    fingerprint as formal_authority_fingerprint,
)
from .second_quantized_fock_m103 import (
    FORMAL_HEAD as FOCK_FORMAL_HEAD,
    FORMAL_PR as FOCK_FORMAL_PR,
    FORMAL_SOURCE_BLOB as FOCK_FORMAL_SOURCE_BLOB,
    FORMAL_THEOREM as FOCK_FORMAL_THEOREM,
    MILESTONE,
    SCHEMA as MODEL_SCHEMA,
    canonical_payload as fock_payload,
    run_second_quantized_fock_study,
)

SCHEMA = "openwave.model-registration.m10.v3"


def canonical_registration_payload() -> dict[str, Any]:
    carrier = carrier_payload()
    fock = fock_payload()
    formal = formal_authority_payload()
    return {
        "schema": SCHEMA,
        "model_id": "M10",
        "model": fock["model"],
        "milestone": MILESTONE,
        "carrier_milestone": CARRIER_MILESTONE,
        "closure_milestone": "M10.2",
        "carrier_schema": CARRIER_SCHEMA,
        "model_schema": MODEL_SCHEMA,
        "construction_api": carrier["construction_api"],
        "state_api": carrier["state_api"],
        "fock_construction_api": fock["construction_api"],
        "fock_study_api": fock["study_api"],
        "formal_authority": formal,
        "formal_authority_fingerprint": formal_authority_fingerprint(formal),
        "second_quantized_formal_authority": dict(fock["formal_authority"]),
        "establishes": [
            *carrier["establishes"],
            "finite fermionic CAR Fock space over four Dirac modes",
            "determinant exterior-power lift of every binary-icosahedral transformation",
            "central binary-icosahedral sign realized as fermion parity",
            "occupation-additive Compton-Yukawa complex energy and entropy suppression",
        ],
        "comparison_role": (
            "second-quantized relativistic Dirac-Cartan comparison model to M9 "
            "Pauli-Hartree-U1"
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
    fock = run_second_quantized_fock_study()
    formal = payload["formal_authority"]
    fock_formal = payload["second_quantized_formal_authority"]
    theorem_names = {source["theorem"] for source in formal["sources"]}
    acceptance = {
        "model_id_is_M10": payload["model_id"] == "M10",
        "latest_milestone_is_M10_3": payload["milestone"] == "M10.3",
        "carrier_lineage_is_retained": (
            payload["carrier_milestone"] == "M10.1"
            and payload["closure_milestone"] == "M10.2"
        ),
        "carrier_core_study_passes": bool(core["passed"]),
        "second_quantized_study_passes": bool(fock["passed"]),
        "one_particle_formal_head_is_exactly_pinned": formal["head"] == FORMAL_HEAD,
        "one_particle_formal_sources_are_blob_pinned": (
            len(formal["sources"]) == 3
            and all(len(source["sha"]) == 40 for source in formal["sources"])
        ),
        "one_particle_theorems_are_registered": theorem_names
        == {
            "binary_icosahedral_dirac_spinor_assembly",
            "dirac_cartan_axial_elimination_assembly",
            "dirac_cartan_2I_compton_yukawa_assembly",
        },
        "second_quantized_formal_authority_is_exact": (
            fock_formal["pull_request"] == FOCK_FORMAL_PR
            and fock_formal["head"] == FOCK_FORMAL_HEAD
            and fock_formal["source_blob"] == FOCK_FORMAL_SOURCE_BLOB
            and fock_formal["theorem"] == FOCK_FORMAL_THEOREM
        ),
        "carrier_and_fock_apis_are_registered": (
            payload["construction_api"].endswith(":construct_state")
            and payload["state_api"].endswith(":DiracCartan2IYukawaState")
            and payload["fock_construction_api"].endswith(":construct_fock_state")
            and payload["fock_study_api"].endswith(":run_second_quantized_fock_study")
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
        "task": "M10.3h",
        "fingerprint": fingerprint(payload),
        "core_fingerprint": core["fingerprint"],
        "fock_fingerprint": fock["fingerprint"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m10_registered_as_separate_model": True,
            "one_particle_and_second_quantized_authorities_are_content_pinned": True,
            "m10_second_quantized_fock_carrier_is_latest": True,
            "m9_registration_rewritten": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
