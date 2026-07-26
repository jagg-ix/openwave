from openwave.xperiments.m9_cat_ept.reconciled_gauge_spinor_stationary_current import (
    ReconciledGaugeSpinorConfig,
)


def test_schrodinger_and_pauli_mass_maps_agree():
    cfg = ReconciledGaugeSpinorConfig()
    assert abs(2.0 * cfg.dispersion * cfg.effective_mass - 1.0) < 2e-15
    assert abs(
        cfg.convective_current_coefficient - 2.0 * cfg.dispersion * cfg.charge
    ) < 2e-15


def test_legacy_mass_mismatch_is_material():
    cfg = ReconciledGaugeSpinorConfig()
    relative = abs(1.0 - cfg.effective_mass) / cfg.effective_mass
    assert relative > 0.25


def test_historical_even_seed_is_separate_from_odd_operational_grid():
    cfg = ReconciledGaugeSpinorConfig()
    assert cfg.seed_points == 16
    assert cfg.points == 17
    assert cfg.seed_points % 2 == 0
    assert cfg.points % 2 == 1


def test_hartree_coupling_is_a_sweep_not_a_hidden_constant():
    cfg = ReconciledGaugeSpinorConfig()
    assert cfg.hartree_couplings[0] == 0.0
    assert len(cfg.hartree_couplings) >= 3
    assert len(set(cfg.hartree_couplings)) == len(cfg.hartree_couplings)
