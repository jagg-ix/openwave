import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.quark_color_sector import (
    baryon_singlet, ckm_matrix, composite_charge, deterministic_su3,
    generator_diagnostics, meson_singlet, run_quark_color_study,
    su3_diagnostics, transform_baryon, transform_meson
)

def test_generator_algebra_closes():
    assert generator_diagnostics()["commutator_closure_error"] <= 3e-15

def test_su3_element_is_special_unitary():
    r = su3_diagnostics(deterministic_su3(7))
    assert r["unitarity_error"] <= 3e-15 and r["determinant_error"] <= 3e-15

def test_singlets_are_invariant():
    u = deterministic_su3(9)
    assert np.max(np.abs(transform_meson(meson_singlet(), u) - meson_singlet())) <= 3e-15
    assert np.max(np.abs(transform_baryon(baryon_singlet(), u) - baryon_singlet())) <= 4e-15

def test_fractional_charge_ledgers():
    assert abs(composite_charge(("u", "u", "d")) - 1) <= 1e-15
    assert abs(composite_charge(("u", "d", "d"))) <= 1e-15

def test_unknown_quark_rejected():
    with pytest.raises(ValueError):
        composite_charge(("strange",))

def test_ckm_is_unitary():
    v = ckm_matrix()
    assert np.max(np.abs(v.conj().T @ v - np.eye(3))) <= 3e-15

def test_invalid_coefficients_rejected():
    from openwave.xperiments.m9_cat_ept.quark_color_sector import su3_element
    with pytest.raises(ValueError):
        su3_element(np.zeros(7))

def test_full_study_passes():
    r = run_quark_color_study()
    assert r["passed"] and all(r["acceptance"].values())
