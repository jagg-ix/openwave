import numpy as np

from openwave.xperiments.m9_cat_ept.clock_action_rate_calibration import (
    ClockActionCalibrationConfig,
    compton_mass,
    entropy_rate_from_clock,
    isolated_yukawa,
    yukawa_mass,
)
from openwave.xperiments.m9_cat_ept.electrogravitic_weak_field_evolution import (
    ElectrograviticEvolutionConfig,
    electrogravitic_fields,
)
from openwave.xperiments.m9_cat_ept.reconciled_gauge_spinor_stationary import (
    normalize_spinor,
)


def test_clock_yukawa_and_entropy_rate_identities_close():
    cfg = ClockActionCalibrationConfig()
    omega = 1.37
    yukawa = isolated_yukawa(omega, cfg)
    assert abs(yukawa_mass(yukawa, cfg) - compton_mass(omega, cfg)) < 2e-15
    entropy_unit = 3.2
    expected = (
        np.sqrt(2.0)
        * cfg.entropy_reference_frequency
        / (2.0 * entropy_unit * cfg.higgs_scale)
        * compton_mass(omega, cfg)
    )
    assert abs(entropy_rate_from_clock(omega, entropy_unit, cfg) - expected) < 2e-15


def test_weak_einstein00_source_closes_on_synthetic_state():
    cfg = ElectrograviticEvolutionConfig(
        points=17,
        seed_points=16,
        neutral_iterations=100,
        steps=10,
    )
    axis = -cfg.half_width + cfg.spacing * np.arange(cfg.points, dtype=np.float64)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    envelope = np.exp(-(x * x + y * y + z * z) / 5.0)
    spinor = np.zeros((2, cfg.points, cfg.points, cfg.points), dtype=np.complex128)
    spinor[0] = envelope
    spinor = normalize_spinor(spinor, cfg.spacing)
    vector = tuple(np.zeros((cfg.points,) * 3, dtype=np.float64) for _ in range(3))
    fields = electrogravitic_fields(spinor, vector, cfg)
    assert fields["einstein00_relative_residual"] < 1e-11
    assert fields["gauss_relative_residual"] < 1e-11
    assert fields["ampere_relative_residual"] < 1e-11
    assert fields["magnetic_divergence_max"] < 1e-11
    assert float(np.min(fields["metric_g00"])) > 0.0
