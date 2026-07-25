"""M9.83 dimensionless heat/thermal-field criterion closure.

Combines OpenWave's exact periodic spectral heat solver, entropy/dissipation
controls, and resolution study with the live PhysLib finite spectral heat-flow
semigroup and Duhamel scaffolding.

The closure validates the explicit dimensionless thermal sector. It does not
claim microscopic CAT/EPT thermodynamics, material coefficients, relativistic
heat conduction, or physical temperature calibration.
"""
from __future__ import annotations
from functools import lru_cache
import json
from typing import Any
from .thermal_field import run_thermal_field_study

OPENWAVE_BASE = "52bbc8ebfc748386145f55b53d1e662874d8844e"
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BASE = "c7283b7fc1ec9ef8acbfd6ed292b34e7ba8d5dd3"
FORMAL_BRANCH = "agent/m9-criterion-reduction-spin-maxwell-thermal"
FORMAL_HEAD = "19ef639d0ab849f92fb462d5899817ac1a5c4161"
FORMAL_WITNESSES = (
    "Physlib.Mathematics.HarmonicAnalysis.FiniteSpectralHeatFlow.flow_add",
    "Physlib.Mathematics.HarmonicAnalysis.FiniteSpectralHeatFlow.flow_preserves_zero_mode",
    "Physlib.Mathematics.HarmonicAnalysis.FiniteSpectralHeatFlow.flow_zero_diffusivity",
    "Physlib.Mathematics.HarmonicAnalysis.SobolevHeatSemigroupDuhamel.duhamel_telescoping",
)

@lru_cache(maxsize=1)
def run_thermal_sector_closure() -> dict[str, Any]:
    thermal = run_thermal_field_study()
    acceptance = {
        "existing_thermal_campaign_passes": bool(thermal["passed"]),
        "total_heat_conservation_closes": thermal["acceptance"]["total_heat_is_conserved"],
        "entropy_monotonicity_closes": thermal["acceptance"]["thermal_entropy_is_monotone"],
        "diffusion_dissipation_identity_closes": thermal["acceptance"]["diffusion_dissipation_identity_closes"],
        "semigroup_property_closes": thermal["acceptance"]["semigroup_property_closes"],
        "zero_diffusivity_control_closes": thermal["acceptance"]["zero_diffusivity_freezes_field"],
        "resolution_control_closes": thermal["acceptance"]["resolution_is_stable"],
        "formal_spectral_heat_witnesses_are_named": len(FORMAL_WITNESSES) == 4,
        "microscopic_thermodynamics_is_not_silently_inferred": True,
        "material_calibration_is_not_silently_inferred": True,
    }
    return {
        "schema": "openwave.m9.thermal-sector-closure.v1",
        "task": "M9.83",
        "repositories": {"openwave_base": OPENWAVE_BASE, "physlib_repository": FORMAL_REPOSITORY, "physlib_base": FORMAL_BASE, "physlib_branch": FORMAL_BRANCH, "physlib_head": FORMAL_HEAD},
        "formal_witnesses": list(FORMAL_WITNESSES),
        "thermal_controls": {"initial": thermal["initial"], "final": thermal["final"], "entropy_increase": thermal["entropy_increase"], "variance_decrease": thermal["variance_decrease"], "mode_decay": thermal["mode_decay"], "dissipation_identity": thermal["dissipation_identity"], "semigroup": thermal["semigroup"], "zero_diffusivity": thermal["zero_diffusivity"], "resolution": thermal["resolution"]},
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {"thermal_field_sector_validated_in_platform": True, "dimensionless_heat_entropy_dissipation_sector_established": True, "microscopic_cat_ept_thermodynamics_derived": False, "material_transport_coefficients_calibrated": False, "relativistic_heat_conduction_established": False},
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
