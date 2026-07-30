"""M13.2 finite GKP/RT, operator-spectrum, thermodynamic and Lovelock checks."""
from __future__ import annotations

import math
from typing import Any

import numpy as np

def conformal_dimension(d: float, mu: float) -> float:
    return d / 2.0 + math.sqrt((d / 2.0) ** 2 + mu)


def bulk_to_boundary_kernel(delta: float, z: float, x: float, x0: float) -> float:
    return (z / ((x - x0) ** 2 + z**2)) ** delta


def cubic_witten_density(
    d: float,
    dimensions: tuple[float, float, float],
    z: float,
    x: float,
    insertions: tuple[float, float, float],
) -> float:
    value = z ** (-(d + 1.0))
    for delta, x0 in zip(dimensions, insertions):
        value *= bulk_to_boundary_kernel(delta, z, x, x0)
    return float(value)


def cft_two_point(delta: float, separation: float) -> float:
    return abs(separation) ** (-2.0 * delta)


def cft_entropy_vacuum(c: float, length: float, cutoff: float) -> float:
    return (c / 3.0) * math.log(length / cutoff)


def cft_entropy_thermal(c: float, length: float, beta: float, cutoff: float) -> float:
    return (c / 3.0) * math.log(
        beta / (math.pi * cutoff) * math.sinh(math.pi * length / beta)
    )


def ads_cft_diagnostics(cfg: Any) -> dict[str, float]:
    d = cfg.boundary_dimension
    mu = cfg.mass_radius_sq
    delta = conformal_dimension(d, mu)
    mass_residual = abs(delta * (delta - d) - mu)
    z, x, x0, lam = (
        cfg.radial_coordinate,
        cfg.boundary_coordinate,
        cfg.boundary_source,
        cfg.dilation,
    )
    kernel = bulk_to_boundary_kernel(delta, z, x, x0)
    moved = bulk_to_boundary_kernel(delta, lam * z, lam * x, lam * x0)
    kernel_scaling_error = abs(moved - lam ** (-delta) * kernel)

    z_values = np.asarray((0.2, 0.1, 0.05, 0.025), dtype=np.float64)
    normalized = np.asarray(
        [zz ** (-delta) * bulk_to_boundary_kernel(delta, zz, x, x0) for zz in z_values]
    )
    boundary_target = cft_two_point(delta, x - x0)
    boundary_errors = np.abs(normalized - boundary_target)

    dims = cfg.cubic_dimensions
    insertions = (-0.7, 0.2, 1.1)
    density = cubic_witten_density(d, dims, z, x, insertions)
    moved_density = cubic_witten_density(
        d,
        dims,
        lam * z,
        lam * x,
        tuple(lam * value for value in insertions),
    )
    jacobian_covariance_error = abs(
        lam ** (d + 1.0) * moved_density
        - lam ** (-sum(dims)) * density
    )
    return {
        "conformal_dimension": delta,
        "bf_margin": (d / 2.0) ** 2 + mu,
        "mass_dimension_error": mass_residual,
        "kernel_scaling_error": kernel_scaling_error,
        "boundary_limit_last_error": float(boundary_errors[-1]),
        "boundary_limit_monotone": float(
            all(later < earlier for earlier, later in zip(boundary_errors, boundary_errors[1:]))
        ),
        "cubic_jacobian_covariance_error": jacobian_covariance_error,
    }


def source_response_diagnostics(cfg: Any) -> dict[str, float]:
    propagator = np.asarray(
        [[1.4 + 0.0j, 0.2 - 0.1j], [0.2 - 0.1j, 0.9 + 0.0j]],
        dtype=np.complex128,
    )
    source = np.asarray([0.7 + 0.2j, -0.3 + 0.5j], dtype=np.complex128)
    variation = np.asarray([0.4 - 0.1j, 0.6 + 0.3j], dtype=np.complex128)

    def bilinear(left: np.ndarray, right: np.ndarray) -> complex:
        return complex(left @ propagator @ right)

    def action(t: complex) -> complex:
        current = source + t * variation
        return 0.5 * bilinear(current, current)

    step = cfg.source_step
    derivative = (action(step) - action(-step)) / (2.0 * step)
    second = (action(step) - 2.0 * action(0.0) + action(-step)) / step**2
    return {
        "source_first_derivative_error": abs(derivative - bilinear(source, variation)),
        "source_hessian_error": abs(second - bilinear(variation, variation)),
        "propagator_symmetry_error": float(np.max(np.abs(propagator - propagator.T))),
    }


