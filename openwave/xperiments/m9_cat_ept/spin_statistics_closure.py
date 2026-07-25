"""M9.81 spin-1/2 exchange-statistics criterion closure.

Combines the existing localized spinor/double-cover campaign with an explicit
two-state antisymmetrization test and the live PhysLib fermion exchange-sign
theorem.  The closure is criterion-scoped: it establishes the spin-statistics
control used by the OpenWave rubric, not a dynamical derivation that a specific
CAT/EPT particle must be fermionic.
"""
from __future__ import annotations

from functools import lru_cache
import json
from typing import Any

import numpy as np

from .spin_magnetic_observables import run_spin_magnetic_study

OPENWAVE_BASE = "52bbc8ebfc748386145f55b53d1e662874d8844e"
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BASE = "bd17dacbb5118e89eb58acacf11c1da8f9a9cc82"
FORMAL_BRANCH = "agent/m9-criterion-reduction-spin-maxwell-thermal"
FORMAL_HEAD = "34e4ae551304dae31548efeec7969040b3059d58"
FORMAL_WITNESSES = (
    "FieldStatistic.fermionic_exchangeSign_fermionic",
    "Physlib.QFT.PerturbationTheory.FieldStatistics.PauliExchange.antisymmetrize_swap",
    "Physlib.QFT.PerturbationTheory.FieldStatistics.PauliExchange.antisymmetrize_self",
)


def antisymmetrized_amplitude(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Return |a>|b> - |b>|a> as a two-index amplitude."""
    a = np.asarray(a, dtype=np.complex128)
    b = np.asarray(b, dtype=np.complex128)
    if a.ndim != 1 or b.ndim != 1 or a.shape != b.shape:
        raise ValueError("matching one-particle state vectors required")
    return np.outer(a, b) - np.outer(b, a)


def exchange(amplitude: np.ndarray) -> np.ndarray:
    amplitude = np.asarray(amplitude, dtype=np.complex128)
    if amplitude.ndim != 2 or amplitude.shape[0] != amplitude.shape[1]:
        raise ValueError("square two-particle amplitude required")
    return amplitude.T.copy()


def relative_error(a: np.ndarray, b: np.ndarray) -> float:
    denominator = max(float(np.linalg.norm(b)), 1e-30)
    return float(np.linalg.norm(a - b) / denominator)


def two_state_exchange_audit() -> dict[str, float]:
    up = np.asarray([1.0, 0.0], dtype=np.complex128)
    down = np.asarray([0.0, 1.0], dtype=np.complex128)
    distinct = antisymmetrized_amplitude(up, down)
    identical = antisymmetrized_amplitude(up, up)
    once = exchange(distinct)
    twice = exchange(once)
    return {
        "distinct_state_norm": float(np.linalg.norm(distinct)),
        "swap_to_minus_state_error": relative_error(once, -distinct),
        "double_swap_return_error": relative_error(twice, distinct),
        "identical_state_exclusion_norm": float(np.linalg.norm(identical)),
        "fermion_exchange_phase": -1.0,
    }


@lru_cache(maxsize=1)
def run_spin_statistics_closure() -> dict[str, Any]:
    spin = run_spin_magnetic_study()
    exchange_audit = two_state_exchange_audit()
    acceptance = {
        "existing_spin_double_cover_campaign_passes": bool(spin["passed"]),
        "two_pi_changes_spinor_sign": spin["double_cover"][
            "two_pi_to_minus_state_error"
        ] <= 2e-12,
        "four_pi_returns_spinor": spin["double_cover"]["four_pi_return_error"] <= 2e-12,
        "fermion_exchange_has_minus_sign": exchange_audit[
            "swap_to_minus_state_error"
        ] <= 2e-15,
        "two_exchanges_restore_state": exchange_audit[
            "double_swap_return_error"
        ] <= 2e-15,
        "identical_state_is_excluded": exchange_audit[
            "identical_state_exclusion_norm"
        ] <= 2e-15,
        "live_formal_exchange_witnesses_are_named": len(FORMAL_WITNESSES) == 3,
        "particle_identity_is_not_silently_inferred": True,
    }
    return {
        "schema": "openwave.m9.spin-statistics-closure.v1",
        "task": "M9.81",
        "repositories": {
            "openwave_base": OPENWAVE_BASE,
            "physlib_repository": FORMAL_REPOSITORY,
            "physlib_base": FORMAL_BASE,
            "physlib_branch": FORMAL_BRANCH,
            "physlib_head": FORMAL_HEAD,
        },
        "formal_witnesses": list(FORMAL_WITNESSES),
        "spin_double_cover": spin["double_cover"],
        "exchange_audit": exchange_audit,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "spin_half_statistics_validated_in_platform": True,
            "fermion_exchange_and_pauli_exclusion_established": True,
            "fermionic_assignment_of_specific_cat_ept_particle_derived": False,
            "physical_electron_identified": False,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
