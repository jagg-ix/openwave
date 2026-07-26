import numpy as np

from openwave.xperiments.m9_cat_ept.compatible_discrete_geometry import (
    PeriodicFourierGeometry,
    analytic_identity_diagnostics,
    spectral_resample,
)


def test_fourier_complex_has_only_global_zero_mode():
    result = analytic_identity_diagnostics(points=17, half_width=8.0)
    assert result["odd_operational_grid"] == 1
    assert result["fourier_null_mode_count"] == 1
    assert result["legacy_even_centered_null_mode_count"] == 8


def test_discrete_vector_calculus_identities_close():
    result = analytic_identity_diagnostics(points=17, half_width=8.0)
    assert result["curl_gradient_max"] < 1e-12
    assert result["divergence_curl_max"] < 1e-12
    assert result["laplacian_identity_relative_error"] < 1e-12


def test_static_maxwell_uses_same_operator_family():
    points = 17
    spacing = 16.0 / points
    geometry = PeriodicFourierGeometry(
        (points, points, points), (spacing, spacing, spacing)
    )
    axis = -8.0 + spacing * np.arange(points, dtype=np.float64)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    rho = np.exp(-(x * x + y * y + z * z) / 8.0)
    current = (
        -y * rho,
        x * rho,
        np.zeros_like(rho),
    )
    fields = geometry.static_maxwell_fields(rho, current)
    assert fields["gauss_relative_residual"] < 1e-11
    assert fields["ampere_relative_residual"] < 1e-11
    assert fields["magnetic_divergence_max"] < 1e-11


def test_even_real_grid_is_rejected_instead_of_silently_dropping_nyquist():
    geometry = PeriodicFourierGeometry((16, 16, 16), (1.0, 1.0, 1.0))
    values = np.ones((16, 16, 16), dtype=np.float64)
    try:
        geometry.derivative(values, 0)
    except ValueError as error:
        assert "Nyquist ambiguity" in str(error)
    else:
        raise AssertionError("even-grid real spectral derivative must fail closed")


def test_spectral_resampling_moves_even_seed_to_odd_grid():
    axis = np.arange(16, dtype=np.float64)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    field = np.exp(2j * np.pi * x / 16.0) * np.exp(2j * np.pi * y / 16.0)
    resampled = spectral_resample(field, (17, 17, 17))
    assert resampled.shape == (17, 17, 17)
    assert np.isfinite(np.linalg.norm(resampled))


def test_covariant_laplacian_reduces_to_laplacian_at_zero_charge():
    geometry = PeriodicFourierGeometry((9, 9, 9), (1.0, 1.0, 1.0))
    axis = np.arange(9, dtype=np.float64)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    scalar = np.exp(2j * np.pi * x / 9.0)
    spinor = np.stack((scalar, 0.5 * scalar), axis=0)
    zero = tuple(np.zeros((9, 9, 9), dtype=np.float64) for _ in range(3))
    covariant = geometry.covariant_laplacian(spinor, zero, 0.0)
    direct = geometry.laplacian(spinor)
    assert np.linalg.norm(covariant - direct) < 1e-11
