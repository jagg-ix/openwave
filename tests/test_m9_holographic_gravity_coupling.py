from openwave.xperiments.m9_cat_ept.holographic_gravity_coupling import run_holographic_gravity_coupling
from openwave.xperiments.m9_cat_ept.model_registration_m110 import run_model_registration_study


def test_screen_density_is_primary_coupling():
    result = run_holographic_gravity_coupling()
    assert result["passed"]
    assert result["decision"]["screen_density_is_primary_G_source"]
    assert not result["decision"]["particle_mass_is_primary_G_source"]
    assert result["default_physical_injection_blocked"]


def test_nonlinear_injection_gap_is_not_hidden():
    result = run_holographic_gravity_coupling()
    assert result["synthetic_contract"]["weak_uses_screen_coupling"]
    assert result["synthetic_contract"]["nonlinear_requires_explicit_injection"]


def test_registration_preserves_boundaries():
    result = run_model_registration_study()
    assert result["passed"]
    current = result["m9_110"]
    assert current["universal_holographic_G_preserved"]
    assert not current["dynamical_renormalization_constructed"]
    assert not current["nonlinear_screen_G_injection"]
    assert current["physical_claims_promoted"] == []
