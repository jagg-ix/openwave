"""Dimensionless radial standing-wave quantization control.

A finite-difference Sturm--Liouville solve is used to qualify discrete bound
modes of a Coulomb-like scalar wave operator. This is a standing-wave control,
not a derivation of atomic structure from the full CAT/EPT field equations.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import eigh_tridiagonal

RealArray = NDArray[np.float64]


@dataclass(frozen=True)
class OrbitalConfig:
    radius: float = 80.0
    points: int = 1600
    angular_momentum: int = 0
    states: int = 4

    def __post_init__(self) -> None:
        if self.radius <= 0.0:
            raise ValueError("positive radius required")
        if self.points < 200:
            raise ValueError("at least 200 radial points required")
        if self.angular_momentum < 0:
            raise ValueError("nonnegative angular momentum required")
        if self.states < 1 or self.states >= self.points:
            raise ValueError("invalid state count")


def radial_grid(cfg: OrbitalConfig) -> tuple[RealArray, float]:
    dr = cfg.radius / (cfg.points + 1)
    r = dr * np.arange(1, cfg.points + 1, dtype=np.float64)
    return r, dr


def operator_diagonals(cfg: OrbitalConfig) -> tuple[RealArray, RealArray]:
    r, dr = radial_grid(cfg)
    centrifugal = cfg.angular_momentum * (cfg.angular_momentum + 1.0) / (2.0 * r * r)
    diagonal = 1.0 / (dr * dr) + centrifugal - 1.0 / r
    off_diagonal = np.full(cfg.points - 1, -0.5 / (dr * dr), dtype=np.float64)
    return diagonal, off_diagonal


def solve_modes(cfg: OrbitalConfig = OrbitalConfig()) -> dict[str, Any]:
    r, dr = radial_grid(cfg)
    diagonal, off_diagonal = operator_diagonals(cfg)
    energies, modes = eigh_tridiagonal(
        diagonal, off_diagonal, select="i", select_range=(0, cfg.states - 1)
    )
    normalized = np.empty_like(modes)
    for index in range(cfg.states):
        vector = modes[:, index]
        norm = math.sqrt(float(np.sum(vector * vector) * dr))
        normalized[:, index] = vector / norm
    overlap = normalized.T @ normalized * dr
    return {"config": asdict(cfg), "r": r, "dr": dr, "energies": energies,
            "modes": normalized, "overlap": overlap}


def analytic_energy(principal_n: int) -> float:
    if principal_n < 1:
        raise ValueError("positive principal quantum number required")
    return -0.5 / (principal_n * principal_n)


def node_count(mode: RealArray, tolerance: float = 1e-10) -> int:
    values = np.asarray(mode)
    mask = np.abs(values) > tolerance * np.max(np.abs(values))
    signs = np.sign(values[mask])
    return int(np.count_nonzero(signs[1:] * signs[:-1] < 0.0))


def density_stationarity(mode: RealArray, energy: float) -> float:
    times = np.linspace(0.0, 11.0, 37)
    reference = np.abs(mode) ** 2
    return max(float(np.max(np.abs(np.abs(mode * np.exp(-1j * energy * time)) ** 2 - reference))) for time in times)


def resolution_study() -> dict[str, Any]:
    points = (600, 1200, 2400)
    ladders = [solve_modes(OrbitalConfig(points=count, radius=80.0, states=3))["energies"] for count in points]
    target = np.asarray([analytic_energy(index) for index in (1, 2, 3)])
    errors = [float(np.linalg.norm(values - target)) for values in ladders]
    orders = [math.log(errors[index] / errors[index + 1], 2.0) for index in range(len(errors) - 1)]
    return {"points": points, "energies": [values.tolist() for values in ladders],
            "errors": errors, "orders": orders}


def domain_study() -> dict[str, Any]:
    radii = (40.0, 60.0, 80.0)
    energies = [solve_modes(OrbitalConfig(radius=radius, points=int(radius / 0.05), states=3))["energies"] for radius in radii]
    spread = np.ptp(np.asarray(energies), axis=0)
    return {"radii": radii, "energies": [values.tolist() for values in energies],
            "maximum_spread": float(np.max(spread))}


@lru_cache(maxsize=1)
def run_orbital_quantization_study() -> dict[str, Any]:
    solution = solve_modes()
    energies = solution["energies"]
    target = np.asarray([analytic_energy(index) for index in range(1, 5)])
    relative_errors = np.abs((energies - target) / target)
    nodes = [node_count(solution["modes"][:, index]) for index in range(4)]
    stationarity = [density_stationarity(solution["modes"][:, index], float(energies[index])) for index in range(4)]
    refinement = resolution_study()
    domains = domain_study()
    acceptance = {
        "four_discrete_bound_modes": bool(np.all(energies < 0.0)),
        "hydrogenic_ladder_recovered": float(np.max(relative_errors[:3])) <= 5e-3,
        "node_ladder_is_integer": nodes == [0, 1, 2, 3],
        "modes_are_orthonormal": float(np.max(np.abs(solution["overlap"] - np.eye(4)))) <= 2e-12,
        "density_is_stationary": max(stationarity) <= 2e-15,
        "resolution_converges": min(refinement["orders"]) >= 1.7,
        "domain_is_stable": domains["maximum_spread"] <= 5e-5,
        "quantization_is_boundary_eigenmode_selection": True,
    }
    return {
        "schema": "openwave.m9.orbital-quantization-result.v1",
        "task": "M9.32",
        "energies": energies.tolist(),
        "analytic_energies": target.tolist(),
        "relative_errors": relative_errors.tolist(),
        "node_counts": nodes,
        "maximum_orthogonality_error": float(np.max(np.abs(solution["overlap"] - np.eye(4)))),
        "maximum_density_stationarity_error": max(stationarity),
        "resolution": refinement,
        "domain": domains,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "discrete normalizable radial standing-wave modes",
                "hydrogenic dimensionless energy ladder",
                "integer node ordering and orthogonality",
                "resolution and domain convergence",
            ],
            "does_not_establish": [
                "orbital quantization from the full CAT/EPT PDE",
                "an emergent electron or nucleus",
                "radiative transitions or selection rules",
                "physical atomic units",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
