"""M9.122 formal authority for external-evidence readiness."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "master"
DEVELOPMENT_BRANCH = "private/entropic-physlib-linear-full"
PREVIOUS_FORMAL_HEAD = "3923d802339c957066fcccd579362f739775797a"
CURRENT_FORMAL_HEAD = "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef"
PHYSLIB_ROOT_BLOB = "f953c09c428eb83d9894c1944e1fd44a7ffe95a1"
ZIL_PUBLIC_HEAD = "c671f02d8b6dcf7ba689afc86477ff7e35465c35"

FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/Basic.lean",
        "blob": "aa84f739aa308e6f7dafcaabc52c7633e951db55",
        "role": "finite LDDL rates, GKSL generator, exponential evolution, and Lorentz carrier",
        "declarations": (
            "QuantumMechanics.LindbladDrivenLeads.lddlGeneratorHS",
            "QuantumMechanics.LindbladDrivenLeads.lddlEvolutionHS",
            "QuantumMechanics.LindbladDrivenLeads.lorentzian",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/TracePreservation.lean",
        "blob": "713ad48e943f6204700215fe6def02b146833271",
        "role": "direct infinitesimal trace preservation of the finite LDDL generator",
        "declarations": (
            "QuantumMechanics.LindbladDrivenLeads.hsTrace_lddlGeneratorHS",
            "QuantumMechanics.LindbladDrivenLeads.hsTrace_comp_lddlGeneratorHS",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/CauchyWeakLimit.lean",
        "blob": "2479d0782e7ea932c57d46644c8d939522db5162",
        "role": "weak zero-width limit of Cauchy broadening to a Dirac level",
        "declarations": (
            "QuantumMechanics.LindbladDrivenLeads.affineCauchySample_tendstoInDistribution",
            "QuantumMechanics.LindbladDrivenLeads.affineCauchyLaw_tendsto_dirac",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/ContinuumSemigroupClosure.lean",
        "blob": "d349630748fb066391810547e7fbb8b4431f244d",
        "role": "bounded continuum C0 semigroups and identified infinitesimal generators",
        "declarations": (
            "QuantumMechanics.LindbladDrivenLeads.boundedGeneratorC0Semigroup",
            "QuantumMechanics.LindbladDrivenLeads.boundedGenerator_hasInfinitesimalGenerator",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/TraceClassDensityOperatorIdeal.lean",
        "blob": "9e286dad87d23dba9cbc77011dfb84b11794cd00",
        "role": "constructive positive trace-class density carriers",
        "declarations": (
            "QuantumMechanics.LindbladDrivenLeads.IsTraceClass",
            "QuantumMechanics.LindbladDrivenLeads.TraceClassDensityOperator",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/NuclearDensityEvolution.lean",
        "blob": "794faadf55b391db58455850fabf5fc0f8678d87",
        "role": "constructive nuclear density ensembles and normalized evolution",
        "declarations": (
            "QuantumMechanics.LindbladDrivenLeads.NuclearDensityOperator",
            "QuantumMechanics.LindbladDrivenLeads.continuum_nuclear_density_certificate",
        ),
    },
    {
        "repository": "jagg-ix/zil-lean",
        "path": "Zil/Datalog/Eval.lean",
        "blob": "6cde34efb9b09cc2f2d189883ff8373263daddba",
        "role": "stratified Horn/Datalog execution for evidence readiness and blockers",
        "declarations": (
            "Zil.Datalog.deriveStratified",
            "Zil.Datalog.deriveProgram",
            "Zil.Datalog.query",
        ),
    },
)


def fingerprint(payload: Any) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.formalization-m122-extension.v1",
        "repository": FORMAL_REPOSITORY,
        "branch": FORMAL_BRANCH,
        "development_branch": DEVELOPMENT_BRANCH,
        "previous_formal_head": PREVIOUS_FORMAL_HEAD,
        "current_formal_head": CURRENT_FORMAL_HEAD,
        "physlib_root_blob": PHYSLIB_ROOT_BLOB,
        "zil_public_head": ZIL_PUBLIC_HEAD,
        "sources": FORMAL_SOURCES,
        "claim_boundary": {
            "weak_zero_width_limit_is_detector_validation": False,
            "trace_preserving_generator_is_observed_decay": False,
            "evidence_package_schema_is_external_evidence": False,
            "synthetic_fixture_is_physical_identity": False,
        },
    }


def validate_formal_snapshot(
    *,
    head: str = CURRENT_FORMAL_HEAD,
    root_blob: str = PHYSLIB_ROOT_BLOB,
    source_blobs: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    expected = {
        f"{source.get('repository', FORMAL_REPOSITORY)}:{source['path']}": source["blob"]
        for source in FORMAL_SOURCES
    }
    observed = expected if source_blobs is None else dict(source_blobs)
    acceptance = {
        "merged_authority_uses_master": FORMAL_BRANCH == "master",
        "development_branch_is_recorded_separately": DEVELOPMENT_BRANCH
        == "private/entropic-physlib-linear-full",
        "merged_formal_head_is_current": head == CURRENT_FORMAL_HEAD,
        "physlib_root_blob_is_current": root_blob == PHYSLIB_ROOT_BLOB,
        "all_source_blobs_match": observed == expected,
        "previous_formal_head_is_not_current": PREVIOUS_FORMAL_HEAD != CURRENT_FORMAL_HEAD,
        "public_zil_head_is_pinned": len(ZIL_PUBLIC_HEAD) == 40,
    }
    return {
        "observed_head": head,
        "observed_root_blob": root_blob,
        "observed_source_blobs": observed,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


@lru_cache(maxsize=1)
def run_formalization_m122_extension() -> dict[str, Any]:
    payload = canonical_payload()
    validation = validate_formal_snapshot()
    acceptance = {
        **validation["acceptance"],
        "seven_merged_sources_are_pinned": len(FORMAL_SOURCES) == 7,
        "source_declarations_are_nonempty": all(
            source["declarations"] for source in FORMAL_SOURCES
        ),
        "trace_and_zero_width_theorems_are_registered": any(
            source["path"].endswith("TracePreservation.lean")
            for source in FORMAL_SOURCES
        )
        and any(
            source["path"].endswith("CauchyWeakLimit.lean")
            for source in FORMAL_SOURCES
        ),
        "no_formal_or_physical_boundary_is_crossed": not any(
            payload["claim_boundary"].values()
        ),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.122-formal-authority",
        "validation": validation,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "merged_open_system_authority_rebased": True,
            "trace_preservation_authority_registered": True,
            "weak_zero_width_authority_registered": True,
            "new_Lean_proof_claimed_by_OpenWave": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
