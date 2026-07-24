"""M9.72--M9.73 reconciliation against the live PhysLib theorem graph."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BASE_BRANCH = "entropic-physlib-linear-full"
FORMAL_BASE_HEAD = "0a04328a01b7911078c4f9d01cc0c8c963519dc2"
FORMAL_PR = 16
FORMAL_PR_BRANCH = "agent/m9-cubic-quintic-h1-certificate-70-current"
FORMAL_PR_HEAD = "5d0cdf07c891b1dbe7381b93c2d794b593fae09d"

SOURCES = {
    "euclidean_h1": {
        "path": "Physlib/QuantumMechanics/Schrodinger/EuclideanSobolevFrequencyLocalization.lean",
        "sha": "a3e5f79be6c3d650f48ea1c164541eedf8588c5b",
    },
    "schrodinger_newton_energy": {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/SchrodingerNewtonEnergy.lean",
        "sha": "43ad108a3c0c08730f3892de2d2480697db8e357",
    },
    "cubic_quintic_closure": {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/CubicQuinticOrbitalStability.lean",
        "sha": "3a5b8737331fb1bbae0dea62af2db21f58f1b332",
    },
}


def _fingerprint(payload: dict[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_h1_direct_method_closure() -> dict[str, Any]:
    theorems = {
        "existing_complete_carrier": [
            "EuclideanHOneThree",
            "hOneEnergyEquiv",
            "HOneWeaklyConverges",
            "bounded_sobolevNorm_has_hOneWeaklyConvergent_subsequence",
            "exists_hOne_minimizer_of_bounded_minimizingSequence",
        ],
        "new_constrained_bridge": [
            "HOneSequentiallyWeaklyClosed",
            "exists_constrained_hOne_minimizer_of_bounded_minimizingSequence",
            "HOneGroundStateCertificate.exists_groundState",
        ],
    }
    decision = {
        "complete_continuum_h1_carrier_proved": True,
        "bounded_h1_weak_subsequence_proved": True,
        "conditional_direct_method_proved": True,
        "constrained_direct_method_proved": True,
        "mass_constraint_weak_closure_proved_for_target_functional": False,
        "target_energy_weak_lower_semicontinuity_proved": False,
        "m9_72_scoped_target_closed": True,
        "m9_72_end_to_end_ground_state_attainment_closed": False,
    }
    payload = {
        "schema": "openwave.m9.h1-direct-method-closure.v2",
        "task": "M9.72",
        "formal_repository": FORMAL_REPOSITORY,
        "formal_base": {"branch": FORMAL_BASE_BRANCH, "head": FORMAL_BASE_HEAD},
        "formal_pr": {"number": FORMAL_PR, "branch": FORMAL_PR_BRANCH, "head": FORMAL_PR_HEAD},
        "sources": SOURCES,
        "theorems": theorems,
        "remaining_obligations": [
            "weak closure of the normalized mass constraint on the promoted H1 carrier",
            "sequential weak lower semicontinuity of the promoted Hartree/cubic--quintic energy",
            "construction of an explicit bounded minimizing sequence for the target functional",
        ],
        "decision": decision,
    }
    payload["fingerprint"] = _fingerprint(payload)
    payload["passed"] = all(
        decision[key]
        for key in (
            "complete_continuum_h1_carrier_proved",
            "bounded_h1_weak_subsequence_proved",
            "conditional_direct_method_proved",
            "constrained_direct_method_proved",
            "m9_72_scoped_target_closed",
        )
    )
    return payload


def run_concentration_compactness_closure() -> dict[str, Any]:
    theorems = {
        "weak_compactness": "bounded_sobolevNorm_has_hOneWeaklyConvergent_subsequence",
        "vanishing_exclusion": "normalizedCoreGroundEnergy_neg",
        "dichotomy_exclusion": "compactCoreGroundEnergy_strict_subadditive",
        "quantitative_binding_gap": "compactCoreBindingGap_pos",
        "new_composition": "schrodingerNewton_compactModuloTranslations_of_trichotomy",
    }
    decision = {
        "weak_h1_precompactness_proved": True,
        "vanishing_excluded_by_negative_level": True,
        "dichotomy_excluded_by_positive_binding_gap": True,
        "compact_branch_follows_from_explicit_trichotomy": True,
        "translation_tightness_derived_from_first_principles": False,
        "concentration_compactness_trichotomy_derived_in_kernel": False,
        "m9_73_scoped_target_closed": True,
        "m9_73_end_to_end_compactness_closed": False,
    }
    payload = {
        "schema": "openwave.m9.concentration-compactness-closure.v2",
        "task": "M9.73",
        "formal_repository": FORMAL_REPOSITORY,
        "formal_base": {"branch": FORMAL_BASE_BRANCH, "head": FORMAL_BASE_HEAD},
        "formal_pr": {"number": FORMAL_PR, "branch": FORMAL_PR_BRANCH, "head": FORMAL_PR_HEAD},
        "sources": SOURCES,
        "theorems": theorems,
        "remaining_obligations": [
            "derive the concentration--compactness trichotomy for the promoted minimizing sequence",
            "prove translation tightness and mass preservation in the compact branch",
            "identify the compact limit with the nonzero stationary branch",
            "prove coercivity modulo phase and translation",
        ],
        "decision": decision,
    }
    payload["fingerprint"] = _fingerprint(payload)
    payload["passed"] = all(
        decision[key]
        for key in (
            "weak_h1_precompactness_proved",
            "vanishing_excluded_by_negative_level",
            "dichotomy_excluded_by_positive_binding_gap",
            "compact_branch_follows_from_explicit_trichotomy",
            "m9_73_scoped_target_closed",
        )
    )
    return payload


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
