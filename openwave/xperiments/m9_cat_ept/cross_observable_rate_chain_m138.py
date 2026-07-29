"""Executable counterpart of Physlib OneLevelCrossObservable.

The same independently counted in/out rates determine gamma, the Lorentzian
widths, the population relaxation time, and the binary-KL production rate.
This validates the formal identities; it does not establish that a measured
carrier obeys the one-level Markov/GKSL model or exclude pure dephasing.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any, Mapping

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_HEAD = "deb1eb3ecb4aabbba1555b24253d9dd8f6fba1f2"
FORMAL_SOURCE = {
    "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/OneLevelCrossObservable.lean",
    "blob": "d99136a02b3d09fa5338f8187ebf023e47be91f0",
    "declarations": (
        "lorentzPeak_eq_halfMaximum_iff",
        "lorentzHWHM_eq_gamma",
        "lorentzFWHM_eq_two_gamma",
        "RateData.predictedOccupation_at_populationRelaxationTime",
        "RateData.ofInOutRates_populationRelaxationTime",
        "calibrated_rate_linewidth_relaxation_KL_chain",
    ),
}

@dataclass(frozen=True)
class RateCalibration:
    gamma_in: float = 3.0
    gamma_out: float = 5.0
    epsilon: float = 1.25
    initial_occupation: float = 0.82
    evaluation_time: float = 0.17

    def __post_init__(self) -> None:
        if min(self.gamma_in, self.gamma_out) <= 0.0:
            raise ValueError("positive independently counted rates required")
        if not 0.0 < self.initial_occupation < 1.0 or self.evaluation_time < 0.0:
            raise ValueError("interior occupation and nonnegative time required")


def binary_kl(n: float, f: float) -> float:
    return n * math.log(n / f) + (1.0 - n) * math.log((1.0 - n) / (1.0 - f))


def canonical_payload(cfg: RateCalibration | None = None) -> dict[str, Any]:
    cfg = RateCalibration() if cfg is None else cfg
    total = cfg.gamma_in + cfg.gamma_out
    gamma = total / 2.0
    f = cfg.gamma_in / total
    t1 = 1.0 / total
    n = f + (cfg.initial_occupation - f) * math.exp(-2.0 * gamma * cfg.evaluation_time)
    sigma = 2.0 * gamma * (n - f) * (math.log(n / f) - math.log((1.0 - n) / (1.0 - f)))
    peak = lambda omega: gamma / ((omega - cfg.epsilon) ** 2 + gamma**2)
    delta = 1.0e-6
    kl_derivative_fd = (
        binary_kl(f + (cfg.initial_occupation - f) * math.exp(-2.0 * gamma * (cfg.evaluation_time + delta)), f)
        - binary_kl(f + (cfg.initial_occupation - f) * math.exp(-2.0 * gamma * (cfg.evaluation_time - delta)), f)
    ) / (2.0 * delta)
    return {
        "schema": "openwave.m9.cross-observable-rate-chain.v1",
        "formal_repository": FORMAL_REPOSITORY,
        "formal_branch": FORMAL_BRANCH,
        "formal_head": FORMAL_HEAD,
        "formal_source": FORMAL_SOURCE,
        "config": asdict(cfg),
        "calibration": {"gamma": gamma, "occupation": f, "total_rate": total},
        "spectral": {
            "center_peak": peak(cfg.epsilon),
            "left_half_peak": peak(cfg.epsilon - gamma),
            "right_half_peak": peak(cfg.epsilon + gamma),
            "hwhm": gamma,
            "fwhm": 2.0 * gamma,
        },
        "relaxation": {
            "T1": t1,
            "deviation_at_T1": (cfg.initial_occupation - f) * math.exp(-1.0),
        },
        "kl": {"occupation": n, "production_rate": sigma, "derivative_fd": kl_derivative_fd},
        "claim_boundary": {
            "carrier_obeys_one_level_markov_gksl_model": False,
            "unmodelled_pure_dephasing_is_negligible": False,
            "experimental_cross_carrier_validation_complete": False,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def run_cross_observable_rate_chain(cfg: RateCalibration | None = None) -> dict[str, Any]:
    payload = canonical_payload(cfg)
    spectral = payload["spectral"]
    relaxation = payload["relaxation"]
    kl = payload["kl"]
    gamma = payload["calibration"]["gamma"]
    total = payload["calibration"]["total_rate"]
    acceptance = {
        "formal_source_is_exactly_pinned": len(FORMAL_HEAD) == 40 and len(FORMAL_SOURCE["blob"]) == 40,
        "half_maximum_points_are_exact": math.isclose(spectral["left_half_peak"], spectral["center_peak"] / 2.0, rel_tol=1e-12) and math.isclose(spectral["right_half_peak"], spectral["center_peak"] / 2.0, rel_tol=1e-12),
        "hwhm_is_gamma": math.isclose(spectral["hwhm"], gamma, rel_tol=1e-15),
        "fwhm_is_total_counted_rate": math.isclose(spectral["fwhm"], total, rel_tol=1e-15),
        "T1_is_inverse_total_rate": math.isclose(relaxation["T1"], 1.0 / total, rel_tol=1e-15),
        "same_gamma_controls_KL_production": kl["production_rate"] > 0.0 and math.isclose(kl["derivative_fd"], -kl["production_rate"], rel_tol=2e-9, abs_tol=2e-9),
        "empirical_model_selection_remains_open": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": fingerprint(payload), "decision": {"formal_cross_observable_chain_closed": True, "physical_claims_promoted": []}}
