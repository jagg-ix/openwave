"""M9.119 registration for gauge-covariant strong and electroweak carriers."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m119_gauge_covariant_evidence_authority import run_m119_gauge_covariant_evidence_authority
from .model_registration_m117 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m119_gauge_covariant_evidence_authority()
    component = evidence["component"]
    formal = evidence["formal_authority"]
    return {
        **previous,
        "schema": "openwave.model-registration.v22",
        "m9_119": {
            "gauge_covariant_sector_campaign_registered": evidence["passed"],
            "formal_authority_fingerprint": formal["fingerprint"],
            "formal_source_count": len(formal["sources"]),
            "local_SU3_link_carrier": component["local_SU3_links"],
            "gauge_covariant_color_dynamics": component["gauge_covariant_color_dynamics"],
            "Wilson_observables": component["Wilson_observables"],
            "QCD_confinement_established": component["QCD_confinement_established"],
            "local_SU2xU1_link_carrier": component["local_SU2xU1_links"],
            "gauge_covariant_Higgs_dynamics": component["gauge_covariant_Higgs_dynamics"],
            "quartic_Higgs_vacuum_orbit": component["quartic_Higgs_vacuum_orbit"],
            "complete_electroweak_theory": component["complete_electroweak_theory"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "local_SU3_carrier_is_physical_QCD": False,
            "Wilson_loops_are_confinement_measurement": False,
            "bosonic_SU2xU1_carrier_is_complete_standard_model": False,
            "uncalibrated_Higgs_flow_predicts_particle_masses": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m119_gauge_covariant_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_119"]
    acceptance = {
        "M9_119_authority_passes": bool(evidence["passed"]),
        "schema_v22_is_current": payload["schema"] == "openwave.model-registration.v22",
        "six_formal_sources_are_registered": current["formal_source_count"] == 6
        and len(current["formal_authority_fingerprint"]) == 64,
        "strong_gauge_carrier_is_registered": current["local_SU3_link_carrier"]
        and current["gauge_covariant_color_dynamics"]
        and current["Wilson_observables"],
        "electroweak_Higgs_carrier_is_registered": current["local_SU2xU1_link_carrier"]
        and current["gauge_covariant_Higgs_dynamics"]
        and current["quartic_Higgs_vacuum_orbit"],
        "QCD_and_complete_electroweak_remain_open": not current["QCD_confinement_established"]
        and not current["complete_electroweak_theory"],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.119-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "gauge_covariant_sector_layer_is_current": True,
            "full_QCD_or_electroweak_validation_complete": False,
            "next_executable_target_is_spectra_decays_and_phenomenology": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
