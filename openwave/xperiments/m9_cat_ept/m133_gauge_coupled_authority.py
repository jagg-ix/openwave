"""M9.133 authority for gauge-coupled CAT/EPT evolution."""
from __future__ import annotations

from .gauge_coupled_cat_ept_m133 import run_gauge_coupled_cat_ept
from .gauge_exchange_refinement_m133 import run_gauge_exchange_refinement


def run_m133_gauge_coupled_authority() -> dict:
    model = run_gauge_coupled_cat_ept()
    campaign = run_gauge_exchange_refinement()
    acceptance = {
        "gauge_coupled_model_passes": model["passed"],
        "exchange_and_refinement_pass": campaign["passed"],
        "charged_matter_field_geometry_entropy_are_jointly_evolved": model["decision"]["charged_matter_gauge_geometry_entropy_evolved_together"],
        "full_relativistic_claim_remains_open": not model["decision"]["full_relativistic_gauge_gravity_constructed"],
        "physical_calibration_remains_open": not model["decision"]["physical_calibration_complete"],
    }
    return {
        "schema": "openwave.m9.m133-gauge-coupled-authority.v1",
        "task": "M9.133",
        "model": model,
        "campaign": campaign,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "dynamical_U1_sector_added": True,
            "local_exchange_accounting_added": True,
            "three_grid_stability_campaign_added": True,
            "complete_Maxwell_Einstein_CAT_EPT": False,
            "external_validation_complete": False,
        },
    }
