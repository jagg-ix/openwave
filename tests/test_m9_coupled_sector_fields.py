from openwave.xperiments.m9_cat_ept.coupled_sector_fields import (
    run_coupled_sector_field_campaigns,
)


def test_three_coupled_field_sectors_close_declared_default_gates():
    result = run_coupled_sector_field_campaigns()
    assert result["passed"]
    assert result["sector_gates"] == {
        "antimatter_annihilation": True,
        "strong_force": True,
        "weak_force": True,
    }
    assert result["antimatter"]["maximum_ledger_error"] <= 5.0e-2
    assert result["strong"]["records"][-1]["singlet_imbalance"] <= 5.0e-3
    assert result["weak"]["records"][-1]["right_norm"] >= 0.95


def test_coupled_sector_gates_do_not_claim_standard_model():
    result = run_coupled_sector_field_campaigns()
    assert not result["decision"]["qed_qcd_electroweak_theories_constructed"]
