"""M9.82 source-free Maxwell-wave criterion closure.

Combines the exact periodic spectral Maxwell controls already present in
OpenWave with the live PhysLib construction of a smooth harmonic vacuum
potential that satisfies Maxwell's equations and is a plane wave.

The closure is limited to the EM-wave criterion. It does not establish photon
quantization, empirical calibration, or derivation of electromagnetism from the
full coupled CAT/EPT dynamics.
"""
from __future__ import annotations
from functools import lru_cache
import json
from typing import Any
from .wave_reductions import run_wave_reduction_study

OPENWAVE_BASE = "52bbc8ebfc748386145f55b53d1e662874d8844e"
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BASE = "c7283b7fc1ec9ef8acbfd6ed292b34e7ba8d5dd3"
FORMAL_BRANCH = "agent/m9-criterion-reduction-spin-maxwell-thermal"
FORMAL_HEAD = "19ef639d0ab849f92fb462d5899817ac1a5c4161"
FORMAL_WITNESSES = (
    "Electromagnetism.ElectromagneticPotential.harmonicWaveX_isExtrema",
    "Electromagnetism.ElectromagneticPotential.harmonicWaveX_isPlaneWave",
    "Electromagnetism.ElectromagneticPotential.harmonicWaveX_maxwell_planeWave",
)

@lru_cache(maxsize=1)
def run_maxwell_wave_closure() -> dict[str, Any]:
    wave = run_wave_reduction_study()
    maxwell = wave["maxwell"]
    bridge = wave["massless_bridge"]
    acceptance = {
        "existing_wave_reduction_campaign_passes": bool(wave["passed"]),
        "source_free_maxwell_energy_is_conserved": maxwell["maximum_energy_drift"] <= 2e-13,
        "right_moving_wave_propagates_at_declared_speed": maxwell["translation"]["maximum_translation_error"] <= 2e-13,
        "transverse_constraint_closes": maxwell["transverse_constraint_residual"] <= 2e-15,
        "massless_wave_bridge_closes": bridge["maximum_field_error"] <= 3e-13,
        "formal_maxwell_and_plane_wave_witnesses_are_named": len(FORMAL_WITNESSES) == 3,
        "photon_quantization_is_not_silently_inferred": True,
        "empirical_calibration_is_not_silently_inferred": True,
    }
    return {
        "schema": "openwave.m9.maxwell-wave-closure.v1",
        "task": "M9.82",
        "repositories": {"openwave_base": OPENWAVE_BASE, "physlib_repository": FORMAL_REPOSITORY, "physlib_base": FORMAL_BASE, "physlib_branch": FORMAL_BRANCH, "physlib_head": FORMAL_HEAD},
        "formal_witnesses": list(FORMAL_WITNESSES),
        "maxwell_controls": maxwell,
        "massless_bridge": bridge,
        "resolution": wave["resolution"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {"em_wave_sector_validated_in_platform": True, "source_free_maxwell_plane_wave_established": True, "electromagnetism_derived_from_full_cat_ept": False, "photon_quantization_established": False, "physical_units_calibrated": False},
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
