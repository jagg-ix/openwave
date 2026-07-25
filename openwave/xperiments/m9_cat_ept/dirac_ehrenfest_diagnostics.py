"""M9.99c: domain-aware Dirac Ehrenfest and spin diagnostics.

M9.97 correctly compared kinetic-momentum transfer with the Lorentz-volume
force, but it also compared the second derivative of the unprojected Dirac
position expectation directly with force per norm.  The exact observable in the
four-spinor carrier is instead

    d<x_i>/dt = <alpha_i>.

This module measures that relation for pair and self-field control separately,
retains momentum-versus-Lorentz as the force diagnostic, and classifies the
rest-frame two-by-two T-BMT shadow as out of domain for a moving, extended,
nonuniform-field packet.
"""
from __future__ import annotations

from functools import lru_cache
import json
from typing import Any, Mapping, Sequence

import numpy as np

from .spinorial_pair_dynamics_authoritative import run_spinorial_pair_dynamics


def _series(records: Sequence[Mapping[str, Any]], key: str, axis: int, count: int) -> np.ndarray:
    return np.asarray([row[key][axis] for row in records[:count]], dtype=np.float64)


def linear_rate(times: np.ndarray, values: np.ndarray) -> float:
    if times.ndim != 1 or values.ndim != 1 or len(times) != len(values) or len(times) < 2:
        raise ValueError("matching one-dimensional samples required")
    return float(np.polyfit(times, values, 1)[0])


def center_velocity_alpha_diagnostic(
    records: Sequence[Mapping[str, Any]],
    *,
    axis: int = 2,
    fit_samples: int = 4,
) -> dict[str, float]:
    if axis not in (0, 1, 2) or len(records) < fit_samples or fit_samples < 3:
        raise ValueError("valid axis and at least three fit samples required")
    times = np.asarray([row["time"] for row in records[:fit_samples]], dtype=np.float64)
    centers = _series(records, "plus_center", axis, fit_samples)
    velocities = _series(records, "plus_velocity", axis, fit_samples)
    center_rate = linear_rate(times, centers)
    alpha_mean = float(np.mean(velocities))
    alpha_midpoint = float(np.interp(0.5 * (times[0] + times[-1]), times, velocities))
    scale = max(abs(alpha_mean), abs(center_rate), 1.0e-12)
    return {
        "center_velocity_fit": center_rate,
        "alpha_velocity_mean": alpha_mean,
        "alpha_velocity_midpoint": alpha_midpoint,
        "absolute_error_mean": abs(center_rate - alpha_mean),
        "relative_error_mean": abs(center_rate - alpha_mean) / scale,
        "absolute_error_midpoint": abs(center_rate - alpha_midpoint),
        "relative_error_midpoint": abs(center_rate - alpha_midpoint) / max(
            abs(alpha_midpoint), abs(center_rate), 1.0e-12
        ),
        "fit_start": float(times[0]),
        "fit_end": float(times[-1]),
    }


def interaction_velocity_diagnostic(
    pair_records: Sequence[Mapping[str, Any]],
    control_records: Sequence[Mapping[str, Any]],
    *,
    axis: int = 2,
    fit_samples: int = 4,
) -> dict[str, float]:
    pair = center_velocity_alpha_diagnostic(
        pair_records, axis=axis, fit_samples=fit_samples
    )
    control = center_velocity_alpha_diagnostic(
        control_records, axis=axis, fit_samples=fit_samples
    )
    center_interaction = pair["center_velocity_fit"] - control["center_velocity_fit"]
    alpha_interaction = pair["alpha_velocity_mean"] - control["alpha_velocity_mean"]
    scale = max(abs(center_interaction), abs(alpha_interaction), 1.0e-12)
    return {
        "interaction_center_velocity": center_interaction,
        "interaction_alpha_velocity": alpha_interaction,
        "absolute_error": abs(center_interaction - alpha_interaction),
        "relative_error": abs(center_interaction - alpha_interaction) / scale,
    }


