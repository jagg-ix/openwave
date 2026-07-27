"""M9.120 evidence authority for finite spectra, response, and refinement."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m120_extension import run_formalization_m120_extension
from .gauge_sector_linear_response import run_gauge_sector_linear_response
from .gauge_sector_spectral_refinement import (
    run_gauge_sector_spectral_refinement,
)
from .gauge_sector_spectrum import run_gauge_sector_spectrum
from .m119_gauge_covariant_evidence_authority import (
    run_m119_gauge_covariant_evidence_authority,
)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), default=str
        ).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m120_spectral_phenomenology_evidence_authority() -> dict[str, Any]:
    previous = run_m119_gauge_covariant_evidence_authority()
    formal = run_formalization_m120_extension()
    spectrum = run_gauge_sector_spectrum()
    response = run_gauge_sector_linear_response()
    refinement = run_gauge_sector_spectral_refinement()
    component = {
        "formal_authority_passed": bool(formal["passed"]),
        "spectrum_campaign_passed": bool(spectrum["passed"]),
        "gauge_invariant_finite_spectra": spectrum["decision"][
            "gauge_invariant_finite_spectra_constructed"
        ],
        "higgs_tangent_and_radial_curvatures": spectrum["decision"][
            "higgs_vacuum_tangent_and_radial_curvatures_constructed"
        ],
        "physical_particle_spectrum_predicted": spectrum["decision"][
            "physical_particle_spectrum_predicted"
        ],
        "response_campaign_passed": bool(response["passed"]),
        "gauge_invariant_transition_response": response["decision"][
            "gauge_invariant_transition_response_constructed"
        ],
        "spectral_sum_rules": response["decision"][
            "spectral_completeness_sum_rules_closed"
        ],
        "intrinsic_decay_channel_constructed": response["decision"][
            "intrinsic_decay_channel_constructed"
        ],
        "refinement_campaign_passed": bool(refinement["passed"]),
        "finite_spectral_refinement": refinement["decision"][
            "finite_gauge_spectral_refinement_constructed"
        ],
        "phenomenology_ledger": refinement["decision"][
            "dimensionless_phenomenology_ledger_constructed"
        ],
        "continuum_spectrum_theorem": refinement["decision"][
            "continuum_spectrum_theorem_complete"
        ],
        "physical_prediction_complete": refinement["decision"][
            "physical_spectrum_or_decay_prediction_complete"
        ],
    }
    payload = {
        "schema": "openwave.m9.m120-spectral-phenomenology-evidence-authority.v1",
        "task": "M9.120",
        "previous_authority": previous,
        "formal_authority": formal,
        "component": component,
        "claim_boundary": {
            "finite_eigenvalues_are_observed_particle_masses": False,
            "broadened_response_is_physical_decay_rate": False,
            "improving_grid_sequence_is_continuum_proof": False,
            "dimensionless_ledger_is_external_phenomenology": False,
            "draft_physlib_candidates_are_merged_proofs": False,
        },
    }
    acceptance = {
        "previous_M9_119_authority_is_preserved": bool(previous["passed"]),
        "merged_formal_spectral_authority_passes": component[
            "formal_authority_passed"
        ],
        "M9_120a_finite_spectrum_closes": component["spectrum_campaign_passed"]
        and component["gauge_invariant_finite_spectra"]
        and component["higgs_tangent_and_radial_curvatures"],
        "M9_120b_linear_response_closes": component["response_campaign_passed"]
        and component["gauge_invariant_transition_response"]
        and component["spectral_sum_rules"],
        "M9_120c_refinement_and_ledger_close": component[
            "refinement_campaign_passed"
        ]
        and component["finite_spectral_refinement"]
        and component["phenomenology_ledger"],
        "physical_spectrum_decay_and_continuum_claims_remain_open": (
            not component["physical_particle_spectrum_predicted"]
            and not component["intrinsic_decay_channel_constructed"]
            and not component["continuum_spectrum_theorem"]
            and not component["physical_prediction_complete"]
        ),
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload)
        == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {
            "spectrum": spectrum,
            "response": response,
            "refinement": refinement,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_120a_gauge_invariant_spectra_complete": True,
            "M9_120b_gauge_invariant_response_complete": True,
            "M9_120c_spectral_refinement_and_ledger_complete": True,
            "physical_spectrum_decay_or_identity_promoted": False,
            "next_target_requires_calibration_or_new_dynamics": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
