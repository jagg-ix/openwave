from openwave.xperiments.m9_cat_ept.holographic_gravity_coupling import (
    ScreenDensityAnchor,
    build_gravity_configs,
    coupling_contract,
    run_holographic_gravity_coupling,
)
from openwave.xperiments.m9_cat_ept.screen_coupled_nonlinear_gravity import (
    ScreenCoupledNonlinearMetricConfig,
)


def test_screen_coupled_nonlinear_config_reconstructs_anchor_G():
    cfg = ScreenCoupledNonlinearMetricConfig(screen_newton_coupling=0.25)
    contract = cfg.coupling_contract()
    assert contract["screen_coupling_is_injected"]
    assert abs(contract["matter_newton_coupling"] - 0.25) <= 5.0e-15


def test_one_screen_anchor_reaches_both_gravity_carriers():
    anchor = ScreenDensityAnchor(
        area=2.0,
        bits=8.0,
        evidence_class="external",
        source="synthetic test fixture",
    )
    contract = coupling_contract(build_gravity_configs(anchor))
    assert contract["weak_uses_screen_coupling"]
    assert contract["nonlinear_uses_screen_coupling"]
    assert contract["weak_and_nonlinear_share_one_G"]


def test_current_coupling_authority_closes_implementation_not_calibration():
    result = run_holographic_gravity_coupling()
    assert result["passed"]
    assert result["decision"]["weak_and_nonlinear_share_one_screen_G"]
    assert result["decision"]["nonlinear_config_has_explicit_screen_coupling"]
    assert not result["decision"]["current_default_is_physically_calibrated"]
