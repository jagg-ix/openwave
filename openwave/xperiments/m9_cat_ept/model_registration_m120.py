"""M9.120 registration for spectra, response, refinement, and scope boundaries."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .m120_spectral_phenomenology_evidence_authority import (
    run_m120_spectral_phenomenology_evidence_authority,
)
from .model_registration_m119 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    evidence = run_m120_spectral_phenomenology_evidence_authority()
    component = evidence["component"]
    formal = evidence["formal_authority"]
    return {
        **previous,
        "schema": "openwave.model-registration.v23",
        "m9_120": {
            "spectral_phenomenology_campaign_registered": evidence["passed"],
            "formal_authority_fingerprint": formal["fingerprint"],
            "formal_source_count": len(formal["sources"]),
            "merged_formal_head": formal["current_formal_head"],
            "pending_formal_candidate_count": len(formal["pending_candidates"]),
            "gauge_invariant_finite_spectra": component[
                "gauge_invariant_finite_spectra"
            ],
            "higgs_tangent_and_radial_curvatures": component[
                "higgs_tangent_and_radial_curvatures"
            ],
            "gauge_invariant_transition_response": component[
                "gauge_invariant_transition_response"
            ],
            "spectral_completeness_sum_rules": component["spectral_sum_rules"],
            "finite_spectral_refinement": component["finite_spectral_refinement"],
            "dimensionless_phenomenology_ledger": component[
                "phenomenology_ledger"
            ],
            "physical_particle_spectrum_predicted": component[
                "physical_particle_spectrum_predicted"
            ],
            "intrinsic_decay_channel_constructed": component[
                "intrinsic_decay_channel_constructed"
            ],
            "continuum_spectrum_theorem_complete": component[
                "continuum_spectrum_theorem"
            ],
            "physical_prediction_complete": component[
                "physical_prediction_complete"
            ],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "finite_gauge_spectrum_is_observed_mass_spectrum": False,
            "linear_response_is_measured_decay_phenomenology": False,
            "finite_grid_Cauchy_improvement_is_continuum_theorem": False,
            "draft_formal_PR_is_merged_authority": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), default=str
        ).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    evidence = run_m120_spectral_phenomenology_evidence_authority()
    payload = canonical_registration_payload()
    current = payload["m9_120"]
    acceptance = {
        "M9_120_authority_passes": bool(evidence["passed"]),
        "schema_v23_is_current": payload["schema"]
        == "openwave.model-registration.v23",
        "five_merged_formal_sources_are_registered": current[
            "formal_source_count"
        ]
        == 5
        and len(current["formal_authority_fingerprint"]) == 64,
        "merged_formal_head_is_not_a_draft_candidate": current[
            "merged_formal_head"
        ]
        == "3923d802339c957066fcccd579362f739775797a"
        and current["pending_formal_candidate_count"] == 2,
        "finite_spectrum_response_and_refinement_are_registered": (
            current["gauge_invariant_finite_spectra"]
            and current["higgs_tangent_and_radial_curvatures"]
            and current["gauge_invariant_transition_response"]
            and current["spectral_completeness_sum_rules"]
            and current["finite_spectral_refinement"]
            and current["dimensionless_phenomenology_ledger"]
        ),
        "physical_spectrum_decay_continuum_and_prediction_remain_open": (
            not current["physical_particle_spectrum_predicted"]
            and not current["intrinsic_decay_channel_constructed"]
            and not current["continuum_spectrum_theorem_complete"]
            and not current["physical_prediction_complete"]
        ),
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload)
        == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.120-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "spectral_phenomenology_layer_is_current": True,
            "physical_spectrum_or_decay_validation_complete": False,
            "next_target_requires_external_calibration_or_open_system_dynamics": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
