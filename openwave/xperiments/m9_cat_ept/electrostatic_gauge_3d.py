"""M9.7b1 three-dimensional electrostatic Maxwell qualification gate.

This module lifts M9's density interface to a regular spherical four-spinor test
ansatz and solves the self-consistent electrostatic Maxwell constraint in finite-
volume form. It qualifies charge sign, Gauss law, boundary flux, Coulomb field
energy, window/refinement behavior, and the radial entropic-clock interface.

It does not solve the coupled three-dimensional Dirac stationary equation or
Maxwell wave evolution. Those remain the M9.7b2 gate.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Sequence

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]


@dataclass(frozen=True)
class RadialSpinorParameters:
    """Regular spherical test-spinor and electrostatic units."""

    length_scale: float = 1.0
    lower_ratio: float = 0.5
    gauge_charge: float = 1.0
    epsilon0: float = 1.0

    def __post_init__(self) -> None:
        if self.length_scale <= 0.0:
            raise ValueError("length_scale must be positive")
        if self.lower_ratio < 0.0:
            raise ValueError("lower_ratio must be nonnegative")
        if self.gauge_charge == 0.0:
            raise ValueError("gauge_charge must be nonzero")
        if self.epsilon0 <= 0.0:
            raise ValueError("epsilon0 must be positive")

    @property
    def raw_norm(self) -> float:
        ratio_sq = self.lower_ratio**2
        return math.pi * self.length_scale**3 * (1.0 + 3.0 * ratio_sq)

    @property
    def exact_central_potential(self) -> float:
        ratio_sq = self.lower_ratio**2
        numerator = self.gauge_charge * (2.0 + 3.0 * ratio_sq)
        denominator = (
            8.0
            * math.pi
            * self.epsilon0
            * self.length_scale
            * (1.0 + 3.0 * ratio_sq)
        )
        return numerator / denominator

    @property
    def exact_field_energy(self) -> float:
        ratio_sq = self.lower_ratio**2
        factor = (
            837.0 * ratio_sq**2 + 672.0 * ratio_sq + 160.0
        ) / (256.0 * (1.0 + 3.0 * ratio_sq) ** 2)
        return (
            self.gauge_charge**2
            * factor
            / (8.0 * math.pi * self.epsilon0 * self.length_scale)
        )


@dataclass(frozen=True)
class RadialGrid:
    outer_radius: float = 16.0
    shells: int = 512

    def __post_init__(self) -> None:
        if self.outer_radius <= 0.0:
            raise ValueError("outer_radius must be positive")
        if self.shells < 64:
            raise ValueError("shells must be at least 64")


@dataclass(frozen=True)
class ReflectingCoarseGraining:
    steps: int = 64
    gamma: float = 1.0

    def __post_init__(self) -> None:
        if self.steps < 1:
            raise ValueError("steps must be positive")
        if self.gamma <= 0.0:
            raise ValueError("gamma must be positive")


@dataclass(frozen=True)
class ElectrostaticSolution:
    edges: RealArray
    centers: RealArray
    volumes: RealArray
    upper_component: RealArray
    lower_component: RealArray
    number_density: RealArray
    shell_charge: RealArray
    enclosed_charge_edges: RealArray
    electric_field_edges: RealArray
    potential_edges: RealArray
    potential_centers: RealArray
    dr: float
    parameters: RadialSpinorParameters
    grid: RadialGrid
    modulation: float


def radial_grid(grid: RadialGrid) -> tuple[RealArray, RealArray, RealArray, float]:
    edges = np.linspace(0.0, grid.outer_radius, grid.shells + 1, dtype=np.float64)
    dr = grid.outer_radius / grid.shells
    centers = 0.5 * (edges[:-1] + edges[1:])
    volumes = 4.0 * math.pi / 3.0 * (edges[1:] ** 3 - edges[:-1] ** 3)
    return edges, centers, volumes, dr


def regular_spinor_components(
    centers: RealArray,
    parameters: RadialSpinorParameters,
    outer_radius: float,
    modulation: float = 0.0,
) -> tuple[RealArray, RealArray]:
    """Return regular upper-s and lower-p radial amplitudes before normalization."""
    scale = parameters.length_scale
    envelope = np.exp(-centers / scale)
    upper = envelope.copy()
    lower = parameters.lower_ratio * centers / scale * envelope
    if modulation != 0.0:
        mode = np.cos(math.pi * centers / outer_radius)
        upper *= 1.0 + modulation * mode
        lower *= 1.0 - modulation * mode
    return np.asarray(upper), np.asarray(lower)


def solve_electrostatic_constraint(
    parameters: RadialSpinorParameters = RadialSpinorParameters(),
    grid: RadialGrid = RadialGrid(),
    *,
    modulation: float = 0.0,
) -> ElectrostaticSolution:
    """Solve spherical Gauss law from a normalized spinor number density."""
    edges, centers, volumes, dr = radial_grid(grid)
    upper, lower = regular_spinor_components(
        centers,
        parameters,
        grid.outer_radius,
        modulation,
    )
    raw_density = upper**2 + lower**2
    normalization = math.sqrt(float(np.sum(raw_density * volumes)))
    upper = upper / normalization
    lower = lower / normalization
    number_density = upper**2 + lower**2

    shell_charge = parameters.gauge_charge * number_density * volumes
    enclosed = np.concatenate(([0.0], np.cumsum(shell_charge)))

    electric = np.zeros_like(edges)
    electric[1:] = enclosed[1:] / (
        4.0 * math.pi * parameters.epsilon0 * edges[1:] ** 2
    )

    potential = np.empty_like(edges)
    potential[-1] = enclosed[-1] / (
        4.0 * math.pi * parameters.epsilon0 * grid.outer_radius
    )
    for index in range(grid.shells - 1, -1, -1):
        potential[index] = potential[index + 1] + 0.5 * (
            electric[index] + electric[index + 1]
        ) * dr
    potential_centers = 0.5 * (potential[:-1] + potential[1:])

    return ElectrostaticSolution(
        edges=edges,
        centers=centers,
        volumes=volumes,
        upper_component=np.asarray(upper, dtype=np.float64),
        lower_component=np.asarray(lower, dtype=np.float64),
        number_density=np.asarray(number_density, dtype=np.float64),
        shell_charge=np.asarray(shell_charge, dtype=np.float64),
        enclosed_charge_edges=np.asarray(enclosed, dtype=np.float64),
        electric_field_edges=np.asarray(electric, dtype=np.float64),
        potential_edges=np.asarray(potential, dtype=np.float64),
        potential_centers=np.asarray(potential_centers, dtype=np.float64),
        dr=dr,
        parameters=parameters,
        grid=grid,
        modulation=modulation,
    )


def number_norm(solution: ElectrostaticSolution) -> float:
    return float(np.sum(solution.number_density * solution.volumes))


def total_charge(solution: ElectrostaticSolution) -> float:
    return float(solution.enclosed_charge_edges[-1])


def gauss_shell_residuals(solution: ElectrostaticSolution) -> RealArray:
    edges = solution.edges
    electric = solution.electric_field_edges
    flux_difference = (
        solution.parameters.epsilon0
        * 4.0
        * math.pi
        * (edges[1:] ** 2 * electric[1:] - edges[:-1] ** 2 * electric[:-1])
    )
    return np.asarray(flux_difference - solution.shell_charge, dtype=np.float64)


def boundary_flux(solution: ElectrostaticSolution) -> float:
    radius = solution.grid.outer_radius
    return float(
        solution.parameters.epsilon0
        * 4.0
        * math.pi
        * radius**2
        * solution.electric_field_edges[-1]
    )


def field_energy(solution: ElectrostaticSolution) -> float:
    """Return interior electric energy plus the analytic exterior Coulomb tail."""
    edges = solution.edges
    electric = solution.electric_field_edges
    integrand = (
        0.5
        * solution.parameters.epsilon0
        * 4.0
        * math.pi
        * edges**2
        * electric**2
    )
    interior = float(np.trapezoid(integrand, edges))
    charge = total_charge(solution)
    tail = charge**2 / (
        8.0
        * math.pi
        * solution.parameters.epsilon0
        * solution.grid.outer_radius
    )
    return interior + tail


def source_potential_energy(solution: ElectrostaticSolution) -> float:
    charge_density = solution.parameters.gauge_charge * solution.number_density
    return 0.5 * float(
        np.sum(charge_density * solution.potential_centers * solution.volumes)
    )


def core_fraction(solution: ElectrostaticSolution, radius: float = 8.0) -> float:
    mask = solution.centers <= radius * solution.parameters.length_scale
    return float(np.sum(solution.number_density[mask] * solution.volumes[mask]))


def edge_fraction(solution: ElectrostaticSolution, fraction: float = 0.20) -> float:
    threshold = fraction * solution.grid.outer_radius
    mask = solution.centers >= solution.grid.outer_radius - threshold
    return float(np.sum(solution.number_density[mask] * solution.volumes[mask]))


def shell_probability(solution: ElectrostaticSolution) -> RealArray:
    probability = solution.number_density * solution.volumes
    probability = probability / float(np.sum(probability))
    return np.asarray(probability, dtype=np.float64)


def apply_reflecting_channel(probability: RealArray) -> RealArray:
    p = np.asarray(probability, dtype=np.float64)
    if p.ndim != 1 or p.size < 2:
        raise ValueError("probability must be a one-dimensional vector")
    if np.any(p < 0.0):
        raise ValueError("probability must be nonnegative")
    if not math.isclose(float(np.sum(p)), 1.0, rel_tol=0.0, abs_tol=1.0e-12):
        raise ValueError("probability must sum to 1")
    q = np.empty_like(p)
    q[0] = 0.75 * p[0] + 0.25 * p[1]
    q[-1] = 0.25 * p[-2] + 0.75 * p[-1]
    q[1:-1] = 0.25 * p[:-2] + 0.50 * p[1:-1] + 0.25 * p[2:]
    q /= float(np.sum(q))
    return q


def kl_divergence(probability: RealArray, reference: RealArray) -> float:
    p = np.asarray(probability, dtype=np.float64)
    q = np.asarray(reference, dtype=np.float64)
    if p.shape != q.shape:
        raise ValueError("probability and reference must have the same shape")
    if np.any(p < 0.0) or np.any(q <= 0.0):
        raise ValueError("invalid KL inputs")
    mask = p > 0.0
    return float(np.sum(p[mask] * np.log(p[mask] / q[mask])))


def reflecting_total_correlation(probability: RealArray) -> float:
    p = np.asarray(probability, dtype=np.float64)
    q = apply_reflecting_channel(p)
    total = 0.0
    last = p.size - 1
    for source, source_probability in enumerate(p):
        if source_probability == 0.0:
            continue
        if source == 0:
            transitions = ((0, 0.75), (1, 0.25))
        elif source == last:
            transitions = ((last - 1, 0.25), (last, 0.75))
        else:
            transitions = (
                (source - 1, 0.25),
                (source, 0.50),
                (source + 1, 0.25),
            )
        for destination, weight in transitions:
            total += source_probability * weight * math.log(weight / q[destination])
    return 0.0 if abs(total) < 1.0e-14 else total


def radial_clock_trajectory(
    probability: RealArray,
    channel: ReflectingCoarseGraining = ReflectingCoarseGraining(),
) -> dict[str, Any]:
    uniform = np.full(probability.size, 1.0 / probability.size, dtype=np.float64)
    initial_remaining = kl_divergence(probability, uniform)
    current = np.asarray(probability, dtype=np.float64).copy()
    remaining: list[float] = []
    gain: list[float] = []
    correlation: list[float] = []
    for _ in range(channel.steps + 1):
        value = kl_divergence(current, uniform)
        remaining.append(value)
        gain.append(initial_remaining - value)
        correlation.append(reflecting_total_correlation(current))
        if len(remaining) <= channel.steps:
            current = apply_reflecting_channel(current)
    closure = max(
        abs(initial_remaining - (value + gained))
        for value, gained in zip(remaining, gain, strict=True)
    )
    return {
        "initial_remaining_disequilibrium": initial_remaining,
        "terminal_remaining_disequilibrium": remaining[-1],
        "terminal_accumulated_gain": gain[-1],
        "terminal_total_correlation": correlation[-1],
        "max_ledger_closure_error": closure,
        "remaining_nonincreasing": all(
            later <= earlier + 1.0e-13
            for earlier, later in zip(remaining[:-1], remaining[1:], strict=True)
        ),
        "gain_nondecreasing": all(
            later + 1.0e-13 >= earlier
            for earlier, later in zip(gain[:-1], gain[1:], strict=True)
        ),
        "correlation_nonnegative": bool(min(correlation) >= -1.0e-12),
    }


def solution_metrics(solution: ElectrostaticSolution) -> dict[str, Any]:
    parameters = solution.parameters
    numerical_field_energy = field_energy(solution)
    numerical_source_energy = source_potential_energy(solution)
    exact_energy = parameters.exact_field_energy
    exact_phi0 = parameters.exact_central_potential
    residual = gauss_shell_residuals(solution)
    charge = total_charge(solution)
    return {
        "shells": solution.grid.shells,
        "outer_radius": solution.grid.outer_radius,
        "dr": solution.dr,
        "modulation": solution.modulation,
        "number_norm": number_norm(solution),
        "total_charge": charge,
        "boundary_flux": boundary_flux(solution),
        "boundary_flux_error": abs(boundary_flux(solution) - charge),
        "max_gauss_shell_residual": float(np.max(np.abs(residual))),
        "field_energy": numerical_field_energy,
        "source_potential_energy": numerical_source_energy,
        "exact_field_energy": exact_energy,
        "field_energy_relative_error": abs(numerical_field_energy - exact_energy)
        / exact_energy,
        "source_field_relative_difference": abs(
            numerical_source_energy - numerical_field_energy
        )
        / exact_energy,
        "central_potential": float(solution.potential_edges[0]),
        "exact_central_potential": exact_phi0,
        "central_potential_relative_error": abs(
            solution.potential_edges[0] - exact_phi0
        )
        / abs(exact_phi0),
        "core_fraction_r8": core_fraction(solution),
        "edge_fraction_outer_20pct": edge_fraction(solution),
    }


def _observed_orders(levels: Sequence[dict[str, Any]], field: str) -> list[float]:
    return [
        math.log(float(coarse[field]) / float(fine[field]), 2.0)
        for coarse, fine in zip(levels[:-1], levels[1:], strict=True)
    ]


def run_electrostatic_gauge_study() -> dict[str, Any]:
    """Run the frozen M9.7b1 electrostatic gauge qualification study."""
    parameters = RadialSpinorParameters()
    levels = [
        solution_metrics(
            solve_electrostatic_constraint(
                parameters,
                RadialGrid(outer_radius=16.0, shells=shells),
            )
        )
        for shells in (256, 512, 1024)
    ]
    energy_orders = _observed_orders(levels, "field_energy_relative_error")
    potential_orders = _observed_orders(
        levels,
        "central_potential_relative_error",
    )

    windows = [
        solution_metrics(
            solve_electrostatic_constraint(
                parameters,
                RadialGrid(
                    outer_radius=outer_radius,
                    shells=round(outer_radius / 0.03125),
                ),
            )
        )
        for outer_radius in (12.0, 16.0, 20.0)
    ]
    energy_values = [float(item["field_energy"]) for item in windows]
    potential_values = [float(item["central_potential"]) for item in windows]
    energy_window_spread = (max(energy_values) - min(energy_values)) / float(
        np.mean(energy_values)
    )
    potential_window_spread = (
        max(potential_values) - min(potential_values)
    ) / float(np.mean(np.abs(potential_values)))

    positive = solve_electrostatic_constraint(parameters, RadialGrid())
    negative_parameters = RadialSpinorParameters(gauge_charge=-1.0)
    negative = solve_electrostatic_constraint(negative_parameters, RadialGrid())
    signed_sector = {
        "electric_sign_reversal_error": float(
            np.max(
                np.abs(
                    positive.electric_field_edges + negative.electric_field_edges
                )
            )
        ),
        "potential_sign_reversal_error": float(
            np.max(np.abs(positive.potential_edges + negative.potential_edges))
        ),
        "field_energy_relative_difference": abs(
            field_energy(positive) - field_energy(negative)
        )
        / field_energy(positive),
        "density_max_difference": float(
            np.max(np.abs(positive.number_density - negative.number_density))
        ),
    }

    perturbed = solve_electrostatic_constraint(
        parameters,
        RadialGrid(),
        modulation=0.02,
    )
    base_metrics = solution_metrics(positive)
    perturbation_metrics = solution_metrics(perturbed)
    perturbation = {
        **perturbation_metrics,
        "field_energy_ratio": perturbation_metrics["field_energy"]
        / base_metrics["field_energy"],
        "central_potential_ratio": perturbation_metrics["central_potential"]
        / base_metrics["central_potential"],
    }

    base_clock = radial_clock_trajectory(shell_probability(positive))
    perturbed_clock = radial_clock_trajectory(shell_probability(perturbed))
    clock = {
        "channel": asdict(ReflectingCoarseGraining()),
        "base": base_clock,
        "perturbed": perturbed_clock,
    }

    finest = levels[-1]
    acceptance = {
        "gauss_law_closes": max(
            float(item["max_gauss_shell_residual"]) for item in levels
        )
        <= 1.0e-13,
        "boundary_flux_closes": max(
            float(item["boundary_flux_error"]) for item in levels
        )
        <= 1.0e-13,
        "number_norm_closes": max(
            abs(float(item["number_norm"]) - 1.0) for item in levels
        )
        <= 1.0e-13,
        "energy_converges_second_order": min(energy_orders) >= 1.8,
        "potential_converges_second_order": min(potential_orders) >= 1.8,
        "finest_field_energy_accurate": (
            float(finest["field_energy_relative_error"]) <= 3.0e-5
        ),
        "finest_central_potential_accurate": (
            float(finest["central_potential_relative_error"]) <= 5.0e-5
        ),
        "source_and_field_energy_agree": (
            float(finest["source_field_relative_difference"]) <= 5.0e-6
        ),
        "localized_density": (
            float(finest["core_fraction_r8"]) >= 0.999
            and float(finest["edge_fraction_outer_20pct"]) <= 1.0e-6
        ),
        "window_independent": (
            energy_window_spread <= 1.0e-5
            and potential_window_spread <= 1.0e-5
        ),
        "signed_charge_sector": (
            signed_sector["electric_sign_reversal_error"] <= 1.0e-14
            and signed_sector["potential_sign_reversal_error"] <= 1.0e-14
            and signed_sector["field_energy_relative_difference"] <= 1.0e-14
            and signed_sector["density_max_difference"] <= 1.0e-14
        ),
        "perturbed_source_remains_well_resolved": (
            0.9 <= perturbation["field_energy_ratio"] <= 1.1
            and 0.9 <= perturbation["central_potential_ratio"] <= 1.1
            and float(perturbation["core_fraction_r8"]) >= 0.999
            and float(perturbation["edge_fraction_outer_20pct"]) <= 1.0e-6
            and float(perturbation["max_gauss_shell_residual"]) <= 1.0e-13
            and float(perturbation["boundary_flux_error"]) <= 1.0e-13
        ),
        "radial_clock_interface_closes": all(
            trajectory["remaining_nonincreasing"]
            and trajectory["gain_nondecreasing"]
            and trajectory["correlation_nonnegative"]
            and trajectory["max_ledger_closure_error"] <= 1.0e-12
            for trajectory in (base_clock, perturbed_clock)
        ),
    }

    return {
        "schema": "openwave.m9.electrostatic-gauge-3d-result.v1",
        "model": "M9-CAT-EPT",
        "target": "M9.7b1",
        "carrier": (
            "regular spherical four-spinor density ansatz: upper s-wave plus "
            "lower p-wave radial amplitude"
        ),
        "maxwell_sector": (
            "self-consistent static electrostatic field from spherical Gauss law"
        ),
        "parameters": asdict(parameters),
        "exact_references": {
            "raw_norm": parameters.raw_norm,
            "central_potential": parameters.exact_central_potential,
            "field_energy": parameters.exact_field_energy,
        },
        "levels": levels,
        "observed_orders": {
            "field_energy": energy_orders,
            "central_potential": potential_orders,
        },
        "windows": windows,
        "window_spreads": {
            "field_energy": energy_window_spread,
            "central_potential": potential_window_spread,
        },
        "signed_sector": signed_sector,
        "perturbation": perturbation,
        "clock": clock,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "a normalized 3D spherical spinor-density interface",
                "a self-consistent electrostatic Maxwell constraint",
                "signed dimensionless source sectors with opposite flux",
                "Gauss-law, boundary-flux, field-energy, and radial-clock ledgers",
            ],
            "does_not_establish": [
                "a coupled 3D Dirac stationary solution",
                "Maxwell wave evolution or magnetic fields",
                "dynamical localization or perturbation stability of a 3D spinor",
                "a calibrated electric charge or electron identity",
                "unique CAT/EPT selection of the radial ansatz",
            ],
        },
    }
