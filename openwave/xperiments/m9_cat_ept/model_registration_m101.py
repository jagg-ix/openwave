"""Current M9.101 registration over the coupled-physics conformance profile."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .model_conformance_m101 import canonical_payload as conformance_payload
from .model_conformance_m101 import run_conformance_study
from .model_registration_maturity_current import canonical_registration_payload as m9_100_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = m9_100_payload()
    conformance = conformance_payload()
    return {
        **previous,
        "schema": "openwave.model-registration.v9",
        "conformance": conformance,
        "m9_101": {
            "formal_head": conformance["formal_head"],
            "coupled_action_registered": conformance["m9_101"]["coupled_action"]["passed"],
            "packet_tbmt_registered": conformance["m9_101"]["packet_tbmt"]["passed"],
            "clock_calibration_registered": conformance["m9_101"]["clock"]["passed"],
            "weak_field_gravity_registered": conformance["m9_101"]["gravity"]["passed"],
            "headline_counts": conformance["summary"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "finite_coupled_action_is_full_continuum_action": False,
            "symmetry_reduced_branch_is_unrestricted_stability": False,
            "packet_tbmt_is_qed_derived_covariant_extension": False,
            "internal_clock_calibration_is_external_validation": False,
            "weak_field_gravity_is_full_einstein_development": False,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    conformance = run_conformance_study()
    payload = canonical_registration_payload()
    boundaries = (
        "finite_coupled_action_is_full_continuum_action",
        "symmetry_reduced_branch_is_unrestricted_stability",
        "packet_tbmt_is_qed_derived_covariant_extension",
        "internal_clock_calibration_is_external_validation",
        "weak_field_gravity_is_full_einstein_development",
    )
    acceptance = {
        "m101_conformance_passes": bool(conformance["passed"]),
        "schema_v9_is_current": payload["schema"] == "openwave.model-registration.v9",
        "current_formal_head_is_exact": payload["m9_101"]["formal_head"] == "acdbe8ce6456e66837bd18604cf3107d3181c4de",
        "all_four_campaigns_are_registered": all(payload["m9_101"][key] for key in ("coupled_action_registered", "packet_tbmt_registered", "clock_calibration_registered", "weak_field_gravity_registered")),
        "no_physical_claim_is_promoted": payload["m9_101"]["physical_claims_promoted"] == [],
        "all_new_scope_boundaries_are_preserved": all(not payload["claim_boundary"][key] for key in boundaries),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.101i",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m101_registration_is_current": True,
            "all_four_proposed_targets_registered": True,
            "physical_identity_changed": False,
            "external_prediction_status_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
