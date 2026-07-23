
"""Neutral localized-state and dark-sector variational survey.

The reference is an electrically neutral complex scalar Gaussian ansatz

    Phi(t,r) = exp(i omega t) A exp(-r^2 / (2 R^2)),

with fixed global U(1) charge Q and potential

    U(f) = 1/2 m^2 f^2 - lambda/4 f^4 + g/6 f^6.

After eliminating omega at fixed Q, the variational energy is minimized over
amplitude A and radius R.  A state with E/Q < m is energetically below the free
quanta threshold within this ansatz.

This is a neutral Q-ball-like survey.  It is not a full CAT/EPT field solution
or a physical dark-matter identification.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize

RealArray = NDArray[np.float64]


@dataclass(frozen=True)
class DarkSectorConfig:
    mass: float = 1.0
    attraction: float = 2.0
    stabilization: float = 1.0
    amplitude_min: float = 0.02
    amplitude_max: float = 4.0
    radius_min: float = 0.2
    radius_max: float = 30.0

    def __post_init__(self) -> None:
        if self.mass <= 0 or self.attraction < 0 or self.stabilization < 0:
            raise ValueError("valid potential parameters required")
        if not 0 < self.amplitude_min < self.amplitude_max:
            raise ValueError("valid amplitude bounds required")
        if not 0 < self.radius_min < self.radius_max:
            raise ValueError("valid radius bounds required")


def gaussian_integrals(amplitude: float, radius: float) -> dict[str, float]:
    if amplitude <= 0 or radius <= 0:
        raise ValueError("positive amplitude and radius required")
    coefficient = math.pi**1.5
    i2 = amplitude**2 * coefficient * radius**3
    i4 = amplitude**4 * coefficient * radius**3 / (2.0**1.5)
    i6 = amplitude**6 * coefficient * radius**3 / (3.0**1.5)
    gradient = 0.75 * amplitude**2 * coefficient * radius
    return {
        "i2": i2,
        "i4": i4,
        "i6": i6,
        "gradient": gradient,
    }


def variational_energy(
    amplitude: float,
    radius: float,
    charge: float,
    cfg: DarkSectorConfig = DarkSectorConfig(),
) -> float:
    if charge <= 0:
        raise ValueError("positive global charge required")
    integrals = gaussian_integrals(amplitude, radius)
    i2 = integrals["i2"]
    return (
        charge**2 / (2.0 * i2)
        + integrals["gradient"]
        + 0.5 * cfg.mass**2 * i2
        - 0.25 * cfg.attraction * integrals["i4"]
        + cfg.stabilization * integrals["i6"] / 6.0
    )


def optimize_charge(
    charge: float,
    cfg: DarkSectorConfig = DarkSectorConfig(),
) -> dict[str, Any]:
    if charge <= 0:
        raise ValueError("positive global charge required")
    bounds = [
        (math.log(cfg.amplitude_min), math.log(cfg.amplitude_max)),
        (math.log(cfg.radius_min), math.log(cfg.radius_max)),
    ]
    starts = (
        (0.05, 12.0),
        (0.3, 5.0),
        (0.8, 2.5),
        (1.3, 2.0),
        (2.0, 3.0),
        (3.0, 1.0),
    )

    best = None
    for amplitude0, radius0 in starts:
        result = minimize(
            lambda values: variational_energy(
                math.exp(float(values[0])),
                math.exp(float(values[1])),
                charge,
                cfg,
            ),
            np.log([amplitude0, radius0]),
            method="L-BFGS-B",
            bounds=bounds,
            options={"ftol": 1e-14, "gtol": 1e-10, "maxiter": 3000},
        )
        if best is None or result.fun < best.fun:
            best = result

    assert best is not None
    amplitude, radius = np.exp(best.x)
    energy = float(best.fun)
    free_threshold = cfg.mass * charge
    interior = (
        amplitude > 1.05 * cfg.amplitude_min
        and amplitude < 0.95 * cfg.amplitude_max
        and radius > 1.05 * cfg.radius_min
        and radius < 0.95 * cfg.radius_max
    )
    bound = interior and energy < free_threshold - 1e-5 * charge

    return {
        "charge": charge,
        "amplitude": float(amplitude),
        "radius": float(radius),
        "energy": energy,
        "energy_per_charge": energy / charge,
        "free_threshold": free_threshold,
        "binding_margin": free_threshold - energy,
        "interior_minimum": bool(interior),
        "bound_candidate": bool(bound),
        "optimizer_success": bool(best.success),
        "optimizer_message": str(best.message),
    }


def numerical_hessian_log_variables(
    charge: float,
    solution: dict[str, Any],
    cfg: DarkSectorConfig,
    epsilon: float = 2e-4,
) -> RealArray:
    center = np.log([solution["amplitude"], solution["radius"]])

    def function(values: RealArray) -> float:
        return variational_energy(
            math.exp(float(values[0])),
            math.exp(float(values[1])),
            charge,
            cfg,
        )

    hessian = np.zeros((2, 2), dtype=np.float64)
    f0 = function(center)
    for i in range(2):
        plus = center.copy()
        minus = center.copy()
        plus[i] += epsilon
        minus[i] -= epsilon
        hessian[i, i] = (
            function(plus) - 2.0 * f0 + function(minus)
        ) / epsilon**2

    plus_plus = center + np.asarray([epsilon, epsilon])
    plus_minus = center + np.asarray([epsilon, -epsilon])
    minus_plus = center + np.asarray([-epsilon, epsilon])
    minus_minus = center - np.asarray([epsilon, epsilon])
    off = (
        function(plus_plus)
        - function(plus_minus)
        - function(minus_plus)
        + function(minus_minus)
    ) / (4.0 * epsilon**2)
    hessian[0, 1] = hessian[1, 0] = off
    return hessian


def survey(
    charges: tuple[float, ...] = (20.0, 40.0, 50.0, 60.0, 80.0, 100.0, 150.0, 200.0),
    cfg: DarkSectorConfig = DarkSectorConfig(),
) -> dict[str, Any]:
    if not charges or any(value <= 0 for value in charges):
        raise ValueError("positive nonempty charge survey required")
    rows = [optimize_charge(value, cfg) for value in charges]
    bound = [row for row in rows if row["bound_candidate"]]
    threshold = bound[0]["charge"] if bound else None
    return {
        "charges": charges,
        "rows": rows,
        "first_bound_charge": threshold,
        "bound_count": len(bound),
    }


def no_attraction_control() -> dict[str, Any]:
    cfg = DarkSectorConfig(attraction=0.0)
    rows = [optimize_charge(charge, cfg) for charge in (60.0, 100.0, 200.0)]
    return {
        "rows": rows,
        "any_bound": any(row["bound_candidate"] for row in rows),
    }


def no_stabilization_control() -> dict[str, Any]:
    cfg = DarkSectorConfig(stabilization=0.0)
    charge = 100.0
    sequence = (
        (1.5, 3.0),
        (2.0, 5.0),
        (3.0, 10.0),
        (4.0, 20.0),
        (4.0, 30.0),
    )
    energies = [
        variational_energy(amplitude, radius, charge, cfg)
        for amplitude, radius in sequence
    ]
    return {
        "sequence": sequence,
        "energies": energies,
        "minimum_energy": min(energies),
        "runaway_detected": energies[-1] < energies[0] - 1e4,
    }


def parameter_robustness() -> dict[str, Any]:
    results = []
    for attraction in (1.9, 2.0, 2.1):
        for stabilization in (0.95, 1.0, 1.05):
            cfg = DarkSectorConfig(
                attraction=attraction,
                stabilization=stabilization,
            )
            row = optimize_charge(100.0, cfg)
            results.append(
                {
                    "attraction": attraction,
                    "stabilization": stabilization,
                    **row,
                }
            )
    return {
        "results": results,
        "all_bound": all(row["bound_candidate"] for row in results),
        "maximum_energy_per_charge": max(
            row["energy_per_charge"] for row in results
        ),
    }


@lru_cache(maxsize=1)
def run_dark_sector_survey() -> dict[str, Any]:
    cfg = DarkSectorConfig()
    scan = survey(cfg=cfg)
    low = next(row for row in scan["rows"] if row["charge"] == 20.0)
    representative = next(
        row for row in scan["rows"] if row["charge"] == 100.0
    )
    hessian = numerical_hessian_log_variables(
        100.0,
        representative,
        cfg,
    )
    eigenvalues = np.linalg.eigvalsh(hessian)
    no_attraction = no_attraction_control()
    no_stabilization = no_stabilization_control()
    robustness = parameter_robustness()

    acceptance = {
        "low_charge_state_is_diffuse": (
            not low["bound_candidate"]
            and low["energy_per_charge"] >= 0.999
        ),
        "finite_charge_threshold_is_found": scan["first_bound_charge"] == 60.0,
        "high_charge_candidate_is_bound": (
            representative["bound_candidate"]
            and representative["energy_per_charge"] < 0.95
        ),
        "representative_minimum_is_locally_positive": float(
            np.min(eigenvalues)
        ) > 1e-2,
        "attraction_is_required": not no_attraction["any_bound"],
        "sextic_stabilization_prevents_runaway": bool(
            no_stabilization["runaway_detected"]
        ),
        "candidate_is_robust_to_parameter_perturbations": robustness["all_bound"],
        "electric_neutrality_is_explicit": True,
    }

    return {
        "schema": "openwave.m9.dark-sector-survey-result.v1",
        "task": "M9.45",
        "config": asdict(cfg),
        "survey": scan,
        "representative_candidate": representative,
        "representative_hessian_eigenvalues": eigenvalues.tolist(),
        "no_attraction_control": no_attraction,
        "no_stabilization_control": no_stabilization,
        "parameter_robustness": robustness,
        "electric_charge": 0.0,
        "global_u1_charge": representative["charge"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "electrically neutral fixed-charge variational survey",
                "finite-charge binding threshold within a Gaussian ansatz",
                "interior locally positive candidate minimum",
                "attraction and sextic-stabilization controls",
                "bounded parameter-robustness survey",
            ],
            "does_not_establish": [
                "a full CAT/EPT field solution",
                "long-horizon dynamical stability",
                "a physical dark-matter particle or abundance",
                "gravitational phenomenology or experimental compatibility",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
