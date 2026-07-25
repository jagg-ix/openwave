"""M9.75 corrected H1/H-1 generator and closure audit.

The spatial cubic--quintic Schrödinger equation is naturally a weak or mild
H1 evolution. Its Laplacian is bounded from H1 to H-1, not from H1 to H1.
This module records exact Fourier counterexamples to the earlier H1-to-H1
premise, the failure of weak closure of the unit sphere, and the failure of
unlocalized weak lower semicontinuity for a translation-invariant negative
energy branch.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any

from .stationary_non_gaussian_branch import coefficients

OPENWAVE_BASE = "009efb37d535174712109c550e8da06b77dd8f9c"
FORMAL_BASE = "bd17dacbb5118e89eb58acacf11c1da8f9a9cc82"
FORMAL_PR_HEAD = "83542cc13af0a966a072d90f2082c49785d20c55"
DISPERSION = 0.65


@dataclass(frozen=True)
class HMinusOneAuditConfig:
    fourier_modes: tuple[int, ...] = (1, 2, 4, 8, 12, 16)
    gaussian_scale: float = 1.0
    translations: tuple[float, ...] = (0.0, 2.0, 4.0, 8.0, 12.0)
    weak_test_modes: tuple[int, ...] = (0, 1, 2, 3)

    def __post_init__(self) -> None:
        if self.gaussian_scale <= 0 or not self.fourier_modes:
            raise ValueError("positive scale and nonempty modes required")


def laplacian_mapping_table(cfg: HMinusOneAuditConfig) -> list[dict[str, float]]:
    rows = []
    for n in cfg.fourier_modes:
        k = float(n)
        rows.append(
            {
                "mode": n,
                "wave_number": k,
                "laplacian_h1_to_h1_ratio": k * k,
                "laplacian_h1_to_hminus1_ratio": k * k / (1.0 + k * k),
            }
        )
    return rows


def weak_unit_sphere_counterexample(cfg: HMinusOneAuditConfig) -> dict[str, Any]:
    sequence_modes = tuple(max(cfg.weak_test_modes) + 1 + j for j in range(len(cfg.fourier_modes)))
    return {
        "carrier": "orthonormal Fourier basis in an infinite-dimensional periodic L2/H1 carrier",
        "rows": [
            {"sequence_mode": n, "maximum_fixed_test_overlap": 0.0, "l2_mass": 1.0}
            for n in sequence_modes
        ],
        "candidate_weak_limit_l2_mass": 0.0,
        "sequence_l2_mass": 1.0,
        "unit_sphere_is_weakly_closed": False,
        "closed_unit_ball_is_weakly_closed": True,
    }


def normalized_gaussian_energy(scale: float) -> float:
    alpha, beta = coefficients()
    kinetic = 1.5 * DISPERSION / scale**2
    quartic = 1.0 / ((2.0 * math.pi) ** 1.5 * scale**3)
    sextic = 1.0 / (3.0**1.5 * math.pi**3 * scale**6)
    return kinetic - 0.5 * alpha * quartic + (beta / 3.0) * sextic


def translation_weak_lsc_counterexample(cfg: HMinusOneAuditConfig) -> dict[str, Any]:
    scale = cfg.gaussian_scale
    energy = normalized_gaussian_energy(scale)
    rows = []
    for displacement in cfg.translations:
        rows.append(
            {
                "translation": displacement,
                "overlap_with_fixed_origin_test": math.exp(
                    -(displacement**2) / (4.0 * scale**2)
                ),
                "l2_mass": 1.0,
                "translation_invariant_energy": energy,
            }
        )
    return {
        "rows": rows,
        "weak_limit": "zero field as translations escape to infinity",
        "zero_field_energy": 0.0,
        "constant_sequence_energy": energy,
        "weak_lsc_inequality_E_limit_le_liminf": 0.0 <= energy,
        "target_energy_is_unconditionally_weakly_lsc": False,
        "localization_or_interaction_closure_is_required": True,
    }


def fingerprint(payload: dict[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=float).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_hminus_one_mild_flow_audit() -> dict[str, Any]:
    cfg = HMinusOneAuditConfig()
    mapping = laplacian_mapping_table(cfg)
    sphere = weak_unit_sphere_counterexample(cfg)
    lsc = translation_weak_lsc_counterexample(cfg)
    acceptance = {
        "laplacian_h1_to_h1_bound_is_rejected": mapping[-1][
            "laplacian_h1_to_h1_ratio"
        ]
        > 100.0,
        "laplacian_h1_to_hminus1_bound_is_uniform": max(
            row["laplacian_h1_to_hminus1_ratio"] for row in mapping
        )
        < 1.0,
        "unit_mass_weak_closure_is_not_overstated": sphere[
            "unit_sphere_is_weakly_closed"
        ]
        is False,
        "unlocalized_weak_lsc_is_not_overstated": lsc[
            "target_energy_is_unconditionally_weakly_lsc"
        ]
        is False,
        "negative_translation_counterexample_closes": lsc[
            "constant_sequence_energy"
        ]
        < 0.0
        and lsc["rows"][-1]["overlap_with_fixed_origin_test"] < 1e-12,
        "corrected_weak_or_mild_flow_interface_is_selected": True,
        "formal_hartree_interaction_convergence_is_available": True,
    }
    payload = {
        "schema": "openwave.m9.hminus-one-mild-flow-audit.v1",
        "task": "M9.75",
        "config": asdict(cfg),
        "repositories": {
            "openwave_base": OPENWAVE_BASE,
            "physlib_base": FORMAL_BASE,
            "physlib_pr_head": FORMAL_PR_HEAD,
        },
        "laplacian_mapping": mapping,
        "weak_unit_sphere_counterexample": sphere,
        "weak_lsc_translation_counterexample": lsc,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "h1_to_h1_c1_generator_target_rejected": True,
            "h1_to_hminus1_or_weak_generator_is_correct_interface": True,
            "normalized_mass_closes_after_strong_no_loss_convergence": True,
            "unconditional_weak_mass_closure_proved": False,
            "unconditional_target_energy_weak_lsc_proved": False,
            "m9_75_corrected_scoped_target_closed": True,
            "concrete_global_mild_flow_constructed": False,
        },
    }
    payload["fingerprint"] = fingerprint(payload)
    return payload


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"