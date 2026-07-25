from fractions import Fraction

import pytest

from openwave.xperiments.m9_cat_ept.canonical_force_formal_bridge import (
    SharedInteractionLedger,
    charge_from_winding,
    declared_particle_state,
    formal_potential_audit,
    pair_force_audit,
    periodic_pair_separation,
    run_canonical_force_formal_bridge,
    yukawa_potential,
)


def test_third_charge_arithmetic_selects_opposite_integer_sectors():
    assert charge_from_winding(3) == Fraction(1, 1)
    assert charge_from_winding(-3) == Fraction(-1, 1)
    assert charge_from_winding(2) == Fraction(2, 3)


def test_periodic_pair_separation_uses_minimum_image():
    first_model, first = declared_particle_state(3, points=16, half_width=4.0)
    second_model, second = declared_particle_state(-3, points=16, half_width=4.0)
    first = first_model.translate_cells(first, (0, 0, 7))
    second = second_model.translate_cells(second, (0, 0, -7))
    distance, vector = periodic_pair_separation(first, second)
    assert distance == pytest.approx(1.0, abs=2e-15)
    assert abs(abs(vector[2]) - 1.0) < 2e-15


def test_yukawa_zero_mass_and_screening_bound_close():
    radius = 3.25
    assert yukawa_potential(0.0, radius) == pytest.approx(1.0 / radius, abs=2e-15)
    assert yukawa_potential(0.2, radius) <= 1.0 / radius
    assert yukawa_potential(0.7, radius) <= yukawa_potential(0.2, radius)
    audit = formal_potential_audit(radius)
    assert audit["zero_mass_yukawa"] == pytest.approx(audit["coulomb"], abs=2e-15)
    assert audit["maximum_screened_excess"] <= 2e-15
    assert bool(audit["screened_values_monotone"])


def test_canonical_pair_uses_one_ledger_and_closes_force_derivatives():
    pair = pair_force_audit(SharedInteractionLedger())
    assert pair["declared_charges"] == [1.0, -1.0]
    assert pair["electric_force"] == pytest.approx(pair["electric_numeric"], abs=2e-9)
    assert pair["magnetic_force"] == pytest.approx(pair["magnetic_numeric"], abs=2e-9)
    assert pair["action_reaction_error"] < 2e-14
    assert not pair["winding_embedded"]


def test_full_force_bridge_passes_without_charged_particle_overclaim():
    result = run_canonical_force_formal_bridge()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["decision"]["formal_electric_and_magnetic_surfaces_imported"]
    assert result["decision"]["canonical_particle_pair_bound_to_force_kernels"]
    assert result["decision"]["shared_dimensionless_ledger_closed"]
    assert not result["decision"]["charged_stationary_particle_pair_constructed"]
    assert not result["decision"]["physical_force_calibration_complete"]
