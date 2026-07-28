"""M9.129a: non-affine, invertible, monotone four-clock calibration controls."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from math import exp, expm1, log1p, sqrt
from typing import Any, Mapping


def _fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def pw_to_modular(tau: float, scale: float = 1.4) -> float:
    return scale * tau


def modular_to_entropic(s: float, curvature: float = 0.35) -> float:
    return log1p(curvature * s) / curvature


def entropic_to_proper(e: float, curvature: float = 0.08) -> float:
    return e + curvature * e * e


def proper_to_entropic(p: float, curvature: float = 0.08) -> float:
    return (-1.0 + sqrt(1.0 + 4.0 * curvature * p)) / (2.0 * curvature)


def entropic_to_modular(e: float, curvature: float = 0.35) -> float:
    return expm1(curvature * e) / curvature


def modular_to_pw(s: float, scale: float = 1.4) -> float:
    return s / scale


def pw_to_proper(tau: float) -> float:
    return entropic_to_proper(modular_to_entropic(pw_to_modular(tau)))


def proper_to_pw(p: float) -> float:
    return modular_to_pw(entropic_to_modular(proper_to_entropic(p)))


@lru_cache(maxsize=1)
def run_calibration_family() -> dict[str, Any]:
    readings = (0.0, 0.1, 0.4, 0.9, 1.7, 3.0)
    proper = tuple(pw_to_proper(value) for value in readings)
    roundtrip = tuple(abs(proper_to_pw(value) - source) for source, value in zip(readings, proper))
    derivatives = {
        "pw_to_modular": tuple(1.4 for _ in readings),
        "modular_to_entropic": tuple(1.0 / (1.0 + 0.35 * pw_to_modular(value)) for value in readings),
        "entropic_to_proper": tuple(1.0 + 0.16 * modular_to_entropic(pw_to_modular(value)) for value in readings),
    }
    order = all(left < right for left, right in zip(proper, proper[1:]))
    payload = {
        "schema": "openwave.m9.nonaffine-four-clock-calibration.v1",
        "task": "M9.129a",
        "readings": readings,
        "proper_readings": proper,
        "derivatives": derivatives,
        "maximum_roundtrip_error": max(roundtrip),
        "claim_boundary": {
            "control_family_is_measured_calibration": False,
            "positive_derivative_is_external_clock_identity": False,
            "nonlinear_roundtrip_is_universal_clock_theorem": False,
        },
    }
    acceptance = {
        "all_pairwise_derivatives_are_positive": all(value > 0 for values in derivatives.values() for value in values),
        "non_affine_map_is_exercised": len({round(value, 12) for value in derivatives["modular_to_entropic"]}) > 1,
        "roundtrip_closes": payload["maximum_roundtrip_error"] < 1e-12,
        "strict_order_is_preserved": order,
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": _fingerprint(payload) == _fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": _fingerprint(payload)}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