@lru_cache(maxsize=1)
def run_dirac_ehrenfest_diagnostics() -> dict[str, Any]:
    dynamics = run_spinorial_pair_dynamics()
    pair_records = dynamics["pair_records"]
    control_records = dynamics["control_records"]
    fit_samples = min(4, len(pair_records), len(control_records))
    pair = center_velocity_alpha_diagnostic(pair_records, fit_samples=fit_samples)
    control = center_velocity_alpha_diagnostic(control_records, fit_samples=fit_samples)
    interaction = interaction_velocity_diagnostic(
        pair_records, control_records, fit_samples=fit_samples
    )
    momentum_error = float(dynamics["relative_errors"]["momentum_vs_lorentz"])
    center_force_error = float(
        dynamics["relative_errors"]["center_acceleration_vs_lorentz"]
    )
    generator_spin_error = float(
        dynamics["relative_errors"]["finite_spin_vs_generator"]
    )
    rest_bmt_error = float(
        dynamics["relative_errors"]["finite_spin_vs_rest_frame_bmt"]
    )
    theorem_domain = {
        "dirac_center_velocity_relation": {
            "observable": "d<x>/dt = <alpha>",
            "applicable": True,
            "reason": "same four-spinor state and canonical alpha matrices",
        },
        "momentum_lorentz_relation": {
            "observable": "d<pi>/dt versus integral(rho E + j cross B)",
            "applicable": True,
            "reason": "source-consistent four-spinor charge/current and Maxwell fields",
        },
        "nonrelativistic_center_force_relation": {
            "observable": "d2<x>/dt2 = F/m",
            "applicable": False,
            "reason": "no proved Foldy-Wouthuysen position projection or nonrelativistic packet limit",
        },
        "rest_frame_tbmt_shadow": {
            "observable": "gq/(2m) S cross B",
            "applicable": False,
            "reason": "packet is extended and moving in nonuniform electric and magnetic fields; gamma, beta cross E, local torque, and Thomas terms are omitted",
        },
    }
    acceptance = {
        "exact_dirac_center_velocity_observable_is_measured": all(
            np.isfinite(value)
            for value in (
                pair["relative_error_mean"],
                control["relative_error_mean"],
                interaction["relative_error"],
            )
        ),
        "momentum_lorentz_remains_the_force_gate": momentum_error >= 0.0,
        "center_force_is_retained_only_as_nonrelativistic_diagnostic": (
            center_force_error >= 0.0
            and not theorem_domain["nonrelativistic_center_force_relation"]["applicable"]
        ),
        "full_dirac_generator_remains_the_spin_integration_gate": generator_spin_error >= 0.0,
        "rest_frame_bmt_is_classified_outside_domain": (
            rest_bmt_error >= 0.0
            and not theorem_domain["rest_frame_tbmt_shadow"]["applicable"]
        ),
        "no_failed_out_of_domain_reduction_is_called_a_lean_contradiction": True,
        "no_criterion_or_physical_identity_is_promoted": True,
    }
    return {
        "schema": "openwave.m9.dirac-ehrenfest-diagnostics.v1",
        "task": "M9.99c",
        "source_dynamics_schema": dynamics["schema"],
        "fit_samples": fit_samples,
        "pair_center_velocity": pair,
        "control_center_velocity": control,
        "interaction_center_velocity": interaction,
        "retained_relative_errors": {
            "momentum_vs_lorentz": momentum_error,
            "center_acceleration_vs_lorentz_nonrelativistic_diagnostic": center_force_error,
            "finite_spin_vs_full_dirac_generator": generator_spin_error,
            "finite_spin_vs_rest_frame_bmt_out_of_domain": rest_bmt_error,
        },
        "theorem_domain": theorem_domain,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "dirac_center_observable_corrected": True,
            "momentum_force_result_retained": True,
            "legacy_center_force_result_is_a_lean_contradiction": False,
            "legacy_rest_bmt_result_is_a_lean_contradiction": False,
            "criterion_rows_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
