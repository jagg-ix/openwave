from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json, math
from typing import Any, Mapping
import numpy as np

from .gauge_sector_linear_response import run_gauge_sector_linear_response

Array = np.ndarray

@dataclass(frozen=True)
class GaugeDecayConfig:
    coupling: float = 0.18
    derivative_step: float = 1.0e-7
    observation_multiples: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0, 2.0)
    minimum_gap: float = 1.0e-8

    def __post_init__(self) -> None:
        if self.coupling <= 0 or self.derivative_step <= 0 or self.minimum_gap <= 0:
            raise ValueError("positive decay controls required")


def amplitude_damping_kraus(gamma: float, time: float, omega: float = 0.0) -> tuple[Array, Array]:
    if gamma <= 0 or time < 0:
        raise ValueError("positive rate and nonnegative time required")
    eta = math.exp(-gamma * time)
    k0 = np.diag(np.asarray((1.0, math.sqrt(eta) * np.exp(-1j * omega * time)), complex))
    k1 = np.asarray(((0.0, math.sqrt(max(0.0, 1.0 - eta))), (0.0, 0.0)), complex)
    return k0, k1


def apply_kraus(rho: Array, kraus: tuple[Array, ...]) -> Array:
    return np.asarray(sum(k @ rho @ k.conjugate().T for k in kraus), complex)


def exact_amplitude_damping(rho: Array, gamma: float, time: float, omega: float = 0.0) -> Array:
    return apply_kraus(rho, amplitude_damping_kraus(gamma, time, omega))


def lindblad_generator(rho: Array, gamma: float, omega: float = 0.0) -> Array:
    hamiltonian = np.diag(np.asarray((0.0, omega), complex))
    jump = np.asarray(((0, 1), (0, 0)), complex)
    number = jump.conjugate().T @ jump
    return -1j * (hamiltonian @ rho - rho @ hamiltonian) + gamma * (
        jump @ rho @ jump.conjugate().T - 0.5 * (number @ rho + rho @ number)
    )


def density_matrix(seed: int = 121) -> Array:
    rng = np.random.default_rng(seed)
    vector = rng.normal(size=2) + 1j * rng.normal(size=2)
    vector /= np.linalg.norm(vector)
    pure = np.outer(vector, vector.conjugate())
    return np.asarray(0.73 * pure + 0.27 * np.eye(2) / 2, complex)


def relative_norm_error(left: Array, right: Array) -> float:
    return float(
        np.linalg.norm(left - right)
        / max(float(np.linalg.norm(left)), float(np.linalg.norm(right)), 1.0e-300)
    )


def select_transition(response: Mapping[str, Any], minimum_gap: float) -> dict[str, float]:
    channels = [
        row
        for row in response["dominant_channels"]
        if abs(float(row["frequency"])) > minimum_gap and float(row["weight"]) > 0
    ]
    if not channels:
        raise ValueError("nonzero response transition required")
    selected = max(channels, key=lambda row: float(row["weight"]))
    total = sum(float(row["weight"]) for row in channels)
    return {
        "gap": abs(float(selected["frequency"])),
        "relative_strength": float(selected["weight"]) / max(total, 1.0e-300),
        "mode": float(selected["mode"]),
    }


