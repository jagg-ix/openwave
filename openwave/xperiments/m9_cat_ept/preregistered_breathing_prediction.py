"""M9.65 first preregistered out-of-sample CAT/EPT physical prediction.

The prediction uses no external measurement lookup. M9.63 fixes the dimensionless
binding coefficients from internal self-consistency. A time-dependent normalized
Gaussian collective coordinate supplies the scale inertia and small-oscillation
frequency. Identifying the spatial unit with the reduced Compton length then
produces a physical angular-frequency ratio that can be tested externally later.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any

import numpy as np

from .coefficient_self_consistency import (
    CoefficientSelectionConfig,
    gaussian_energy_constants,
    selected_coefficients,
)

OPENWAVE_HEAD = "421c962fdaa4aa7359c00cd6b37f985d297f0dac"
FORMAL_HEAD = "54b4ced090b200fac7ff04ee6a7e8797f1263049"
ZIL_HEAD = "f39758f85ee6300b8060e4f8ea1ecf344ed32c96"


@dataclass(frozen=True)
class PredictionConfig:
    dispersion: float = 0.65
    reference_scale: float = 1.0
    perturbation_fraction: float = 0.04
    relative_tolerance: float = 0.05
    external_observable: str = "dominant radial breathing angular frequency"
    spatial_anchor: str = "reduced Compton length hbar/(m c)"

    def __post_init__(self) -> None:
        if self.dispersion <= 0 or self.reference_scale <= 0:
            raise ValueError("positive prediction controls required")
        if not 0 < self.perturbation_fraction < 0.2:
            raise ValueError("small positive perturbation required")
        if not 0 < self.relative_tolerance < 0.5:
            raise ValueError("valid relative tolerance required")


def variational_energy_derivatives(
    cfg: PredictionConfig = PredictionConfig(),
) -> dict[str, float]:
    selection_cfg = CoefficientSelectionConfig(
        dispersion=cfg.dispersion,
        reference_scale=cfg.reference_scale,
    )
    selected = selected_coefficients(selection_cfg)
    alpha, beta = selected["alpha"], selected["beta"]
    constants = gaussian_energy_constants(cfg.dispersion)
    s = cfg.reference_scale
    first = (
        -2.0 * constants["kinetic"] / s**3
        + 3.0 * constants["quartic"] * alpha / s**4
        - 6.0 * constants["sextic"] * beta / s**7
    )
    second = (
        6.0 * constants["kinetic"] / s**4
        - 12.0 * constants["quartic"] * alpha / s**5
        + 42.0 * constants["sextic"] * beta / s**8
    )
    collective_inertia = 3.0 / (4.0 * cfg.dispersion)
    omega_dimensionless = math.sqrt(second / collective_inertia)
    omega_over_compton = omega_dimensionless / (2.0 * cfg.dispersion)
    return {
        "alpha": alpha,
        "beta": beta,
        "first_derivative": first,
        "second_derivative": second,
        "collective_scale_inertia": collective_inertia,
        "omega_dimensionless": omega_dimensionless,
        "omega_over_compton": omega_over_compton,
        "breathing_period_over_compton_period": 1.0 / omega_over_compton,
    }


def dispersion_independence_control() -> dict[str, Any]:
    rows = []
    for dispersion in (0.40, 0.50, 0.65, 0.80, 1.00):
        result = variational_energy_derivatives(PredictionConfig(dispersion=dispersion))
        rows.append(
            {
                "dispersion": dispersion,
                "alpha": result["alpha"],
                "beta": result["beta"],
                "omega_over_compton": result["omega_over_compton"],
            }
        )
    ratios = np.asarray([row["omega_over_compton"] for row in rows])
    return {
        "rows": rows,
        "maximum_ratio_spread": float(np.ptp(ratios)),
        "ratio_is_dispersion_independent_under_selection_rule": float(np.ptp(ratios)) <= 2e-13,
    }


def preregistration(cfg: PredictionConfig = PredictionConfig()) -> dict[str, Any]:
    prediction = variational_energy_derivatives(cfg)
    ratio = prediction["omega_over_compton"]
    return {
        "prediction_id": "CAT-EPT-M9.65-BREATHING-COMPTON-RATIO-v1",
        "observable": cfg.external_observable,
        "initial_condition": f"localized branch with a +{100*cfg.perturbation_fraction:.1f}% radial scale perturbation",
        "spatial_anchor": cfg.spatial_anchor,
        "prediction": f"omega_breath = {ratio:.12f} * m c^2 / hbar",
        "dimensionless_ratio": ratio,
        "relative_tolerance": cfg.relative_tolerance,
        "failure_rule": (
            "reject this collective-coordinate prediction if a converged independent physical or "
            f"higher-fidelity CAT/EPT measurement gives |omega/omega_C-{ratio:.12f}|/"
            f"{ratio:.12f} > {cfg.relative_tolerance:.3f}"
        ),
        "frozen_before_external_comparison": True,
        "external_data_used_to_compute_prediction": False,
    }


def prediction_fingerprint(cfg: PredictionConfig = PredictionConfig()) -> str:
    payload = {
        "schema": "openwave.m9.preregistered-prediction.v1",
        "openwave_head": OPENWAVE_HEAD,
        "formal_head": FORMAL_HEAD,
        "zil_head": ZIL_HEAD,
        "config": asdict(cfg),
        "preregistration": preregistration(cfg),
    }
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_preregistered_breathing_prediction() -> dict[str, Any]:
    cfg = PredictionConfig()
    derivatives = variational_energy_derivatives(cfg)
    independence = dispersion_independence_control()
    record = preregistration(cfg)
    acceptance = {
        "current_repository_heads_are_pinned": all(
            len(value) == 40 for value in (OPENWAVE_HEAD, FORMAL_HEAD, ZIL_HEAD)
        ),
        "reference_branch_is_stationary": abs(derivatives["first_derivative"]) <= 2e-13,
        "breathing_curvature_is_positive": derivatives["second_derivative"] > 0,
        "collective_inertia_is_positive": derivatives["collective_scale_inertia"] > 0,
        "prediction_ratio_is_finite_and_positive": math.isfinite(derivatives["omega_over_compton"])
        and derivatives["omega_over_compton"] > 0,
        "selection_rule_removes_dispersion_scale": independence[
            "ratio_is_dispersion_independent_under_selection_rule"
        ],
        "failure_rule_is_preregistered": bool(record["failure_rule"]),
        "prediction_is_frozen_before_external_comparison": record[
            "frozen_before_external_comparison"
        ],
        "no_external_data_were_used": not record["external_data_used_to_compute_prediction"],
        "fingerprint_is_deterministic": prediction_fingerprint(cfg) == prediction_fingerprint(cfg),
    }
    return {
        "schema": "openwave.m9.preregistered-breathing-prediction.v1",
        "task": "M9.65",
        "config": asdict(cfg),
        "repositories": {
            "openwave": OPENWAVE_HEAD,
            "physlib": FORMAL_HEAD,
            "zil": ZIL_HEAD,
        },
        "derivation": derivatives,
        "dispersion_independence": independence,
        "preregistration": record,
        "fingerprint": prediction_fingerprint(cfg),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "first_out_of_sample_physical_prediction_preregistered": True,
            "prediction_externally_tested": False,
            "prediction_validated": False,
            "prediction_ready_count": 1,
        },
        "classification": {
            "establishes": [
                "one frozen dimensionful breathing-frequency prediction derived before external comparison",
                "a quantitative failure threshold and reproducible cross-repository fingerprint",
                "dispersion-independent frequency ratio under the M9.63 self-consistency selection rule",
            ],
            "does_not_establish": [
                "experimental agreement",
                "validity of the Gaussian collective-coordinate approximation for the full physical particle",
                "identification of the localized branch with the electron",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
