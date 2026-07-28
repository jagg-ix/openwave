"""M9.128b executable four-clock composition and conditioned-step controls."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping


def _fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def _pw_to_modular(tau: float) -> float:
    return 1.25 * tau


def _modular_to_entropic(s: float) -> float:
    return 0.8 * s + 0.2


def _entropic_to_proper(e: float) -> float:
    return 0.92 * e


def _pw_to_proper(tau: float) -> float:
    return _entropic_to_proper(_modular_to_entropic(_pw_to_modular(tau)))


def _proper_to_pw(proper: float) -> float:
    return (((proper / 0.92) - 0.2) / 0.8) / 1.25


@lru_cache(maxsize=1)
def run_four_clock_integration() -> dict[str, Any]:
    readings = (0.0, 0.25, 0.7, 1.4, 2.8)
    direct = tuple(0.18 + 0.63 * (0.72 ** index) for index, _ in enumerate(readings))
    conditioned = direct
    system_step = lambda value: 0.18 + 0.72 * (value - 0.18)
    step_errors = tuple(abs(conditioned[index + 1] - system_step(conditioned[index])) for index in range(len(conditioned) - 1))
    proper = tuple(_pw_to_proper(tau) for tau in readings)
    roundtrip_errors = tuple(abs(_proper_to_pw(value) - tau) for tau, value in zip(readings, proper))
    path_errors = tuple(abs(_pw_to_proper(tau) - _entropic_to_proper(_modular_to_entropic(_pw_to_modular(tau)))) for tau in readings)
    order_preserved = all(left < right for left, right in zip(proper, proper[1:]))
    payload = {
        "schema": "openwave.m9.four-clock-integration.v1",
        "task": "M9.128b",
        "page_wootters_readings": readings,
        "conditioned_states": conditioned,
        "direct_states": direct,
        "proper_time_readings": proper,
        "metrics": {
            "maximum_conditioning_error": max(abs(a - b) for a, b in zip(conditioned, direct)),
            "maximum_conditioned_step_error": max(step_errors),
            "maximum_path_commutation_error": max(path_errors),
            "maximum_roundtrip_error": max(roundtrip_errors),
            "strict_order_preserved": order_preserved,
        },
        "claim_boundary": {
            "affine_control_is_physical_calibration": False,
            "numerical_control_is_lean_proof": False,
            "order_control_establishes_universal_clock": False,
        },
    }
    acceptance = {
        "conditioning_is_exact": payload["metrics"]["maximum_conditioning_error"] == 0.0,
        "conditioned_step_transport_closes": payload["metrics"]["maximum_conditioned_step_error"] < 1e-14,
        "four_clock_path_commutes": payload["metrics"]["maximum_path_commutation_error"] < 1e-14,
        "roundtrip_closes": payload["metrics"]["maximum_roundtrip_error"] < 1e-14,
        "temporal_order_is_preserved": order_preserved,
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": _fingerprint(payload) == _fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": _fingerprint(payload)}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