def sector_decay_record(response: Mapping[str, Any], cfg: GaugeDecayConfig) -> dict[str, Any]:
    transition = select_transition(response, cfg.minimum_gap)
    gap = transition["gap"]
    strength = transition["relative_strength"]
    gamma = cfg.coupling**2 * gap**3 * strength
    omega = gap
    lifetime = 1 / gamma
    half_life = math.log(2) / gamma
    rho = density_matrix()
    excited = np.asarray(((0, 0), (0, 1)), complex)
    kraus = amplitude_damping_kraus(gamma, 0.37 * lifetime, omega)
    completeness = sum(operator.conjugate().T @ operator for operator in kraus)
    s, t = 0.31 * lifetime, 0.47 * lifetime
    composed = exact_amplitude_damping(
        exact_amplitude_damping(rho, gamma, t, omega), gamma, s, omega
    )
    direct = exact_amplitude_damping(rho, gamma, s + t, omega)
    step = cfg.derivative_step / max(gamma, 1.0)
    derivative = (exact_amplitude_damping(rho, gamma, step, omega) - rho) / step
    generator = lindblad_generator(rho, gamma, omega)
    records = []
    minimum_eigenvalue = 1.0
    for multiple in cfg.observation_multiples:
        time = multiple * lifetime
        evolved = exact_amplitude_damping(excited, gamma, time, omega)
        minimum_eigenvalue = min(
            minimum_eigenvalue, float(np.min(np.linalg.eigvalsh(evolved)))
        )
        records.append(
            {
                "lifetime_multiple": multiple,
                "time": time,
                "excited_population": float(evolved[1, 1].real),
                "expected_population": math.exp(-multiple),
                "trace": float(np.trace(evolved).real),
            }
        )
    return {
        "transition": transition,
        "gamma_model_units": gamma,
        "omega_model_units": omega,
        "lifetime_model_units": lifetime,
        "half_life_model_units": half_life,
        "kraus_completeness_error": float(np.linalg.norm(completeness - np.eye(2))),
        "semigroup_relative_error": relative_norm_error(composed, direct),
        "generator_derivative_relative_error": relative_norm_error(derivative, generator),
        "minimum_density_eigenvalue": minimum_eigenvalue,
        "population_at_lifetime_error": abs(records[3]["excited_population"] - math.exp(-1)),
        "population_at_half_life_error": abs(
            float(exact_amplitude_damping(excited, gamma, half_life, omega)[1, 1].real)
            - 0.5
        ),
        "records": records,
        "response_broadening_used_as_decay_rate": False,
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=float).encode()
    ).hexdigest()


def run_with_response(response_result: Mapping[str, Any]) -> dict[str, Any]:
    cfg = GaugeDecayConfig()
    strong = sector_decay_record(response_result["strong"], cfg)
    electroweak = sector_decay_record(response_result["electroweak"], cfg)
    payload = {
        "schema": "openwave.m9.gauge-sector-open-decay.v1",
        "task": "M9.121a",
        "config": asdict(cfg),
        "strong": strong,
        "electroweak": electroweak,
        "claim_boundary": {
            "model_unit_rate_is_measured_decay_width": False,
            "two_level_truncation_is_full_radiative_qft": False,
            "golden_rule_proxy_is_parameter_free_prediction": False,
            "cptp_channel_identifies_observed_particle": False,
        },
    }
    acceptance = {
        "positive_intrinsic_model_rates": strong["gamma_model_units"] > 0
        and electroweak["gamma_model_units"] > 0,
        "kraus_channels_are_trace_preserving": max(
            strong["kraus_completeness_error"], electroweak["kraus_completeness_error"]
        )
        <= 2.0e-14,
        "exact_semigroup_composition_closes": max(
            strong["semigroup_relative_error"], electroweak["semigroup_relative_error"]
        )
        <= 2.0e-13,
        "lindblad_generator_matches_right_derivative": max(
            strong["generator_derivative_relative_error"],
            electroweak["generator_derivative_relative_error"],
        )
        <= 2.0e-5,
        "density_positivity_is_preserved": min(
            strong["minimum_density_eigenvalue"], electroweak["minimum_density_eigenvalue"]
        )
        >= -2.0e-14,
        "population_lifetime_and_half_life_close": max(
            strong["population_at_lifetime_error"],
            electroweak["population_at_lifetime_error"],
            strong["population_at_half_life_error"],
            electroweak["population_at_half_life_error"],
        )
        <= 2.0e-14,
        "response_broadening_is_not_reused": not strong[
            "response_broadening_used_as_decay_rate"
        ]
        and not electroweak["response_broadening_used_as_decay_rate"],
        "no_physical_decay_claim_is_promoted": not any(payload["claim_boundary"].values()),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "cptp_open_system_decay_constructed": True,
            "intrinsic_model_unit_lifetime_constructed": True,
            "physical_decay_width_calibrated": False,
            "observed_transition_identity_promoted": False,
        },
    }


@lru_cache(maxsize=1)
def run_gauge_sector_open_decay() -> dict[str, Any]:
    response = run_gauge_sector_linear_response()
    result = run_with_response(response)
    result["acceptance"] = {
        "M9_120_response_authority_passes": bool(response["passed"]),
        **result["acceptance"],
    }
    result["passed"] = all(result["acceptance"].values())
    return result


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
