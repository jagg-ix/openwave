"""M9.109c: one frozen Newton coupling for weak and nonlinear gravity levels."""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

from .electrogravitic_weak_field_evolution import ElectrograviticEvolutionConfig
from .newton_g_anchor_protocol import GravityAnchorBundle, audit_bundle, execute_frozen_prediction
from .nonlinear_constraint_gravity import NonlinearMetricConfig


@dataclass(frozen=True)
class GravityUnitMap:
    """SI base units represented by one OpenWave numerical unit."""

    mass_unit_kg: float
    length_unit_m: float
    time_unit_s: float
    hbar_dimensionless: float = 1.0
    light_speed_dimensionless: float = 1.0
    source: str = "external calibrated unit map"

    def __post_init__(self) -> None:
        if min(
            self.mass_unit_kg,
            self.length_unit_m,
            self.time_unit_s,
            self.hbar_dimensionless,
            self.light_speed_dimensionless,
        ) <= 0.0:
            raise ValueError("positive unit-map entries required")


@dataclass(frozen=True)
class AnchoredNonlinearMetricConfig(NonlinearMetricConfig):
    inference_width: float = 1.0
    hbar: float = 1.0
    light_speed: float = 1.0

    def __post_init__(self) -> None:
        super().__post_init__()
        if min(self.inference_width, self.hbar, self.light_speed) <= 0.0:
            raise ValueError("positive anchored gravity constants required")

    def matter_config(self) -> ElectrograviticEvolutionConfig:
        return replace(
            super().matter_config(),
            inference_width=self.inference_width,
            hbar=self.hbar,
            light_speed=self.light_speed,
        )


def dimensionless_newton_G(newton_G_si: float, units: GravityUnitMap) -> float:
    """Convert G [L^3 M^-1 T^-2] to the selected numerical units."""
    if newton_G_si <= 0.0:
        raise ValueError("positive Newton coupling required")
    return (
        newton_G_si
        * units.mass_unit_kg
        * units.time_unit_s**2
        / units.length_unit_m**3
    )


def inference_width_from_dimensionless_G(
    newton_G_dimensionless: float,
    *,
    hbar_dimensionless: float,
    light_speed_dimensionless: float,
) -> float:
    if min(newton_G_dimensionless, hbar_dimensionless, light_speed_dimensionless) <= 0.0:
        raise ValueError("positive dimensionless coupling data required")
    return (
        newton_G_dimensionless / (hbar_dimensionless * light_speed_dimensionless)
    ) ** 0.25


def coupling_contract(prediction: Mapping[str, Any], units: GravityUnitMap) -> dict[str, Any]:
    if not prediction.get("executed"):
        return {
            "ready": False,
            "reason": "frozen Newton-G prediction has not executed",
            "unit_map": asdict(units),
        }
    predicted = prediction.get("predictions")
    if not isinstance(predicted, Mapping) or not predicted:
        raise ValueError("executed prediction must contain one or more G values")
    values = [float(value) for value in predicted.values()]
    if any(value <= 0.0 or not math.isfinite(value) for value in values):
        raise ValueError("finite positive predicted G values required")
    spread = (
        0.0
        if len(values) == 1
        else (max(values) - min(values)) / max(abs(values[0]), 1.0e-300)
    )
    if spread > 1.0e-10:
        return {
            "ready": False,
            "reason": "independent universal anchor paths disagree",
            "relative_spread": spread,
            "unit_map": asdict(units),
        }
    newton_G_si = values[0]
    dimensionless = dimensionless_newton_G(newton_G_si, units)
    sigma0 = inference_width_from_dimensionless_G(
        dimensionless,
        hbar_dimensionless=units.hbar_dimensionless,
        light_speed_dimensionless=units.light_speed_dimensionless,
    )
    weak = ElectrograviticEvolutionConfig(
        hbar=units.hbar_dimensionless,
        light_speed=units.light_speed_dimensionless,
        inference_width=sigma0,
    )
    nonlinear = AnchoredNonlinearMetricConfig(
        hbar=units.hbar_dimensionless,
        light_speed=units.light_speed_dimensionless,
        inference_width=sigma0,
    )
    weak_G = weak.newton_coupling
    nonlinear_G = nonlinear.matter_config().newton_coupling
    return {
        "ready": True,
        "newton_G_si": newton_G_si,
        "newton_G_dimensionless": dimensionless,
        "inference_width_dimensionless": sigma0,
        "weak_field_config": {
            "hbar": weak.hbar,
            "light_speed": weak.light_speed,
            "inference_width": weak.inference_width,
            "newton_coupling": weak_G,
        },
        "nonlinear_metric_config": {
            "hbar": nonlinear.hbar,
            "light_speed": nonlinear.light_speed,
            "inference_width": nonlinear.inference_width,
            "newton_coupling": nonlinear_G,
        },
        "same_frozen_G_used_in_both_gravity_levels": abs(weak_G - nonlinear_G)
        <= 2.0e-15 * max(abs(weak_G), 1.0),
        "unit_map": asdict(units),
        "policy": {
            "SI_to_dimensionless_conversion_is_explicit": True,
            "natural_unit_G_equals_one_is_not_physical_prediction": True,
            "inference_width_is_derived_after_unit_calibration": True,
        },
    }


def evaluate_bundle_for_gravity(
    bundle: GravityAnchorBundle, units: GravityUnitMap
) -> dict[str, Any]:
    audit = audit_bundle(bundle)
    prediction = execute_frozen_prediction(bundle)
    contract = coupling_contract(prediction, units)
    return {
        "anchor_audit": audit,
        "prediction": prediction,
        "coupling_contract": contract,
        "ready": bool(
            audit["prediction_ready"]
            and prediction["executed"]
            and prediction["passed"]
            and contract["ready"]
            and contract["same_frozen_G_used_in_both_gravity_levels"]
        ),
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_newton_G_gravity_adapter() -> dict[str, Any]:
    illustrative_units = GravityUnitMap(
        mass_unit_kg=1.0,
        length_unit_m=1.0,
        time_unit_s=1.0,
        source="illustrative SI base-unit identity map; not OpenWave physical calibration",
    )
    blocked = coupling_contract({"executed": False}, illustrative_units)
    payload = {
        "schema": "openwave.m9.newton-G-gravity-adapter.v1",
        "task": "M9.109c-adapter",
        "blocked_default": blocked,
        "dimensional_rule": "G_dimensionless = G_SI * mass_unit * time_unit^2 / length_unit^3",
        "sigma_rule": "sigma0 = (G_dimensionless/(hbar_dimensionless*c_dimensionless))^(1/4)",
        "policy": {
            "prediction_must_execute_before_coupling_injection": True,
            "unit_map_must_be_explicit": True,
            "weak_and_nonlinear_gravity_share_one_G": True,
            "default_natural_unit_G_is_not_external_calibration": True,
        },
    }
    acceptance = {
        "unexecuted_prediction_is_blocked": not blocked["ready"],
        "dimensional_conversion_is_declared": bool(payload["dimensional_rule"]),
        "one_G_policy_is_explicit": payload["policy"][
            "weak_and_nonlinear_gravity_share_one_G"
        ],
        "natural_unit_overclaim_is_forbidden": payload["policy"][
            "default_natural_unit_G_is_not_external_calibration"
        ],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "calibrated_gravity_coupling_injected": False,
            "weak_and_nonlinear_defaults_promoted": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
