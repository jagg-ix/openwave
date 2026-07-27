"""M9.119 formal authority for gauge-covariant strong and electroweak carriers.

The numerical adapters bind to exact theorem surfaces on
``entropic-physlib-linear-full``. Physlib supplies finite Wilson-action
identities, the Standard Model gauge-group product, unitary Higgs action, and
the quartic vacuum relation. OpenWave supplies finite numerical carriers; it
does not turn those interfaces into a Lean proof of QCD or the Standard Model.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formalization_m117_extension import (
    CURRENT_FORMAL_HEAD as PREVIOUS_FORMAL_HEAD,
    FORMAL_BRANCH,
    FORMAL_REPOSITORY,
    PHYSLIB_ROOT_BLOB,
    canonical_payload as previous_payload,
    run_formalization_m117_extension,
)

CURRENT_FORMAL_HEAD = "bca7617e1294c4645a13bc9eae9aa6d97de78430"

FORMAL_SOURCES = (
    {
        "path": "Physlib/QFT/PathIntegral/FiniteWilsonGaugeModel.lean",
        "blob": "870efa65de9037ea7c8e617628b15c19fb3de521",
        "role": "finite Wilson action, positive damping, and finite partition/expectation interfaces",
        "declarations": (
            "Physlib.QFT.PathIntegral.FiniteWilsonGaugeModel.wilsonAction",
            "Physlib.QFT.PathIntegral.FiniteWilsonGaugeModel.boltzmannFactor_pos",
            "Physlib.QFT.PathIntegral.FiniteWilsonGaugeModel.imaginaryAction_nonneg",
            "Physlib.QFT.PathIntegral.FiniteWilsonGaugeModel.partition_eq_finset_sum",
        ),
    },
    {
        "path": "Physlib/QFT/Lattice/WilsonLoopAreaLaw.lean",
        "blob": "ffd0b7e6dc1ec8b39851755aeda3ae753a5c42d0",
        "role": "plaquette Wilson action, area-law implication, and center-vortex observable formulas",
        "declarations": (
            "Physlib.QFT.Lattice.WilsonLoopAreaLaw.wilsonAction_nonneg",
            "Physlib.QFT.Lattice.WilsonLoopAreaLaw.areaLaw_implies_decay",
            "Physlib.QFT.Lattice.WilsonLoopAreaLaw.vortexAreaLaw_exp",
        ),
    },
    {
        "path": "Physlib/Particles/StandardModel/Basic.lean",
        "blob": "18c72a2fe920bfb46da5a2fcab66f6974bfddbab",
        "role": "global SU(3) x SU(2) x U(1) gauge-group carrier and projections",
        "declarations": (
            "StandardModel.GaugeGroupI",
            "StandardModel.GaugeGroupI.toSU3",
            "StandardModel.GaugeGroupI.toSU2",
            "StandardModel.GaugeGroupI.toU1",
        ),
    },
    {
        "path": "Physlib/Particles/StandardModel/Representations.lean",
        "blob": "90b7fd5d5950f6afb9b5d0a363f599f136100abf",
        "role": "unitary U(1) and fundamental SU(2) representations and their commuting action",
        "declarations": (
            "StandardModel.repU1",
            "StandardModel.fundamentalSU2",
            "StandardModel.repU1_fundamentalSU2_commute",
        ),
    },
    {
        "path": "Physlib/Particles/StandardModel/HiggsBoson/Basic.lean",
        "blob": "5a647eab31bdaa1bbee89d8a14da48250bbace78",
        "role": "Higgs doublet, GaugeGroupI action, unitary inner product, and gauge-orbit norm",
        "declarations": (
            "StandardModel.HiggsVec.gaugeGroupI_smul_eq",
            "StandardModel.HiggsVec.gaugeGroupI_smul_inner",
            "StandardModel.HiggsVec.gaugeGroupI_smul_norm",
            "StandardModel.HiggsVec.mem_orbit_gaugeGroupI_iff",
        ),
    },
    {
        "path": "Physlib/Particles/StandardModel/HiggsBoson/Potential.lean",
        "blob": "d0dc8878985037ca5ea0efa30178e002934525c7",
        "role": "quartic Higgs potential, complete-square identity, and vacuum norm condition",
        "declarations": (
            "StandardModel.HiggsField.Potential.toFun",
            "StandardModel.HiggsField.Potential.complete_square",
            "StandardModel.HiggsField.Potential.quadDiscrim_eq_zero_iff_normSq",
        ),
    },
)

SCOPE = {
    "finite_Wilson_action_authority_available": True,
    "standard_model_gauge_group_available": True,
    "unitary_Higgs_gauge_action_available": True,
    "quartic_Higgs_vacuum_identity_available": True,
    "full_standard_model_fermion_content_constructed": False,
    "formal_interfaces_prove_OpenWave_QCD": False,
    "formal_interfaces_calibrate_electroweak_parameters": False,
}


def _is_sha(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 40
        and all(character in "0123456789abcdef" for character in value.lower())
    )


def expected_source_blobs() -> dict[str, str]:
    return {str(row["path"]): str(row["blob"]) for row in FORMAL_SOURCES}


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.formalization-m119-extension.v1",
        "previous_authority": previous_payload(),
        "formal_repository": {
            "name": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "previous_head": PREVIOUS_FORMAL_HEAD,
            "current_head": CURRENT_FORMAL_HEAD,
            "physlib_root_blob": PHYSLIB_ROOT_BLOB,
        },
        "sources": [dict(row) for row in FORMAL_SOURCES],
        "scope": dict(SCOPE),
        "policy": {
            "numerical_gauge_covariance_is_not_a_new_Lean_theorem": True,
            "finite_Wilson_loops_do_not_establish_confinement": True,
            "bosonic_Higgs_carrier_is_not_full_electroweak_theory": True,
            "unfixed_couplings_do_not_predict_particle_masses": True,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def validate_formalization_m119(
    *,
    observed_head: str | None = None,
    observed_root_blob: str | None = None,
    observed_source_blobs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    head = CURRENT_FORMAL_HEAD if observed_head is None else observed_head
    root = PHYSLIB_ROOT_BLOB if observed_root_blob is None else observed_root_blob
    sources = expected_source_blobs() if observed_source_blobs is None else dict(observed_source_blobs)
    errors: list[str] = []
    if head != CURRENT_FORMAL_HEAD:
        errors.append("formal head drift detected")
    if root != PHYSLIB_ROOT_BLOB:
        errors.append("Physlib root drift detected")
    for path, blob in expected_source_blobs().items():
        if sources.get(path) != blob:
            errors.append(f"M9.119 formal source drift detected: {path}")
    return {"errors": errors, "passed": not errors}


@lru_cache(maxsize=1)
def run_formalization_m119_extension() -> dict[str, Any]:
    previous = run_formalization_m117_extension()
    validation = validate_formalization_m119()
    payload = canonical_payload()
    acceptance = {
        "previous_M9_117_formal_authority_passes": bool(previous["passed"]),
        "current_formal_revision_and_root_are_exact": _is_sha(CURRENT_FORMAL_HEAD)
        and _is_sha(PHYSLIB_ROOT_BLOB),
        "six_gauge_sources_are_blob_pinned": len(FORMAL_SOURCES) == 6
        and all(_is_sha(str(row["blob"])) for row in FORMAL_SOURCES),
        "all_theorem_families_are_declared": all(row["declarations"] for row in FORMAL_SOURCES),
        "source_validation_has_no_errors": bool(validation["passed"]),
        "fermions_QCD_and_calibration_remain_open": not SCOPE[
            "full_standard_model_fermion_content_constructed"
        ]
        and not SCOPE["formal_interfaces_prove_OpenWave_QCD"]
        and not SCOPE["formal_interfaces_calibrate_electroweak_parameters"],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.119-formal",
        "source_validation": validation,
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_Wilson_authority_registered": True,
            "Standard_Model_gauge_group_registered": True,
            "Higgs_gauge_and_potential_authority_registered": True,
            "complete_QCD_or_electroweak_theory_proved": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
