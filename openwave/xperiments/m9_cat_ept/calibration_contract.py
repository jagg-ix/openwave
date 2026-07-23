"""M9.19 physical-calibration and observable-contract qualification.

The current M9 back-reaction models are dimensionless. This module makes the
additional calibration information required for SI-valued predictions explicit.
It also demonstrates the rate/time-scale degeneracy that remains when no
independent physical time anchor is supplied.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Iterable

import numpy as np

MECHANISMS = ("imaginary_action", "lindblad_dephasing", "explicit_reservoir")


@dataclass(frozen=True)
class CalibrationAnchors:
    time_scale_seconds: float
    trace_efficiency: float
    coherence_efficiency: float
    reservoir_efficiency: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.time_scale_seconds) or self.time_scale_seconds <= 0.0:
            raise ValueError("time_scale_seconds must be finite and positive")
        for name in (
            "trace_efficiency",
            "coherence_efficiency",
            "reservoir_efficiency",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0.0 < value <= 1.0:
                raise ValueError(f"{name} must lie in (0,1]")


@dataclass(frozen=True)
class CalibrationContract:
    schema: str
    time_unit: str
    trace_observable: str
    purity_observable: str
    coherence_observable: str
    reservoir_observable: str
    anchors: CalibrationAnchors

    def __post_init__(self) -> None:
        if self.schema != "openwave.m9.calibration-contract.v1":
            raise ValueError("unsupported calibration contract schema")
        if self.time_unit != "s":
            raise ValueError("time_unit must be SI seconds")
        for name in (
            "trace_observable",
            "purity_observable",
            "coherence_observable",
            "reservoir_observable",
        ):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be nonempty")


def default_contract() -> CalibrationContract:
    return CalibrationContract(
        schema="openwave.m9.calibration-contract.v1",
        time_unit="s",
        trace_observable="accessible normalized count fraction",
        purity_observable="normalized two-copy purity estimator",
        coherence_observable="normalized off-diagonal coherence fraction",
        reservoir_observable="captured reservoir-transfer fraction",
        anchors=CalibrationAnchors(
            time_scale_seconds=2.5e-6,
            trace_efficiency=0.91,
            coherence_efficiency=0.88,
            reservoir_efficiency=0.84,
        ),
    )


def physical_rate_per_second(rate_dimensionless: float, anchors: CalibrationAnchors) -> float:
    if rate_dimensionless < 0.0 or not math.isfinite(rate_dimensionless):
        raise ValueError("rate_dimensionless must be finite and nonnegative")
    return rate_dimensionless / anchors.time_scale_seconds


def dimensionless_time(time_seconds: float, anchors: CalibrationAnchors) -> float:
    if time_seconds < 0.0 or not math.isfinite(time_seconds):
        raise ValueError("time_seconds must be finite and nonnegative")
    return time_seconds / anchors.time_scale_seconds


def calibrated_signature(
    mechanism: str,
    time_seconds: float,
    rate_dimensionless: float,
    contract: CalibrationContract,
) -> dict[str, float]:
    if mechanism not in MECHANISMS:
        raise KeyError(f"unknown mechanism: {mechanism}")
    u = dimensionless_time(time_seconds, contract.anchors)
    decay = math.exp(-rate_dimensionless * u)
    if mechanism == "imaginary_action":
        trace = contract.anchors.trace_efficiency * decay**2
        purity = 1.0
        coherence = contract.anchors.coherence_efficiency
        reservoir = 0.0
    elif mechanism == "lindblad_dephasing":
        trace = contract.anchors.trace_efficiency
        purity = 0.5 + 0.5 * decay**4
        coherence = contract.anchors.coherence_efficiency * decay**2
        reservoir = 0.0
    else:
        trace = contract.anchors.trace_efficiency * decay
        purity = 1.0
        coherence = contract.anchors.coherence_efficiency * math.sqrt(decay)
        reservoir = contract.anchors.reservoir_efficiency * (1.0 - decay)
    return {
        "time_seconds": time_seconds,
        "accessible_trace": trace,
        "normalized_purity": purity,
        "measured_coherence": coherence,
        "reservoir_transfer": reservoir,
    }


def recover_rate_from_pair(
    mechanism: str,
    first: dict[str, float],
    second: dict[str, float],
    contract: CalibrationContract,
) -> float:
    delta_u = dimensionless_time(
        second["time_seconds"] - first["time_seconds"],
        contract.anchors,
    )
    if delta_u <= 0.0:
        raise ValueError("observation times must be strictly increasing")
    if mechanism == "imaginary_action":
        ratio = second["accessible_trace"] / first["accessible_trace"]
        factor = 2.0
    elif mechanism == "lindblad_dephasing":
        ratio = second["measured_coherence"] / first["measured_coherence"]
        factor = 2.0
    elif mechanism == "explicit_reservoir":
        ratio = second["accessible_trace"] / first["accessible_trace"]
        factor = 1.0
    else:
        raise KeyError(f"unknown mechanism: {mechanism}")
    return -math.log(ratio) / (factor * delta_u)


def rate_time_jacobian(
    times_seconds: Iterable[float],
    *,
    rate_dimensionless: float,
    time_scale_seconds: float,
    include_time_anchor: bool,
) -> np.ndarray:
    times = np.asarray(tuple(times_seconds), dtype=np.float64)
    if times.size < 2:
        raise ValueError("at least two times are required")
    u = times / time_scale_seconds
    trace = np.exp(-2.0 * rate_dimensionless * u)
    # Derivatives with respect to log(rate) and log(time scale).
    first = -2.0 * rate_dimensionless * u * trace
    second = -first
    rows = np.column_stack((first, second))
    if include_time_anchor:
        rows = np.vstack((rows, np.asarray([0.0, 1.0])))
    return rows


def identifiability_audit(contract: CalibrationContract) -> dict[str, Any]:
    times = np.linspace(0.5, 4.0, 8) * contract.anchors.time_scale_seconds
    without_anchor = rate_time_jacobian(
        times,
        rate_dimensionless=0.17,
        time_scale_seconds=contract.anchors.time_scale_seconds,
        include_time_anchor=False,
    )
    with_anchor = rate_time_jacobian(
        times,
        rate_dimensionless=0.17,
        time_scale_seconds=contract.anchors.time_scale_seconds,
        include_time_anchor=True,
    )
    return {
        "rank_without_time_anchor": int(np.linalg.matrix_rank(without_anchor, tol=1e-12)),
        "rank_with_time_anchor": int(np.linalg.matrix_rank(with_anchor, tol=1e-12)),
        "parameters": 2,
        "unanchored_null_vector_residual": float(
            np.linalg.norm(without_anchor @ np.asarray([1.0, 1.0]))
        ),
        "condition_number_with_anchor": float(np.linalg.cond(with_anchor)),
    }


def synthetic_roundtrip(contract: CalibrationContract) -> dict[str, Any]:
    rates = {
        "imaginary_action": 0.17,
        "lindblad_dephasing": 0.23,
        "explicit_reservoir": 0.12,
    }
    times = (1.0e-6, 7.5e-6)
    recovered: dict[str, float] = {}
    errors: dict[str, float = {}
    for mechanism, rate in rates.items():
        first = calibrated_signature(mechanism, times[0], rate, contract)
        second = calibrated_signature(mechanism, times[1], rate, contract)
        recovered_rate = recover_rate_from_pair(mechanism, first, second, contract)
        recovered[mechanism] = recovered_rate
        errors[mechanism] = abs(recovered_rate - rate)
    return {
        "rates_dimensionless": rates,
        "rates_per_second": {
            name: physical_rate_per_second(value, contract.anchors)
            for name, value in rates.items()
        },
        "recovered_dimensionless": recovered,
        "absolute_errors": errors,
        "maximum_absolute_error": max(errors.values()),
        "synthetic_only": True,
    }


def missing_anchor_rejections() -> dict[str, bool]:
    cases = {
        "zero_time_scale": dict(time_scale_seconds=0.0),
        "trace_efficiency_above_one": dict(trace_efficiency=1.1),
        "zero_coherence_efficiency": dict(coherence_efficiency=0.0),
        "negative_reservoir_efficiency": dict(reservoir_efficiency=-0.1),
    }
    results: dict[str, bool] = {}
    base = asdict(default_contract().anchors)
    for name, patch in cases.items():
        values = dict(base)
        values.update(patch)
        try:
            CalibrationAnchors(**values)
        except ValueError:
            results[name] = True
        else:
            results[name] = False
    return results


@lru_cache(maxsize=1)
def run_calibration_contract_study() -> dict[str, Any]:
    contract = default_contract()
    identifiability = identifiability_audit(contract)
    roundtrip = synthetic_roundtrip(contract)
    rejections = missing_anchor_rejections()
    acceptance = {
        "contract_schema_valid": contract.schema == "openwave.m9.calibration-contract.v1",
        "si_time_anchor_positive": contract.anchors.time_scale_seconds > 0.0,
        "efficiencies_bounded": all(
            0.0 < value <= 1.0
            for value in (
                contract.anchors.trace_efficiency,
                contract.anchors.coherence_efficiency,
                contract.anchors.reservoir_efficiency,
            )
        ),
        "unanchored_rate_scale_is_rank_deficient": (
            identifiability["rank_without_time_anchor"] == 1
            and identifiability["unanchored_null_vector_residual"] <= 1e-12
        ),
        "time_anchor_restores_local_rank": identifiability["rank_with_time_anchor"] == 2,
        "synthetic_roundtrip_closes": roundtrip["maximum_absolute_error"] <= 2e-14,
        "missing_anchors_rejected": all(rejections.values()),
        "physical_calibration_not_promoted": roundtrip["synthetic_only"],
    }
    return {
        "schema": "openwave.m9.calibration-contract-result.v1",
        "task": "M9.19",
        "contract": {
            **asdict(contract),
            "anchors": asdict(contract.anchors),
        },
        "required_metadata": [
            "SI time-scale anchor with uncertainty and provenance",
            "trace-channel efficiency calibration",
            "coherence/purity estimator calibration",
            "reservoir-capture efficiency calibration",
            "blinded mechanism-independent acquisition times",
        ],
        "identifiability": identifiability,
        "synthetic_roundtrip": roundtrip,
        "missing_anchor_rejections": rejections,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "physical_calibration_completed": False,
        "classification": {
            "establishes": [
                "a machine-readable SI calibration and observable contract",
                "the unanchored rate/time-scale degeneracy",
                "local rank restoration after an independent time anchor",
                "exact synthetic parameter roundtrip for all three interfaces",
            ],
            "does_not_establish": [
                "an experimentally measured time scale or detector efficiency",
                "physical values of the selected dimensionless rates",
                "which back-reaction interface is realized in Nature",
                "particle identity or experimental agreement",
            ],
        },
    }


def result_to_json(result: dict[str, A[ž]
HOˆÝŽ‚ˆ™]\›ˆœÛÛ‹™[\Ê™\Ý[[™[L‹ÛÜÚÙ^\ÏUYKY˜][Y›Ø]
H
È—ˆ‚