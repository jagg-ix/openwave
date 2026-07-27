"""M9.110e: weak/nonlinear gravity from one screen anchor and one matter state."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

import numpy as np

from .holographic_gravity_coupling import ScreenDensityAnchor, build_gravity_configs
from .electrogravitic_weak_field_evolution import electrogravitic_fields
from .nonlinear_constraint_gravity import constraint_fields
from .reconciled_gauge_spinor_stationary import normalize_spinor, reconciled_charge_current
from .reconciled_gauge_spinor_stationary_current import odd_grid_seed


def relative_error(a: float, b: float) -> float:
    return abs(a - b) / max(abs(a), abs(b), 1.0e-300)


def shared_initial_state(anchor: ScreenDensityAnchor) -> dict[str, Any]:
    configs = build_gravity_configs(anchor)
    weak = configs.weak
    nonlinear = configs.nonlinear
    matter = nonlinear.matter_config()

    scalar = odd_grid_seed(weak.action_config().reconciled_config())
    spinor = np.zeros((2, weak.points, weak.points, weak.points), dtype=np.complex128)
    spinor[0] = scalar
    spinor = normalize_spinor(spinor, weak.spacing)
    vector = tuple(np.zeros((weak.points,) * 3, dtype=np.float64) for _ in range(3))

    weak_fields = electrogravitic_fields(spinor, vector, weak)
    nonlinear_fields = electrogravitic_fields(spinor, vector, matter)
    geometry = matter.geometry()
    _, current = reconciled_charge_current(
        spinor,
        nonlinear_fields["vector_potential"],
        geometry,
        matter.action_config().reconciled_config(),
    )
    weak_phi = np.asarray(weak_fields["gravitational_potential"], dtype=np.float64)
    u0 = np.asarray(0.5 * weak_phi / matter.light_speed**2, dtype=np.float64)
    k0 = np.zeros_like(u0)
    constraints = constraint_fields(u0, k0, nonlinear_fields, current, nonlinear)

    source_error = float(
        np.linalg.norm(
            np.asarray(weak_fields["total_gravitational_source"])
            - np.asarray(nonlinear_fields["total_gravitational_source"])
        )
        / max(float(np.linalg.norm(weak_fields["total_gravitational_source"])), 1.0e-300)
    )
    potential_error = float(
        np.linalg.norm(
            np.asarray(weak_fields["gravitational_potential"])
            - np.asarray(nonlinear_fields["gravitational_potential"])
        )
        / max(float(np.linalg.norm(weak_fields["gravitational_potential"])), 1.0e-300)
    )
    expected_u = 0.25 * (np.asarray(weak_fields["metric_g00"]) - 1.0)
    metric_seed_error = float(
        np.linalg.norm(u0 - expected_u) / max(float(np.linalg.norm(expected_u)), 1.0e-300)
    )

    return {
        "screen_newton_coupling": anchor.newton_coupling,
        "weak_newton_coupling": weak.newton_coupling,
        "nonlinear_newton_coupling": matter.newton_coupling,
        "source_relative_error": source_error,
        "potential_relative_error": potential_error,
        "metric_seed_relative_error": metric_seed_error,
        "weak_minimum_g00": float(np.min(weak_fields["metric_g00"])),
        "initial_hamiltonian_relative": float(constraints["hamiltonian_relative"]),
        "initial_momentum_relative": float(constraints["momentum_relative"]),
        "initial_max_abs_u": float(np.max(np.abs(u0))),
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_shared_screen_gravity_campaign() -> dict[str, Any]:
    anchor = ScreenDensityAnchor(
        area=2.0,
        bits=8.0,
        evidence_class="external",
        source="synthetic shared-screen fixture; not physical evidence",
    )
    observables = shared_initial_state(anchor)
    acceptance = {
        "one_screen_G_reaches_both_models": max(
            relative_error(observables["screen_newton_coupling"], observables["weak_newton_coupling"]),
            relative_error(observables["screen_newton_coupling"], observables["nonlinear_newton_coupling"]),
        ) <= 5.0e-15,
        "one_matter_source_is_shared": observables["source_relative_error"] <= 5.0e-15,
        "one_weak_potential_is_shared": observables["potential_relative_error"] <= 5.0e-15,
        "nonlinear_metric_seed_matches_weak_g00": observables["metric_seed_relative_error"] <= 5.0e-13,
        "initial_constraints_are_finite": np.isfinite(observables["initial_hamiltonian_relative"])
        and np.isfinite(observables["initial_momentum_relative"]),
        "synthetic_anchor_is_not_physical_calibration": True,
    }
    payload = {
        "schema": "openwave.m9.shared-screen-gravity-campaign.v1",
        "task": "M9.110e",
        "anchor": {
            "area": anchor.area,
            "bits": anchor.bits,
            "area_per_bit": anchor.area_per_bit,
            "newton_coupling": anchor.newton_coupling,
            "epistemic_status": "synthetic-fixture-not-physical-evidence",
        },
        "observables": observables,
        "claim_boundary": {
            "shared_initial_observables_are_full_GR_equivalence": False,
            "finite_constraints_are_constraint_closure": False,
            "synthetic_anchor_is_external_calibration": False,
        },
        "acceptance": acceptance,
    }
    return {
        **payload,
        "passed": all(acceptance.values()) and not any(payload["claim_boundary"].values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "shared_screen_source_potential_and_metric_seed_constructed": True,
            "full_nonlinear_time_evolution_compared": False,
            "physical_screen_density_calibrated": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
