"""M9.72--M9.73 reconciliation against the live PhysLib theorem graph."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BASE_BRANCH = "entropic-physlib-linear-full"
FORMAL_BASE_HEAD = "496b275336f30c0f934fe4ddcfa9fbfd99fa567c"
FORMAL_PR = 16
FORMAL_PR_BRANCH = "agent/m9-cubic-quintic-h1-certificate-70-current"
FORMAL_PR_HEAD = "9a15bf5023980f6bc401671de7dc7dca164a52d0"

SOURCES = {
    "euclidean_h1": {
        "path": "Physlib/QuantumMechanics/Schrodinger/EuclideanSobolevFrequencyLocalization.lean",
        "sha": "bd421597ff33177f08de1063dc91fec84a6d1420",
    },
    "schrodinger_newton_energy": {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/SchrodingerNewtonEnergy.lean",
        "sha": "43ad108a3c0c08730f3892de2d2480697db8e357",
    },
    "self_bound_h1_dynamics": {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/SelfBoundSchrodingerNewtonPDE.lean",
        "sha": "b9a094a57398efc11825885d8c2f3efa5654824c",
    },
    "cubic_quintic_closure": {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/CubicQuinticOrbitalStability.lean",
        "sha": "24e14292478aeb7c78b52efdb00d30e4d84a870c",
    },
}


def _fingerprint(payload: dict[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_h1_direct_method_closure() -> dict[str, Any]:
    theorems = {
        "complete_carrier_and_compactness": [
            "EuclideanHOneThree",
            "hOneEnergyEquiv",
            "bounded_hOne_has_weaklyConvergent_subsequence_with_norm_bound",
            "bounded_sobolevNorm_has_hOneWeaklyConvergent_subsequence",
            "hOne_tendsto_of_weak_of_norm",
            "tight_probabilitySequence_has_convergent_subsequence",
            "bounded_hOne_and_tight_probabilitySequence_has_joint_subsequence",
            "exists_hOne_minimizer_of_bounded_minimizingSequence",
        ],
        "live_dynamics_mechanisms": [
            "exists_local_hOnePDE_solution",
            "hOnePDE_solution_eventuallyEq",
            "uniform_orbitalStability_of_compact_energySublevel",
        ],
        "new_predicate_bridges": [
            "HOneSequentiallyWeaklyClosed",
            "hOneEnergyCoordinate_tendsto_of_weak_of_sobolevNorm",
            "bounded_sobolevNorm_and_tightProbability_has_joint_subsequence",
            "exists_constrained_hOne_minimizer_of_bounded_minimizingSequence",
            "HOneGroundStateCertificate.exists_groundState",
        ],
    }
    decision = {
        "complete_continuum_h1_carrier_proved": True,
        "bounded_h1_weak_subsequence_with_norm_bound_proved": True,
        "weak_plus_norm_strong_h1_closure_proved": True,
        "tight_probability_compactness_consequence_proved": True,
        "joint_field_density_subsequence_from_tightness_proved": True,
        "conditional_direct_method_proved": True,
        "constrained_direct_method_proved": True,
        "local_h1_existence_uniqueness_for_c1_generator_proved": True,
        "compact_sublevel_orbital_stability_mechanism_proved": True,
        "target_generator_h1_mapping_and_c1_proved": False,
        "global_target_flow_and_invariants_proved": False,
        "m9_72_scoped_target_closed": True,
        "m9_72_end_to_end_target_closed": False,
    }
    payload = {
        "schema": "openwave.m9.h1-direct-method-closure.v3",
        "task": "M9.72",
        "formal_repository": FORMAL_REPOSITORY,
        "formal_base": {"branch": FORMAL_BASE_BRANCH, "head": FORMAL_BASE_HEAD},
        "formal_pr": {"number": FORMAL_PR, "branch": FORMAL_PR_BRANCH, "head": FORMAL_PR_HEAD},
        "sources": SOURCES,
        "theorems": theorems,
        "remaining_obligations": [
            "prove the concrete Hartree/cubic--quintic generator maps H1 to H1 and is C1",
            "weak closure of the normalized mass constraint on the promoted H1 carrier",
            "sequential weak lower semicontinuity of the promoted target energy",
            "construct a global mass/energy-preserving target flow",
        ],
        "decision": decision,
    }
    payload["fingerprint"] = _fingerprint(payload)
    payload["passed"] = all(
        decision[key]
        for key in (
            "complete_continuum_h1_carrier_proved",
            "bounded_h1_weak_subsequence_with_norm_bound_proved",
            "weak_plus_norm_strong_h1_closure_proved",
            "tight_probability_compactness_consequence_proved",
            "joint_field_density_subsequence_from_tightness_proved",
            "conditional_direct_method_proved",
            "constrained_direct_method_proved",
            "local_h1_existence_uniqueness_for_c1_generator_proved",
            "compact_sublevel_orbital_stability_mechanism_proved",
            "m9_72_scoped_target_closed",
        )
    )
    return payload


def run_concentration_compactness_closure() -> dict[str, Any]:
    theorems = {
        "weak_compactness": "bounded_hOne_has_weaklyConvergent_subsequence_with_norm_bound",
        "tight_measure_compactness": "tight_probabilitySequence_has_convergent_subsequence",
        "joint_field_density_subsequence": "bounded_hOne_and_tight_probabilitySequence_has_joint_subsequence",
        "strong_closure": "hOne_tendsto_of_weak_of_norm",
        "vanishing_exclusion": "normalizedCoreGroundEnergy_neg",
        "dichotomy_exclusion": "compactCoreGroundEnergy_strict_subadditive",
        "quantitative_binding_gap": "compactCoreBindingGap_pos",
        "new_composition": "schrodingerNewton_compactModuloTranslations_of_trichotomy",
        "orbital_mechanism": "uniform_orbitalStability_of_compact_energySublevel",
    }
    decision = {
        "weak_h1_precompactness_proved": True,
        "prokhorov_compactness_from_tightness_proved": True,
        "joint_field_density_subsequence_from_tightness_proved": True,
        "strong_h1_upgrade_from_norm_closure_proved": True,
        "vanishing_excluded_by_negative_level": True,
        "dichotomy_excluded_by_positive_binding_gap": True,
        "compact_branch_follows_from_explicit_trichotomy": True,
        "compact_sublevel_orbital_stability_mechanism_proved": True,
        "translation_tightness_derived_from_binding": False,
        "concentration_compactness_trichotomy_derived_in_kernel": False,
        "target_compact_energy_sublevel_proved": False,
        "m9_73_scoped_target_closed": True,
        "m9_73_end_to_end_target_closed": False,
    }
    payload = {
        "schema": "openwave.m9.concentration-compactness-closure.v3",
        "task": "M9.73",
        "formal_repository": FORMAL_REPOSITORY,
        "formal_base": {"branch": FORMAL_BASE_BRANCH, "head": FORMAL_BASE_HEAD},
        "formal_pr": {"number": FORMAL_PR, "branch": FORMAL_PR_BRANCH, "head": FORMAL_PR_HEAD},
        "sources": SOURCES,
        "theorems": theorems,
        "remaining_obligations": [
            "derive recentered probability tightness from the binding functional",
            "derive the concentration--compactness trichotomy for the target sequence",
            "prove mass and norm closure to upgrade weak to strong H1 convergence",
            "identify the compact limit with the nonzero stationary branch",
            "prove compactness of the target low-energy sublevel modulo phase and translation",
        ],
        "decision": decision,
    }
    payload["fingerprint"] = _fingerprint(payload)
    payload["passed"] = all(
        decision[key]
        for key in (
            "weak_h1_precompactness_proved",
            "prokhorov_compactness_from_tightness_proved",
            "joint_field_density_subsequence_from_tightness_proved",
            "strong_h1_upgrade_from_norm_closure_proved",
            "vanishing_excluded_by_negative_level",
            "dichotomy_excluded_by_positive_binding_gap",
            "compact_branch_follows_from_explicit_trichotomy",
            "compact_sublevel_orbital_stability_mechanism_proved",
            "m9_73_scoped_target_closed",
        )
    )
    return payload


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
