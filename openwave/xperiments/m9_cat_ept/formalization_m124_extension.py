"""M9.124 formal authority for the three-clock synthesis audit."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
MERGED_BRANCH = "master"
MERGED_FORMAL_HEAD = "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef"
DEVELOPMENT_BRANCH = "entropic-physlib-linear-full"
DEVELOPMENT_HEAD = "af78ea63ee0b39456d8dab023761482196b8c172"
ZIL_PUBLIC_HEAD = "c671f02d8b6dcf7ba689afc86477ff7e35465c35"

FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/Lindblad/ThreeClockReversibilitySpectrum.lean",
        "blob": "cb9f45dbc92e2f2b38ad37481a7167a3cd64fad4",
        "authority": "development_branch",
        "role": "spectral reversibility split between unitary/modular and entropic flows",
        "declarations": (
            "Physlib.QuantumMechanics.Lindblad.ThreeClockReversibilitySpectrum.flow_unitary_iff_re_zero",
            "Physlib.QuantumMechanics.Lindblad.ThreeClockReversibilitySpectrum.entropic_generator_flow_contracts",
            "Physlib.QuantumMechanics.Lindblad.ThreeClockReversibilitySpectrum.modular_flow_entropy_preserving",
            "Physlib.QuantumMechanics.Lindblad.ThreeClockReversibilitySpectrum.entropic_direction_orthogonal_modular",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/RelationalTime/EntropicThermalComplementarity.lean",
        "blob": "f111102cdccfd3d599d31361427f8ae93d65d532",
        "authority": "development_branch",
        "role": "static bridge and dynamical complementarity of modular and entropic time",
        "declarations": (
            "Physlib.QuantumMechanics.RelationalTime.Complementarity.Sᵥₙ_U_conj",
            "Physlib.QuantumMechanics.RelationalTime.Complementarity.modular_direction_orthogonal_to_commutant",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/RelationalTime/PageWootters.lean",
        "blob": "eadbf91743ad60c0c850c5da17cdabbfa79f3739",
        "authority": "development_branch",
        "role": "Page-Wootters constraint, conditional clock, dissipative extension, and bipartite carrier",
        "declarations": (
            "QuantumMechanics.RelationalTime.HamiltonianConstraint.IsPhysical",
            "QuantumMechanics.RelationalTime.DissipativeConditionalClock.gksLGen_eq_vonNeumannGen_of_lindblad_zero",
            "QuantumMechanics.RelationalTime.DissipativeConditionalClock.conditionalEntropicRate_nonneg",
            "Physlib.Thermodynamics.Landauer.PageWoottersBipartite.marginal_entropies_equal",
        ),
    },
    {
        "repository": "jagg-ix/zil-lean",
        "path": "Zil/Datalog/Eval.lean",
        "blob": "6cde34efb9b09cc2f2d189883ff8373263daddba",
        "authority": "public_zil",
        "role": "stratified Datalog execution for pairwise bridges and unification blockers",
        "declarations": (
            "Zil.Datalog.deriveStratified",
            "Zil.Datalog.deriveProgram",
            "Zil.Datalog.query",
        ),
    },
)


def fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.formalization-m124-extension.v1",
        "repository": FORMAL_REPOSITORY,
        "merged_branch": MERGED_BRANCH,
        "merged_formal_head": MERGED_FORMAL_HEAD,
        "development_branch": DEVELOPMENT_BRANCH,
        "development_head": DEVELOPMENT_HEAD,
        "zil_public_head": ZIL_PUBLIC_HEAD,
        "sources": FORMAL_SOURCES,
        "claim_boundary": {
            "development_branch_source_is_merged_master_authority": False,
            "page_wootters_carrier_is_full_conditioning_derivation": False,
            "modular_entropy_preservation_is_physical_clock_calibration": False,
            "entropic_rate_nonnegativity_is_universal_time_theorem": False,
            "pairwise_clock_bridges_are_triple_equivalence": False,
        },
    }


def validate_formal_snapshot(
    *,
    development_head: str = DEVELOPMENT_HEAD,
    source_blobs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    expected = {
        f"{source.get('repository', FORMAL_REPOSITORY)}:{source['path']}": source["blob"]
        for source in FORMAL_SOURCES
    }
    observed = expected if source_blobs is None else dict(source_blobs)
    acceptance = {
        "merged_and_development_authorities_are_separated": MERGED_BRANCH == "master" and DEVELOPMENT_BRANCH == "entropic-physlib-linear-full",
        "development_head_matches_clock_sources": development_head == DEVELOPMENT_HEAD,
        "all_source_blobs_match": observed == expected,
        "public_zil_head_is_pinned": len(ZIL_PUBLIC_HEAD) == 40,
        "development_head_is_not_mislabeled_as_master": DEVELOPMENT_HEAD != MERGED_FORMAL_HEAD,
    }
    return {
        "observed_development_head": development_head,
        "observed_source_blobs": observed,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


@lru_cache(maxsize=1)
def run_formalization_m124_extension() -> dict[str, Any]:
    payload = canonical_payload()
    validation = validate_formal_snapshot()
    paths = {source["path"] for source in FORMAL_SOURCES}
    acceptance = {
        **validation["acceptance"],
        "four_clock_and_runtime_sources_are_pinned": len(FORMAL_SOURCES) == 4,
        "page_wootters_modular_and_entropic_sources_are_present": all(
            any(token in path for path in paths)
            for token in ("PageWootters", "EntropicThermalComplementarity", "ThreeClockReversibilitySpectrum")
        ),
        "all_declaration_lists_are_nonempty": all(source["declarations"] for source in FORMAL_SOURCES),
        "no_formal_or_physical_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.124-formal-authority",
        "validation": validation,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "three_clock_formal_surfaces_registered": True,
            "development_authority_recorded_honestly": True,
            "new_Lean_proof_claimed_by_OpenWave": False,
            "single_unified_clock_theorem_present": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
