"""Lepton-family hierarchy and parameter-selection audit.

The benchmark uses the charged-lepton mass ratios normalized to the lightest
member. It evaluates whether simple generation laws are predictive:

- a two-parameter geometric hierarchy;
- a three-parameter log-quadratic interpolant;
- one independent effective scale parameter per generation.

The audit distinguishes interpolation from prediction. It does not fit or
promote a physical CAT/EPT lepton model.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

RealArray = NDArray[np.float64]


@dataclass(frozen=True)
class SpectrumBenchmark:
    labels: tuple[str, ...] = ("e", "mu", "tau")
    masses_mev: tuple[float, ...] = (0.51099895069, 105.6583755, 1776.86)

    def __post_init__(self) -> None:
        if len(self.labels) != len(self.masses_mev) or len(self.labels) < 3:
            raise ValueError("matched spectrum with at least three members required")
        if any(value <= 0.0 for value in self.masses_mev):
            raise ValueError("positive masses required")

    def normalized(self) -> RealArray:
        values = np.asarray(self.masses_mev, dtype=np.float64)
        return values / values[0]

    def generation(self) -> RealArray:
        return np.arange(len(self.labels), dtype=np.float64)


def fit_log_geometric(benchmark: SpectrumBenchmark) -> dict[str, Any]:
    n = benchmark.generation()
    log_mass = np.log(benchmark.normalized())
    design = np.column_stack((np.ones_like(n), n))
    parameters, *_ = np.linalg.lstsq(design, log_mass, rcond=None)
    prediction = np.exp(design @ parameters)
    ratios = prediction / benchmark.normalized()
    multiplicative_errors = np.maximum(ratios, 1.0 / ratios)
    return {
        "log_scale": float(parameters[0]),
        "log_ratio": float(parameters[1]),
        "ratio": float(math.exp(parameters[1])),
        "prediction": prediction,
        "multiplicative_errors": multiplicative_errors,
        "maximum_multiplicative_error": float(np.max(multiplicative_errors)),
        "log_rms_error": float(
            math.sqrt(np.mean((np.log(prediction) - log_mass) ** 2))
        ),
        "parameter_count": 2,
        "residual_dof": len(n) - 2,
    }


def leave_one_out_geometric(benchmark: SpectrumBenchmark) -> dict[str, Any]:
    n = benchmark.generation()
    masses = benchmark.normalized()
    predictions = []
    factors = []
    for held_out in range(len(n)):
        mask = np.arange(len(n)) != held_out
        design = np.column_stack((np.ones(np.count_nonzero(mask)), n[mask]))
        parameters = np.linalg.solve(design, np.log(masses[mask]))
        predicted = float(math.exp(parameters[0] + parameters[1] * n[held_out]))
        factor = max(predicted / masses[held_out], masses[held_out] / predicted)
        predictions.append(predicted)
        factors.append(factor)
    return {
        "predictions": predictions,
        "multiplicative_error_factors": factors,
        "maximum_factor": max(factors),
        "median_factor": float(np.median(factors)),
    }


def fit_log_quadratic(benchmark: SpectrumBenchmark) -> dict[str, Any]:
    n = benchmark.generation()
    log_mass = np.log(benchmark.normalized())
    design = np.column_stack((np.ones_like(n), n, n * n))
    parameters = np.linalg.solve(design, log_mass)
    prediction = np.exp(design @ parameters)
    turnover = (
        math.inf
        if abs(parameters[2]) <= 1e-15
        else float(-parameters[1] / (2.0 * parameters[2]))
    )
    extrapolation_n = np.arange(3, 7, dtype=np.float64)
    extrapolation_design = np.column_stack(
        (
            np.ones_like(extrapolation_n),
            extrapolation_n,
            extrapolation_n * extrapolation_n,
        )
    )
    extrapolation = np.exp(extrapolation_design @ parameters)
    return {
        "parameters": parameters,
        "prediction": prediction,
        "maximum_relative_error": float(
            np.max(np.abs(prediction / benchmark.normalized() - 1.0))
        ),
        "parameter_count": 3,
        "residual_dof": len(n) - 3,
        "design_condition_number": float(np.linalg.cond(design)),
        "turnover_generation": turnover,
        "extrapolation_generation": extrapolation_n,
        "extrapolation": extrapolation,
        "monotone_beyond_observed": bool(np.all(np.diff(extrapolation) > 0.0)),
    }


def m927_effective_parameters(
    benchmark: SpectrumBenchmark,
    *,
    electron_reference_energy: float = 22.61946710584651,
) -> dict[str, Any]:
    """Map each target mass to the M9.27 selected-energy effective knob.

    M9.27 used E* = 4π + 8π q sqrt(2/3), where q=mu*sqrt(kappa).
    A single global calibration fixes the electron reference energy. Each
    remaining generation then requires its own q unless an additional law is
    supplied.
    """
    normalized = benchmark.normalized()
    target_energies = electron_reference_energy * normalized
    offset = 4.0 * math.pi
    coefficient = 8.0 * math.pi * math.sqrt(2.0 / 3.0)
    q = (target_energies - offset) / coefficient
    if np.any(q <= 0.0):
        raise ValueError("benchmark incompatible with positive effective scale")
    log_q = np.log(q)
    n = benchmark.generation()
    design = np.column_stack((np.ones_like(n), n))
    parameters, *_ = np.linalg.lstsq(design, log_q, rcond=None)
    predicted_q = np.exp(design @ parameters)
    predicted_energy = offset + coefficient * predicted_q
    predicted_mass = predicted_energy / electron_reference_energy
    factors = np.maximum(
        predicted_mass / normalized,
        normalized / predicted_mass,
    )
    return {
        "electron_reference_energy": electron_reference_energy,
        "target_dimensionless_energies": target_energies,
        "effective_q_per_generation": q,
        "independent_parameter_count": len(q),
        "shared_geometric_q": {
            "q0": float(math.exp(parameters[0])),
            "ratio": float(math.exp(parameters[1])),
            "predicted_normalized_masses": predicted_mass,
            "maximum_multiplicative_error": float(np.max(factors)),
        },
    }


def perturbation_audit(
    benchmark: SpectrumBenchmark,
    relative_perturbation: float = 1e-3,
) -> dict[str, Any]:
    if relative_perturbation <= 0.0:
        raise ValueError("positive perturbation required")
    base = np.asarray(benchmark.masses_mev, dtype=np.float64)
    predictions = []
    for index in range(len(base)):
        for sign in (-1.0, 1.0):
            modified = base.copy()
            modified[index] *= 1.0 + sign * relative_perturbation
            fit = fit_log_quadratic(
                SpectrumBenchmark(benchmark.labels, tuple(modified.tolist()))
            )
            predictions.append(float(fit["extrapolation"][0]))
    predictions_array = np.asarray(predictions)
    return {
        "relative_input_perturbation": relative_perturbation,
        "next_generation_predictions": predictions,
        "minimum_prediction": float(np.min(predictions_array)),
        "maximum_prediction": float(np.max(predictions_array)),
        "relative_prediction_span": float(
            (np.max(predictions_array) - np.min(predictions_array))
            / np.mean(predictions_array)
        ),
    }


@lru_cache(maxsize=1)
def run_lepton_hierarchy_audit() -> dict[str, Any]:
    benchmark = SpectrumBenchmark()
    geometric = fit_log_geometric(benchmark)
    loo = leave_one_out_geometric(benchmark)
    quadratic = fit_log_quadratic(benchmark)
    effective = m927_effective_parameters(benchmark)
    perturbation = perturbation_audit(benchmark)

    acceptance = {
        "benchmark_is_normalized": bool(abs(benchmark.normalized()[0] - 1.0) <= 1e-15),
        "geometric_law_fails_predictive_gate": bool(
            geometric["maximum_multiplicative_error"] >= 2.0
            and loo["maximum_factor"] >= 10.0
        ),
        "quadratic_interpolates_exactly": quadratic["maximum_relative_error"] <= 2e-14,
        "quadratic_has_zero_residual_dof": quadratic["residual_dof"] == 0,
        "quadratic_extrapolation_turns_over": (
            quadratic["turnover_generation"] < 3.0
            and not quadratic["monotone_beyond_observed"]
        ),
        "m927_requires_generation_specific_knobs": (
            effective["independent_parameter_count"] == 3
            and effective["shared_geometric_q"]["maximum_multiplicative_error"] >= 1.5
        ),
        "exact_fit_is_perturbation_sensitive": (
            perturbation["relative_prediction_span"]
            >= 5.0 * perturbation["relative_input_perturbation"]
        ),
        "predictive_hierarchy_not_selected": True,
    }
    return {
        "schema": "openwave.m9.lepton-hierarchy-audit.v1",
        "task": "M9.39",
        "benchmark": {
            "labels": benchmark.labels,
            "masses_mev": benchmark.masses_mev,
            "normalized": benchmark.normalized().tolist(),
        },
        "geometric_fit": {
            **{
                key: value
                for key, value in geometric.items()
                if key not in {"prediction", "multiplicative_errors"}
            },
            "prediction": geometric["prediction"].tolist(),
            "multiplicative_errors": geometric["multiplicative_errors"].tolist(),
        },
        "leave_one_out": loo,
        "log_quadratic_fit": {
            **{
                key: value
                for key, value in quadratic.items()
                if key not in {"parameters", "prediction", "extrapolation_generation", "extrapolation"}
            },
            "parameters": quadratic["parameters"].tolist(),
            "prediction": quadratic["prediction"].tolist(),
            "extrapolation_generation": quadratic["extrapolation_generation"].tolist(),
            "extrapolation": quadratic["extrapolation"].tolist(),
        },
        "m9_27_effective_parameter_audit": {
            **{
                key: value
                for key, value in effective.items()
                if key not in {"target_dimensionless_energies", "effective_q_per_generation", "shared_geometric_q"}
            },
            "target_dimensionless_energies": effective["target_dimensionless_energies"].tolist(),
            "effective_q_per_generation": effective["effective_q_per_generation"].tolist(),
            "shared_geometric_q": {
                **{
                    key: value
                    for key, value in effective["shared_geometric_q"].items()
                    if key != "predicted_normalized_masses"
                },
                "predicted_normalized_masses": effective["shared_geometric_q"]["predicted_normalized_masses"].tolist(),
            },
        },
        "perturbation_audit": perturbation,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "predictive_lepton_hierarchy_selected": False,
            "exact_interpolation_is_prediction": False,
            "physical_mass_spectrum_established": False,
            "classification": "honest negative for current candidate laws",
        },
        "classification": {
            "establishes": [
                "deterministic hierarchy model-comparison audit",
                "leave-one-out rejection of a geometric generation law",
                "zero-degree-of-freedom diagnosis for exact quadratic interpolation",
                "generation-specific knob audit for the M9.27 scale law",
            ],
            "does_not_establish": [
                "a CAT/EPT lepton spectrum",
                "a new charged lepton",
                "physical mass prediction",
                "that no possible CAT/EPT hierarchy law can succeed",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
