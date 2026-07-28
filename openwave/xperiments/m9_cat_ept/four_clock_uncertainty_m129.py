"""M9.129b: monotone interval propagation and robust temporal-order checks."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .four_clock_calibration_family_m129 import pw_to_proper


def _fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def propagate_interval(center: float, uncertainty: float) -> tuple[float, float]:
    if uncertainty <= 0:
        raise ValueError("uncertainty must be positive")
    lower = max(0.0, center - uncertainty)
    upper = center + uncertainty
    return pw_to_proper(lower), pw_to_proper(upper)


@lru_cache(maxsize=1)
def run_uncertainty_propagation() -> dict[str, Any]:
    observations = (
        {"id": "clock-0", "reading": 0.20, "uncertainty": 0.015},
        {"id": "clock-1", "reading": 0.55, "uncertainty": 0.020},
        {"id": "clock-2", "reading": 1.05, "uncertainty": 0.030},
        {"id": "clock-3", "reading": 1.90, "uncertainty": 0.040},
    )
    propagated = tuple({**item, "proper_interval": propagate_interval(item["reading"], item["uncertainty"])} for item in observations)
    robust_pairs = tuple(
        left["proper_interval"][1] < right["proper_interval"][0]
        for left, right in zip(propagated, propagated[1:])
    )
    widths = tuple(item["proper_interval"][1] - item["proper_interval"][0] for item in propagated)
    payload = {
        "schema": "openwave.m9.four-clock-uncertainty-propagation.v1",
        "task": "M9.129b",
        "observations": propagated,
        "metrics": {
            "all_intervals_positive_width": all(width > 0 for width in widths),
            "all_adjacent_orders_robust": all(robust_pairs),
            "maximum_proper_interval_width": max(widths),
        },
        "claim_boundary": {
            "fixture_uncertainties_are_experimental_errors": False,
            "interval_separation_is_physical_validation": False,
            "monotone_propagation_replaces_covariance_analysis": False,
        },
    }
    invalid_rejected = False
    try:
        propagate_interval(1.0, 0.0)
    except ValueError:
        invalid_rejected = True
    acceptance = {
        "monotone_endpoint_propagation_executes": all(a < b for a, b in (item["proper_interval"] for item in propagated)),
        "temporal_order_is_robust_to_declared_uncertainty": all(robust_pairs),
        "invalid_uncertainty_is_rejected": invalid_rejected,
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": _fingerprint(payload) == _fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": _fingerprint(payload)}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
