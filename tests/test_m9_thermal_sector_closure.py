from openwave.xperiments.m9_cat_ept.thermal_sector_closure import (
    run_thermal_sector_closure,
)


def test_thermal_sector_closure_passes():
    result = run_thermal_sector_closure()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["decision"]["thermal_field_sector_validated_in_platform"]
    assert result["decision"][
        "dimensionless_heat_entropy_dissipation_sector_established"
    ]


def test_thermal_promotion_keeps_stronger_boundaries():
    decision = run_thermal_sector_closure()["decision"]
    assert not decision["microscopic_cat_ept_thermodynamics_derived"]
    assert not decision["material_transport_coefficients_calibrated"]
    assert not decision["relativistic_heat_conduction_established"]