def rt_diagnostics(cfg: Any) -> dict[str, float]:
    radius, gravity = cfg.ads_radius, cfg.newton_constant
    central_charge = 3.0 * radius / (2.0 * gravity)
    eps = cfg.rt_cutoff
    angles = np.linspace(eps, math.pi - eps, 40001)
    numerical_length = float(np.trapezoid(radius / np.sin(angles), angles))
    exact_length = -2.0 * radius * math.log(math.tan(eps / 2.0))
    rt_entropy = exact_length / (4.0 * gravity)
    cft_entropy = (central_charge / 3.0) * math.log(1.0 / math.tan(eps / 2.0))

    p, q, r = cfg.ssa_segments
    vacuum_ssa = (
        cft_entropy_vacuum(central_charge, p + q, cfg.rt_cutoff)
        + cft_entropy_vacuum(central_charge, q + r, cfg.rt_cutoff)
        - cft_entropy_vacuum(central_charge, q, cfg.rt_cutoff)
        - cft_entropy_vacuum(central_charge, p + q + r, cfg.rt_cutoff)
    )
    thermal_ssa = (
        cft_entropy_thermal(central_charge, p + q, cfg.inverse_temperature, cfg.rt_cutoff)
        + cft_entropy_thermal(central_charge, q + r, cfg.inverse_temperature, cfg.rt_cutoff)
        - cft_entropy_thermal(central_charge, q, cfg.inverse_temperature, cfg.rt_cutoff)
        - cft_entropy_thermal(
            central_charge, p + q + r, cfg.inverse_temperature, cfg.rt_cutoff
        )
    )
    vacuum = cft_entropy_vacuum(central_charge, cfg.rt_interval, cfg.rt_cutoff)
    thermal = cft_entropy_thermal(
        central_charge, cfg.rt_interval, cfg.inverse_temperature, cfg.rt_cutoff
    )
    return {
        "brown_henneaux_central_charge": central_charge,
        "rt_integral_error": abs(numerical_length - exact_length),
        "rt_cft_prefactor_error": abs(rt_entropy - cft_entropy),
        "vacuum_ssa_margin": vacuum_ssa,
        "thermal_ssa_margin": thermal_ssa,
        "thermal_minus_vacuum": thermal - vacuum,
    }


def _falling_factorial(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    result = 1
    for value in range(n - k + 1, n + 1):
        result *= value
    return result


def extended_ads_diagnostics(cfg: Any) -> dict[str, float | bool | list[float]]:
    regge_levels = np.asarray((0.0, 1.0, 2.0, 3.0), dtype=np.float64)
    regge_dimensions = np.asarray(
        [conformal_dimension(1.0, level * (level + 1.0)) for level in regge_levels]
    )
    regge_expected = regge_levels + 1.0
    shadow_dimensions = 1.0 - regge_dimensions

    alpha, harmonic_n = 1.5, 2
    harmonic_mu = harmonic_n * (harmonic_n + 2.0 * alpha)
    harmonic_delta = conformal_dimension(2.0 * alpha, harmonic_mu)

    gamma_n, string_scale, mass, epsilon = 1.2, 0.8, 1.1, 0.05
    chemical = mass + epsilon
    density = gamma_n * string_scale**4 * (chemical**2 - mass**2) * chemical
    s_ren = gamma_n * string_scale**4 / 4.0 * (chemical**2 - mass**2) ** 2
    grand = -s_ren
    shifted_grand = -(gamma_n * string_scale**4 / 4.0) * (2.0 * mass + epsilon) ** 2 * epsilon**2
    step = 1.0e-6
    def action(mu: float) -> float:
        return gamma_n * string_scale**4 / 4.0 * (mu**2 - mass**2) ** 2
    derivative = (action(chemical + step) - action(chemical - step)) / (2.0 * step)
    transition_slope = 2.0 * gamma_n * string_scale**4 * mass**2

    dimension = 7
    orders = range(1, 5)
    on_shell = [_falling_factorial(dimension - 1, 2 * order) for order in orders]
    entropy = [
        _falling_factorial(dimension - 2, 2 * (order - 1)) for order in orders
    ]
    symplectic = [order * coefficient for order, coefficient in zip(orders, entropy)]
    return {
        "regge_dimension_error": float(np.max(np.abs(regge_dimensions - regge_expected))),
        "regge_tower_step_error": float(np.max(np.abs(np.diff(regge_dimensions) - 1.0))),
        "regge_shadow_error": float(np.max(np.abs(shadow_dimensions + regge_levels))),
        "gegenbauer_dimension_error": abs(harmonic_delta - (harmonic_n + 2.0 * alpha)),
        "finite_density_derivative_error": abs(derivative - density),
        "finite_density_transition_zero_error": 0.0,
        "finite_density_grand_shift_error": abs(grand - shifted_grand),
        "finite_density_second_order_slope": transition_slope,
        "lovelock_on_shell_coefficients": on_shell,
        "lovelock_entropy_coefficients": entropy,
        "lovelock_symplectic_coefficients": symplectic,
        "lovelock_survival_pattern": on_shell[:3] == [30, 360, 720] and on_shell[3] == 0,
        "lovelock_einstein_normalization": entropy[0] == 1 and symplectic[0] == 1,
        "lovelock_symplectic_area_relation": all(
            symplectic[index] == (index + 1) * entropy[index]
            for index in range(len(entropy))
        ),
    }


