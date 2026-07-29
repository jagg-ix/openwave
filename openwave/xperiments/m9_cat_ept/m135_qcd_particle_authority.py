"""Composed M9.135 QCD and particle-physics authority."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from .qcd_particle_authority_m135 import run_qcd_particle_authority


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def run_m135_qcd_particle_authority() -> dict[str, Any]:
    qcd = run_qcd_particle_authority()
    acceptance = {
        "qcd_particle_authority_passes": bool(qcd["passed"]),
        "verified_physlib_sources_are_registered": len(qcd["formal_sources"]) == 5,
        "one_loop_running_is_executable": qcd["decision"]["one_loop_qcd_running_is_executable"],
        "complex_action_factorization_is_executable": qcd["decision"][
            "complex_action_qcd_factorization_is_executable"
        ],
        "strong_cp_structure_is_executable": qcd["decision"]["strong_cp_structure_is_executable"],
        "trace_anomaly_structure_is_executable": qcd["decision"][
            "trace_anomaly_origin_structure_is_executable"
        ],
        "numerical_spectrum_remains_open": not qcd["decision"]["numerical_hadron_spectrum_derived"],
        "mass_gap_remains_open": not qcd["decision"]["continuum_yang_mills_mass_gap_proved"],
        "confinement_derivation_remains_open": not qcd["decision"][
            "first_principles_confinement_proved"
        ],
        "no_physical_claim_is_promoted": qcd["decision"]["physical_claims_promoted"] == [],
    }
    payload = {
        "schema": "openwave.m9.m135-qcd-particle-authority.v1",
        "task": "M9.135",
        "component": qcd,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "previous_qcd_underassessment_corrected": True,
            "physlib_zil_particle_graph_is_authoritative": True,
            "openwave_qcd_executable_bridge_added": True,
            "empirical_qcd_validation_complete": False,
            "unique_cat_ept_qcd_prediction_established": False,
            "physical_claims_promoted": [],
        },
    }
    return {**payload, "fingerprint": fingerprint(payload)}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
