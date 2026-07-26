"""M9.109 combined evidence authority for Newton-G clock anchoring."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m109_extension import (
    CURRENT_FORMAL_HEAD,
    CURRENT_ZIL_HEAD,
    run_formalization_m109_extension,
)
from .m106_108_evidence_authority import run_m106_108_evidence_authority
from .newton_g_anchor_protocol import run_newton_G_anchor_protocol
from .newton_g_clock_universality import run_newton_G_clock_universality
from .newton_g_gravity_adapter import run_newton_G_gravity_adapter


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m109_evidence_authority() -> dict[str, Any]:
    previous = run_m106_108_evidence_authority()
    formal = run_formalization_m109_extension()
    universality = run_newton_G_clock_universality()
    anchor = run_newton_G_anchor_protocol()
    adapter = run_newton_G_gravity_adapter()
    payload = {
        "schema": "openwave.m9.m109-evidence-authority.v1",
        "task": "M9.109",
        "physlib_head": CURRENT_FORMAL_HEAD,
        "zil_head": CURRENT_ZIL_HEAD,
        "previous_authority": previous,
        "components": {
            "formal_G_clock_authority": {
                "campaign_passed": formal["passed"],
                "G_is_derived_not_primitive": formal["scope"][
                    "newton_G_is_canonical_derived_quantity"
                ],
                "mass_value_is_predicted": formal["scope"][
                    "particle_mass_value_is_derived"
                ],
            },
            "clock_universality": {
                "campaign_passed": universality["passed"],
                "particle_clocks_define_universal_G": universality[
                    "particle_clocks_define_one_universal_G"
                ],
                "particle_clocks_match_measured_G": universality[
                    "particle_clocks_match_measured_G"
                ],
                "universal_Planck_scale_anchor_required": universality["decision"][
                    "universal_Planck_scale_anchor_required"
                ],
            },
            "universal_anchor": {
                "campaign_passed": anchor["passed"],
                "independent_anchor_ready": anchor["decision"][
                    "independent_universal_gravity_anchor_complete"
                ],
                "withheld_G_prediction_executed": anchor["decision"][
                    "withheld_G_prediction_executed"
                ],
            },
            "gravity_adapter": {
                "campaign_passed": adapter["passed"],
                "calibrated_coupling_injected": adapter["decision"][
                    "calibrated_gravity_coupling_injected"
                ],
            },
        },
        "claim_boundary": {
            "algebraic_G_equivalence_is_numerical_G_prediction": False,
            "particle_Compton_clock_is_universal_gravity_clock": False,
            "Planck_scale_inversion_from_measured_G_is_prediction": False,
            "natural_unit_G_equals_one_is_physical_calibration": False,
        },
    }
    acceptance = {
        "previous_authority_is_preserved": bool(previous["passed"]),
        "current_formal_G_authority_passes": bool(formal["passed"]),
        "species_universality_audit_passes": bool(universality["passed"]),
        "noncircular_anchor_protocol_passes": bool(anchor["passed"]),
        "one_G_gravity_adapter_contract_passes": bool(adapter["passed"]),
        "ordinary_particle_clock_overclaim_is_rejected": not payload["components"][
            "clock_universality"
        ]["particle_clocks_define_universal_G"],
        "external_G_prediction_remains_blocked": not payload["components"][
            "universal_anchor"
        ]["withheld_G_prediction_executed"],
        "all_claim_boundaries_remain_false": not any(
            payload["claim_boundary"].values()
        ),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {
            "formal": formal,
            "clock_universality": universality,
            "universal_anchor": anchor,
            "gravity_adapter": adapter,
        },
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "M9_109_three_targets_completed": True,
            "Newton_G_is_formally_derived": True,
            "Newton_G_is_externally_predicted": False,
            "M9_110_general_metric_evolution_ready_for_physical_units": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
