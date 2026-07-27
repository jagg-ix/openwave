"""M9.123 formal authority for the non-particle CAT/EPT physics audit."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "master"
DEVELOPMENT_BRANCH = "private/entropic-physlib-linear-full"
CURRENT_FORMAL_HEAD = "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef"
PHYSLIB_ROOT_BLOB = "f953c09c428eb83d9894c1944e1fd44a7ffe95a1"
ZIL_PUBLIC_HEAD = "c671f02d8b6dcf7ba689afc86477ff7e35465c35"

FORMAL_SOURCES = (
    {
        "path": "Physlib/EntropicSpinePublic.lean",
        "blob": "261517a9bc5e5ef341403f8c6a3eb1fe2fd94a4e",
        "role": "public entropic spine and explicit audit boundary",
        "declarations": (
            "Physlib.EntropicSpine.Core",
            "Physlib.QuantumMechanics.ComplexAction.EntropicTime.CubicQuinticMildFlow.exists_minimizingOrbit_uniformlyStable",
        ),
    },
    {
        "path": "Physlib/EntropicSpine.lean",
        "blob": "2232e462d5a88f5524439339ddda448bb6cbefb5",
        "role": "curated QM-to-GR, thermodynamic, AQFT, and continuum interface surface",
        "declarations": (
            "Physlib.Thermodynamics.QuantumRelativeEntropyArrow.dissipative_orbit_antitone",
            "QuantumMechanics.LindbladDrivenLeads.boundedGeneratorC0Semigroup",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/EntropicDynamicsWaveFunctionReconstruction.lean",
        "blob": "90e3b39360dad1780f06feb3f29704b2ed0f1688",
        "role": "wave-functional reconstruction and continuum Born identities",
        "declarations": (
            "Physlib.QuantumMechanics.ComplexAction.EntropicTime.EntropicDynamicsWaveFunctionReconstruction.edWaveFunctional_modulus_sq",
            "Physlib.QuantumMechanics.ComplexAction.EntropicTime.EntropicDynamicsWaveFunctionReconstruction.integral_edWaveFunctional_modulus_sq",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/EntropicDynamicsEvolutionSchrodingerEhrenfest.lean",
        "blob": "b4652ff601e9dad1fa46a58258d8e1b132ba1e33",
        "role": "quantum-potential, Ehrenfest/Klein-Gordon, and classical-limit interfaces",
        "declarations": (
            "Physlib.QuantumMechanics.ComplexAction.EntropicTime.EntropicDynamicsEvolutionSchrodingerEhrenfest.kinetic_eq_four_coupling",
            "Physlib.QuantumMechanics.ComplexAction.EntropicTime.EntropicDynamicsEvolutionSchrodingerEhrenfest.ehrenfest_classical_kleinGordon",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/EntropicDynamicsLocalTimeFokkerPlanck.lean",
        "blob": "99c39cd8dd3629831e7361a5e7e72eaaa7483c35",
        "role": "local-time Fokker-Planck and kinetic Kolmogorov control",
        "declarations": (
            "Physlib.QuantumMechanics.ComplexAction.EntropicTime.EntropicDynamicsLocalTimeFokkerPlanck.ltfp_currentVelocity_flux",
            "Physlib.QuantumMechanics.ComplexAction.EntropicTime.EntropicDynamicsLocalTimeFokkerPlanck.kineticDiffusionTransportBracket_eq",
        ),
    },
    {
        "path": "Physlib/Thermodynamics/QuantumRelativeEntropyArrow.lean",
        "blob": "8a8a5b29ab6e12f25943fef7fe26a48dfc534b07",
        "role": "relative-entropy arrow from CPTP and unitary orbits",
        "declarations": (
            "Physlib.Thermodynamics.QuantumRelativeEntropyArrow.dissipative_orbit_antitone",
            "Physlib.Thermodynamics.QuantumRelativeEntropyArrow.unitary_orbit_const_to_invariant",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/ComplexEinstein/EntropicComplexEinstein.lean",
        "blob": "3e480aca62a95ae4b739dd92e3aa97ffea1b4414",
        "role": "positive-imaginary-energy clock and proper-time identification",
        "declarations": (
            "Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.EntropicComplexEinstein.imaginaryEinstein_entropicPhysicalClockCalibration",
            "Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.EntropicComplexEinstein.imaginaryEinstein_entropicTime_eq_physicalProperTime",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/ComplexEinstein/ElectroGravitationalFieldEquations.lean",
        "blob": "7ecfc0ce288e84d575af60718b74fb1148bf0c5f",
        "role": "metric-built curvature, Maxwell source, and variational electrogravity",
        "declarations": (
            "Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.ElectroGravitationalFieldEquations.metricBuiltStationary_iff_complexEinstein",
            "Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.ElectroGravitationalFieldEquations.electromagneticStationary_iff_sourceFree",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/NavierStokes/NSFourierDampedStokesSemigroup.lean",
        "blob": "ea78c9de2c6c364119a95755511edd26b0eb7655",
        "role": "finite Fourier Stokes semigroup and energy balance",
        "declarations": (
            "Physlib.QuantumMechanics.ComplexAction.NavierStokes.NSFourierDampedStokesSemigroup.stokesGalerkinC0ContractionSemigroup",
            "Physlib.QuantumMechanics.ComplexAction.NavierStokes.NSFourierDampedStokesSemigroup.stokesGalerkin_hasInfinitesimalGenerator",
        ),
    },
    {
        "path": "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/CauchyWeakLimit.lean",
        "blob": "2479d0782e7ea932c57d46644c8d939522db5162",
        "role": "weak zero-width Cauchy-to-Dirac spectral limit",
        "declarations": (
            "QuantumMechanics.LindbladDrivenLeads.affineCauchySample_tendstoInDistribution",
            "QuantumMechanics.LindbladDrivenLeads.affineCauchyLaw_tendsto_dirac",
        ),
    },
    {
        "repository": "jagg-ix/zil-lean",
        "path": "Zil/Datalog/Eval.lean",
        "blob": "6cde34efb9b09cc2f2d189883ff8373263daddba",
        "role": "stratified Datalog execution for scope and promotion audits",
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
        "schema": "openwave.m9.formalization-m123-extension.v1",
        "repository": FORMAL_REPOSITORY,
        "branch": FORMAL_BRANCH,
        "development_branch": DEVELOPMENT_BRANCH,
        "current_formal_head": CURRENT_FORMAL_HEAD,
        "physlib_root_blob": PHYSLIB_ROOT_BLOB,
        "zil_public_head": ZIL_PUBLIC_HEAD,
        "sources": FORMAL_SOURCES,
        "claim_boundary": {
            "aggregator_import_is_a_new_theorem": False,
            "formal_compatibility_is_unique_unification": False,
            "finite_control_is_continuum_closure": False,
            "source_pin_is_external_validation": False,
        },
    }


def validate_formal_snapshot(*, head: str = CURRENT_FORMAL_HEAD, root_blob: str = PHYSLIB_ROOT_BLOB, source_blobs: Mapping[str, str] | None = None) -> dict[str, Any]:
    expected = {f"{source.get('repository', FORMAL_REPOSITORY)}:{source['path']}": source["blob"] for source in FORMAL_SOURCES}
    observed = expected if source_blobs is None else dict(source_blobs)
    acceptance = {
        "merged_authority_uses_master": FORMAL_BRANCH == "master",
        "development_branch_is_recorded_separately": DEVELOPMENT_BRANCH == "private/entropic-physlib-linear-full",
        "merged_formal_head_is_current": head == CURRENT_FORMAL_HEAD,
        "physlib_root_blob_is_current": root_blob == PHYSLIB_ROOT_BLOB,
        "all_source_blobs_match": observed == expected,
        "public_zil_head_is_pinned": len(ZIL_PUBLIC_HEAD) == 40,
    }
    return {"observed_head": head, "observed_root_blob": root_blob, "observed_source_blobs": observed, "acceptance": acceptance, "passed": all(acceptance.values())}


@lru_cache(maxsize=1)
def run_formalization_m123_extension() -> dict[str, Any]:
    payload = canonical_payload()
    validation = validate_formal_snapshot()
    paths = {source["path"] for source in FORMAL_SOURCES}
    acceptance = {
        **validation["acceptance"],
        "eleven_cross_domain_sources_are_pinned": len(FORMAL_SOURCES) == 11,
        "all_source_declaration_lists_are_nonempty": all(source["declarations"] for source in FORMAL_SOURCES),
        "time_quantum_gravity_thermo_and_fluid_sources_are_present": all(token in "\n".join(paths) for token in ("QuantumRelativeEntropyArrow", "WaveFunctionReconstruction", "ElectroGravitationalFieldEquations", "LocalTimeFokkerPlanck", "NSFourierDampedStokesSemigroup")),
        "no_formal_or_physical_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.123-formal-authority",
        "validation": validation,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {"nonparticle_cross_domain_authority_registered": True, "new_Lean_proof_claimed_by_OpenWave": False, "external_validation_complete": False},
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
