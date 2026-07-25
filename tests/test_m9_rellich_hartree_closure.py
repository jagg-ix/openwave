import numpy as np

from openwave.xperiments.m9_cat_ept.rellich_hartree_closure import (
    periodic_hartree_energy,
    spectral_resample_state,
    strictly_decreasing,
)


def test_strictly_decreasing_helper():
    assert strictly_decreasing([3.0, 2.0, 1.0])
    assert not strictly_decreasing([3.0, 3.0, 1.0])


def test_spectral_resample_preserves_normalization():
    state = np.ones((8, 8, 8), dtype=np.complex128)
    state /= np.sqrt(np.sum(np.abs(state) ** 2))
    result = spectral_resample_state(state, 12, 1.0)
    assert result.shape == (12, 12, 12)
    assert abs(float(np.sum(np.abs(result) ** 2)) - 1.0) < 1e-12


def test_periodic_hartree_energy_is_finite():
    density = np.zeros((8, 8, 8))
    density[4, 4, 4] = 1.0
    wave = 2.0 * np.pi * np.fft.fftfreq(8)
    kx, ky, kz = np.meshgrid(wave, wave, wave, indexing="ij")
    value = periodic_hartree_energy(density, kx * kx + ky * ky + kz * kz, 1.0)
    assert np.isfinite(value) and value >= 0.0
