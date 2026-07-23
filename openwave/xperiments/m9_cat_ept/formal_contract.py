"""Executable CAT/EPT-to-OpenWave formal conformance helpers.

This module translates a small, version-pinned set of algebraic identities from
``entropic-physlib`` into ordinary Python functions. Passing these checks means
that the Python transcription matches those identities at the tested points. It
does not prove that OpenWave contains a localized or stable particle solution.
"""

from __future__ import annotations

import cmath
import json
import math
from pathlib import Path
from typing import Any, Sequence

NumberGrid = Sequence[Sequence[float]]
DEFAULT_TOLERANCE = 1.0e-12


def _require_nonzero(value: float, name: str) -> None:
    if value == 0.0:
        raise ValueError(f"{name} must be nonzero")


def _require_finite(value: float, name: str) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def compton_frequency(mass: float, speed_of_light: float, hbar: float) -> float:
    """Return ``omega_C = m c^2 / hbar``."""
    _require_nonzero(hbar, "hbar")
    return mass * speed_of_light**2 / hbar


def zitterbewegung_frequency(
    momentum: float, mass: float, speed_of_light: float, hbar: float
) -> float:
    """Return ``omega_Z = 2 sqrt(p^2 c^2 + m^2 c^4) / hbar``."""
    _require_nonzero(hbar, "hbar")
    radicand = momentum**2 * speed_of_light**2 + mass**2 * speed_of_light**4
    if radicand < 0.0:
        raise ValueError("zitterbewegung radicand must be nonnegative")
    return 2.0 * math.sqrt(radicand) / hbar


def de_broglie_frequency(energy: float, hbar: float) -> float:
    """Return ``omega_dB = E / hbar``."""
    _require_nonzero(hbar, "hbar")
    return energy / hbar


def compton_wavelength(mass: float, speed_of_light: float, hbar: float) -> float:
    """Return the reduced Compton wavelength ``lambda_C = hbar / (m c)``."""
    _require_nonzero(mass, "mass")
    _require_nonzero(speed_of_light, "speed_of_light")
    return hbar / (mass * speed_of_light)


def quantum_coupling(hbar: float) -> float:
    """Return the Caticha quantum-potential coupling ``lambda = hbar^2 / 8``."""
    return hbar**2 / 8.0


def ed_wave_function(rho: float, phase: float) -> complex:
    """Return the Madelung/entropic-dynamics state ``sqrt(rho) exp(i phase)``."""
    if rho < 0.0:
        raise ValueError("rho must be nonnegative")
    return math.sqrt(rho) * cmath.exp(1j * phase)


def _normalized_joint(joint: NumberGrid, *, atol: float = DEFAULT_TOLERANCE) -> list[list[float]]:
    rows = [list(row) for row in joint]
    if not rows or not rows[0]:
        raise ValueError("joint distribution must be nonempty")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("joint distribution must be rectangular")

    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            _require_finite(value, f"joint[{i}][{j}]")
            if value < 0.0:
                raise ValueError("joint probabilities must be nonnegative")

    total = math.fsum(value for row in rows for value in row)
    if not math.isclose(total, 1.0, rel_tol=0.0, abs_tol=atol):
        raise ValueError(f"joint probabilities must sum to 1, got {total!r}")
    return rows


def total_correlation(joint: NumberGrid) -> float:
    """Compute ``D_KL(p_XY || p_X p_Y)`` using the ``0 log 0 = 0`` convention."""
    rows = _normalized_joint(joint)
    row_marginal = [math.fsum(row) for row in rows]
    col_marginal = [math.fsum(row[j] for row in rows) for j in range(len(rows[0]))]

    terms: list[float] = []
    for i, row in enumerate(rows):
        for j, probability in enumerate(row):
            if probability == 0.0:
                continue
            reference = row_marginal[i] * col_marginal[j]
            if reference <= 0.0:
                raise ValueError("positive joint mass requires a positive product marginal")
            terms.append(probability * math.log(probability / reference))
    value = math.fsum(terms)
    # Floating-point roundoff can produce a tiny negative number for a factorized state.
    return 0.0 if abs(value) <= DEFAULT_TOLERANCE else value


