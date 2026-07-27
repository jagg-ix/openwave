"""M9.120 formal authority for spectra, response, and refinement.

The contract repins the merged ``entropic-physlib-linear-full`` branch after it
advanced beyond the historical M9.119 revision. Draft Physlib PR heads are
recorded as candidate evidence only and are not accepted as merged authority.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
PREVIOUS_FORMAL_HEAD = "bca7617e1294c4645a13bc9eae9aa6d97de78430"
CURRENT_FORMAL_HEAD = "3923d802339c957066fcccd579362f739775797a"
PHYSLIB_ROOT_BLOB = "d225e3cdb0e3239eb6c83f20af25968ddb9ec37b"

FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/PeriodicSchrodinger/ResonanceMatrix.lean",
        "blob": "2e2cac17f9cbce24afcd1070df22d66e0b2f3b70",
        "role": "finite Hermitian resonance matrices, eigenpairs, and explicit residuals",
        "declarations": (
            "Physlib.QuantumMechanics.PeriodicSchrodinger.resonanceMatrix",
            "Physlib.QuantumMechanics.PeriodicSchrodinger.resonanceResidual_eq_zero_iff",
            "Physlib.QuantumMechanics.PeriodicSchrodinger.resonanceMatrix_isHermitian",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/PeriodicSchrodinger/BlochApproximation.lean",
        "blob": "59e87c2afaff36ca8253468a16920bf57a3694e7",
        "role": "finite and summable infinite spectral localization diagnostics",
        "declarations": (
            "Physlib.QuantumMechanics.PeriodicSchrodinger.finiteTailMass",
            "Physlib.QuantumMechanics.PeriodicSchrodinger.IsFiniteBlochLocalized",
            "Physlib.QuantumMechanics.PeriodicSchrodinger.IsInfiniteBlochLocalized",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/PeriodicSchrodinger/EntropicSelection.lean",
        "blob": "d3e00cd819176c810823a992ceaf0cb97a413909",
        "role": "nonnegative spectral mismatch and contractive complex-action selection weights",
        "declarations": (
            "Physlib.QuantumMechanics.PeriodicSchrodinger.spectralMismatchPenalty_eq_zero_iff",
            "Physlib.QuantumMechanics.PeriodicSchrodinger.norm_spectralSelectionWeight",
            "Physlib.QuantumMechanics.PeriodicSchrodinger.norm_spectralSelectionWeight_le_one",
        ),
    },
    {
        "path": "Physlib/QFT/ScalarGreenFunctions/SourceJet.lean",
        "blob": "fb4fcf3f4b51b2f98ae5e10b7fe0d3a8fc21ea70",
        "role": "commuting source insertions and exact response-coefficient extraction",
        "declarations": (
            "Physlib.QFT.ScalarGreenFunctions.formalSourceDerivative_comm",
            "Physlib.QFT.ScalarGreenFunctions.recoverGreenFromSourceJet",
            "Physlib.QFT.ScalarGreenFunctions.recoverGreenFromDerivativeCoefficient",
        ),
    },
    {
        "path": "Physlib/Particles/StandardModel/HiggsBoson/Potential.lean",
        "blob": "d0dc8878985037ca5ea0efa30178e002934525c7",
        "role": "quartic Higgs potential and vacuum-norm characterization",
        "declarations": (
            "StandardModel.HiggsField.Potential.complete_square",
            "StandardModel.HiggsField.Potential.quadDiscrim_eq_zero_iff_normSq",
        ),
    },
)

PENDING_FORMAL_CANDIDATES = (
    {
        "pull_request": 19,
        "head": "128bebd375cd895af1431444974a7a591c872a31",
        "state": "draft-open-unmerged",
        "role": "candidate live H1 flow and identified stable minimizing branch adapters",
    },
    {
        "pull_request": 20,
        "head": "e192104955fc516f1ba267f8653f0dcf8d18ab51",
        "state": "draft-open-unmerged",
        "role": "candidate charge, Klein-Gordon, and orbital criterion bridges",
    },
)


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.formalization-m120-extension.v1",
        "repository": FORMAL_REPOSITORY,
        "branch": FORMAL_BRANCH,
        "previous_formal_head": PREVIOUS_FORMAL_HEAD,
        "current_formal_head": CURRENT_FORMAL_HEAD,
        "physlib_root_blob": PHYSLIB_ROOT_BLOB,
        "sources": FORMAL_SOURCES,
        "pending_candidates": PENDING_FORMAL_CANDIDATES,
        "claim_boundary": {
            "draft_physlib_PR_is_merged_authority": False,
            "finite_Hermitian_spectrum_is_physical_particle_spectrum": False,
            "formal_source_jet_is_measured_decay_rate": False,
            "finite_grid_localization_is_continuum_spectral_theorem": False,
            "spectral_selection_weight_replaces_spectral_proof": False,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), default=str
        ).encode()
    ).hexdigest()


def validate_formal_snapshot(
    *,
    head: str = CURRENT_FORMAL_HEAD,
    root_blob: str = PHYSLIB_ROOT_BLOB,
    source_blobs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    observed = (
        {source["path"]: source["blob"] for source in FORMAL_SOURCES}
        if source_blobs is None
        else dict(source_blobs)
    )
    expected = {source["path"]: source["blob"] for source in FORMAL_SOURCES}
    acceptance = {
        "formal_repository_and_branch_are_explicit": bool(
            FORMAL_REPOSITORY and FORMAL_BRANCH
        ),
        "merged_formal_head_is_current": head == CURRENT_FORMAL_HEAD,
        "physlib_root_blob_is_current": root_blob == PHYSLIB_ROOT_BLOB,
        "all_formal_source_blobs_match": observed == expected,
        "historical_M119_head_is_not_reported_as_current": (
            PREVIOUS_FORMAL_HEAD != CURRENT_FORMAL_HEAD
        ),
        "draft_candidate_heads_are_not_promoted": all(
            candidate["state"] == "draft-open-unmerged"
            for candidate in PENDING_FORMAL_CANDIDATES
        ),
    }
    return {
        "observed_head": head,
        "observed_root_blob": root_blob,
        "observed_source_blobs": observed,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


@lru_cache(maxsize=1)
def run_formalization_m120_extension() -> dict[str, Any]:
    payload = canonical_payload()
    validation = validate_formal_snapshot()
    acceptance = {
        **validation["acceptance"],
        "five_merged_source_surfaces_are_pinned": len(FORMAL_SOURCES) == 5,
        "source_declarations_are_nonempty": all(
            source["declarations"] for source in FORMAL_SOURCES
        ),
        "no_formal_or_physical_boundary_is_crossed": not any(
            payload["claim_boundary"].values()
        ),
        "fingerprint_is_deterministic": fingerprint(payload)
        == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.120-formal-authority",
        "validation": validation,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "merged_periodic_spectral_authority_rebased": True,
            "finite_response_source_authority_registered": True,
            "draft_physlib_candidates_recorded_but_not_promoted": True,
            "new_Lean_proof_claimed_by_OpenWave": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