def entropic_clock(gamma: float, joint: NumberGrid) -> float:
    """Return ``tau_ent = gamma * total_correlation``."""
    return gamma * total_correlation(joint)


def imaginary_action(hbar: float, gamma: float, joint: NumberGrid) -> float:
    """Return ``S_I = hbar * tau_ent``."""
    return hbar * entropic_clock(gamma, joint)


def correlation_weight_norm(gamma: float, joint: NumberGrid) -> float:
    """Return the formal complex-action modulus ``exp(-tau_ent)``."""
    return math.exp(-entropic_clock(gamma, joint))


def _error(actual: float, expected: float) -> float:
    return abs(actual - expected)


def _check(name: str, actual: float, expected: float, tolerance: float) -> dict[str, Any]:
    error = _error(actual, expected)
    return {
        "name": name,
        "actual": actual,
        "expected": expected,
        "absolute_error": error,
        "tolerance": tolerance,
        "passed": error <= tolerance,
    }


def default_contract_path() -> Path:
    return Path(__file__).with_name("formal") / "entropic_spine_contract.json"


def load_contract(path: Path | None = None) -> dict[str, Any]:
    contract_path = path or default_contract_path()
    with contract_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_conformance_suite(path: Path | None = None) -> dict[str, Any]:
    """Run deterministic checks for every identity exercised by M9.1."""
    contract = load_contract(path)
    tolerance = float(contract["numerics"]["default_absolute_tolerance"])

    mass = 2.0
    speed_of_light = 3.0
    hbar = 5.0
    rho = 0.37
    phase = 1.2
    gamma = 1.7
    correlated = [[0.4, 0.1], [0.1, 0.4]]
    independent = [[0.12, 0.28], [0.18, 0.42]]

    omega_c = compton_frequency(mass, speed_of_light, hbar)
    omega_z_rest = zitterbewegung_frequency(0.0, mass, speed_of_light, hbar)
    lambda_c = compton_wavelength(mass, speed_of_light, hbar)
    psi = ed_wave_function(rho, phase)
    tau = entropic_clock(gamma, correlated)
    action_i = imaginary_action(hbar, gamma, correlated)
    correlation = total_correlation(correlated)
    independent_correlation = total_correlation(independent)

    checks = [
        _check("born_rule", abs(psi) ** 2, rho, tolerance),
        _check("zitterbewegung_rest_eq_two_compton", omega_z_rest, 2.0 * omega_c, tolerance),
        _check(
            "compton_wavelength_mul_frequency",
            lambda_c * omega_c,
            speed_of_light,
            tolerance,
        ),
        _check("quantum_coupling", quantum_coupling(hbar), hbar**2 / 8.0, tolerance),
        _check("entropic_clock_eq_imaginary_action_div", tau, action_i / hbar, tolerance),
        _check(
            "correlation_weight_norm",
            correlation_weight_norm(gamma, correlated),
            math.exp(-tau),
            tolerance,
        ),
        _check("independent_total_correlation", independent_correlation, 0.0, tolerance),
    ]

    properties = {
        "correlated_total_correlation_nonnegative": correlation >= -tolerance,
        "entropic_clock_nonnegative": tau >= -tolerance,
        "correlation_weight_contractive": (
            correlation_weight_norm(gamma, correlated) <= 1.0 + tolerance
        ),
    }
    passed = all(check["passed"] for check in checks) and all(properties.values())

    return {
        "schema": "openwave.m9.conformance-result.v1",
        "model": contract["model"],
        "formal_source": contract["formal_source"],
        "scope": contract["scope"],
        "checks": checks,
        "properties": properties,
        "passed": passed,
    }
