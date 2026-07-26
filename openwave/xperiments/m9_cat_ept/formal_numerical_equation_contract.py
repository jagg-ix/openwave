"""M9.99a: exact formal-to-numerical equation authority.

This module pins the current ``entropic-physlib-linear-full`` source surfaces used
when interpreting OpenWave numerical results.  It deliberately distinguishes:

* an exact equation or algebraic identity;
* a theorem whose analytic hypotheses remain supplied premises;
* a model term present only on one side;
* a comparison outside the Lean theorem's carrier or kinematic domain.

The contract is diagnostic authority.  It does not promote a Lean theorem, a
numerical result, or a physical particle identity.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Literal, Mapping

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"

Relation = Literal[
    "exact_structure",
    "conditional_bridge",
    "formal_term_missing_numerically",
    "numerical_term_not_in_formal_carrier",
    "carrier_mismatch",
    "parameter_mismatch",
    "observable_domain_mismatch",
    "discrete_operator_mismatch",
]

FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/CubicQuinticMildFlow.lean",
        "blob": "82a89eabf1179eff2373b2f005317e63cbd62cba",
        "role": "current target interaction: attractive Newton/Hartree plus supplied local interaction",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/CubicQuinticOrbitalStability.lean",
        "blob": "fb47b98296a771eee44570ce42b5c2ab03d450a3",
        "role": "cubic-quintic coercivity and conditional H1 minimizer/orbital-stability bridges",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/SelfBoundSchrodingerNewtonPDE.lean",
        "blob": "d84c06718e292dd18e03653efb34d237a4e2899a",
        "role": "certified self-bound Schrodinger-Newton/Hartree profile carrier",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Dirac/PauliEquationSpinOrbit.lean",
        "blob": "9752e6c317b1e3bd714c2e36bc4dd5152a6289df",
        "role": "Foldy-Wouthuysen Pauli matrix structure including relativistic, Darwin, and spin-orbit terms",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Dirac/FourSpinorDiracHamiltonian.lean",
        "blob": "31f89ac030a5fd336dd5ca74fc5488e7f6108f2b",
        "role": "free four-spinor Dirac algebra, dispersion, and velocity operator",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Electromagnetic/MaxwellContinuityCovariant.lean",
        "blob": "553c9c77b895cfcb1681b594dc370a82675412b1",
        "role": "momentum-space Maxwell/continuity algebra and conditional Green inversion",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/MuonAnomaly/ThomasBMTMagicCancellation.lean",
        "blob": "7a7863819b8c86dfa1eb5a9647b4f59250885d4f",
        "role": "T-BMT scalar carriers and exact rest-frame Dirac-Pauli rate bridge",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/ParametrizedTetradGravity/EMParticleDynamics.lean",
        "blob": "a1ef5ce20dfe0b843b124c6fa7a85b6809b8df50",
        "role": "isolated-space Coulomb kernel and abstract radiation-gauge projector",
    },
    {
        "path": "Physlib/Electromagnetism/PointParticle/ThreeDimension.lean",
        "blob": "ac69848c2707b128a24afa4e2cb3e228b1ba4859",
        "role": "distributional stationary point charge on R3",
    },
)

OPENWAVE_SOURCES = (
    {
        "path": "openwave/xperiments/m9_cat_ept/stationary_non_gaussian_branch.py",
        "blob": "15705bc4df129d097f722363964901fc448f23d8",
        "role": "legacy local-only normalized cubic-quintic stationary equation",
    },
    {
        "path": "openwave/xperiments/m9_cat_ept/gauge_spinor_stationary_feasibility.py",
        "blob": "2251567b253f60d4f0f7589473cb75bdf307e6bd",
        "role": "gauge-spinor stationary operator using exact Fourier matter derivatives",
    },
    {
        "path": "openwave/xperiments/m9_cat_ept/charged_field_tools.py",
        "blob": "9fe5656e2855736d26b2d17e7f2ff5fa5cebb033",
        "role": "periodic neutralized Maxwell inversion using centered-difference symbols",
    },
    {
        "path": "openwave/xperiments/m9_cat_ept/spinorial_pair_dynamics_current.py",
        "blob": "90a6324085d86272a21fa8bf0efa080490769b9c",
        "role": "four-spinor source-consistent pair response and legacy center/BMT comparisons",
    },
    {
        "path": "openwave/xperiments/m9_cat_ept/spatial_3d_hamiltonian.py",
        "blob": "d735cdd1aeabcc6ecb523b25be8ecadd1d0486d1",
        "role": "bounded Maxwell-Dirac engine with centered finite differences",
    },
)


@dataclass(frozen=True)
class EquationRelation:
    identifier: str
    formal_equation: str
    numerical_equation: str
    relation: Relation
    consequence: str
    formal_sources: tuple[str, ...]
    openwave_sources: tuple[str, ...]


def equation_relations() -> tuple[EquationRelation, ...]:
    f = "Physlib/QuantumMechanics/ComplexAction/"
    o = "openwave/xperiments/m9_cat_ept/"
    return (
        EquationRelation(
            "binding_interaction",
            "I_target[u] = I_Newton/Hartree[G,u] + I_local[u]",
            "I_OW[u] = integral(-alpha/2 rho^2 + beta/3 rho^3)",
            "formal_term_missing_numerically",
            "the omitted nonlocal Hartree term changes the stationary Euler-Lagrange equation, scale, chemical potential, and force law",
            (f + "EntropicTime/CubicQuinticMildFlow.lean", f + "EntropicTime/SelfBoundSchrodingerNewtonPDE.lean"),
            (o + "stationary_non_gaussian_branch.py", o + "gauge_spinor_stationary_feasibility.py"),
        ),
        EquationRelation(
            "coefficient_selection",
            "alpha and beta remain parameters subject to beta>0 coercivity and model-specific closure hypotheses",
            "alpha and beta are selected from a normalized Gaussian reference-scale ansatz",
            "parameter_mismatch",
            "Lean coercivity does not predict the OpenWave coefficient pair or its radius",
            (f + "EntropicTime/CubicQuinticOrbitalStability.lean",),
            (o + "coefficient_self_consistency.py",),
        ),
        EquationRelation(
            "schrodinger_mass_map",
            "nonrelativistic kinetic coefficient is 1/(2m)",
            "D=0.65 while the Pauli and Dirac stages use m=1",
            "parameter_mismatch",
            "the scalar branch has effective mass 1/(2D), so its convective current and lower-spinor embedding use inconsistent masses",
            (f + "Dirac/PauliEquationSpinOrbit.lean",),
            (o + "gauge_spinor_stationary_feasibility.py", o + "spinorial_pair_dynamics.py"),
        ),
        EquationRelation(
            "pauli_hamiltonian",
            "FW matrix carrier includes p^2/(2m), -p^4/(8m^3), Darwin, and spin-orbit terms",
            "-D D_A^2 + q phi - alpha rho + beta rho^2 - gq sigma.B/(4m)",
            "numerical_term_not_in_formal_carrier",
            "the formal Pauli theorem is a matrix-level reduction and is not the nonlinear self-consistent PDE executed by OpenWave",
            (f + "Dirac/PauliEquationSpinOrbit.lean",),
            (o + "gauge_spinor_stationary_feasibility.py",),
        ),
        EquationRelation(
            "maxwell_carrier",
            "isolated R3 point source or momentum-space F=dA with conditional Green inversion",
            "periodic torus with rho-mean(rho), transverse current projection, and finite extended sources",
            "carrier_mismatch",
            "the periodic neutralized field is not the isolated 1/(4 pi r) point-charge solution",
            ("Physlib/Electromagnetism/PointParticle/ThreeDimension.lean", f + "Electromagnetic/MaxwellContinuityCovariant.lean"),
            (o + "charged_field_tools.py",),
        ),
        EquationRelation(
            "discrete_differential_complex",
            "one derivative operator underlies F=dA, Bianchi, divergence, and continuity identities",
            "matter uses exact Fourier ik while Maxwell uses sin(kh)/h centered symbols",
            "discrete_operator_mismatch",
            "a field can close the projected centered Maxwell equations while failing the spectral matter stationary equation",
            (f + "Electromagnetic/MaxwellContinuityCovariant.lean",),
            (o + "gauge_spinor_stationary_feasibility.py", o + "charged_field_tools.py"),
        ),
        EquationRelation(
            "dirac_velocity",
            "d<x_i>/dt is represented by the Dirac alpha_i velocity operator; position/FW transformation is outside the proved carrier",
            "d^2<z>/dt^2 is compared directly with Lorentz force per norm",
            "observable_domain_mismatch",
            "momentum-force agreement does not imply the unprojected Dirac center obeys nonrelativistic F=ma",
            (f + "Dirac/FourSpinorDiracHamiltonian.lean",),
            (o + "spinorial_pair_dynamics_current.py",),
        ),
        EquationRelation(
            "spin_precession",
            "exact bridge is the rest-frame vertical-field two-by-two Dirac-Pauli/T-BMT rate",
            "moving extended four-spinor packet is compared with gq/(2m) S_avg cross B_avg",
            "observable_domain_mismatch",
            "the comparison omits gamma, beta cross E, field inhomogeneity, local torque averaging, and the covariant Thomas term",
            (f + "MuonAnomaly/ThomasBMTMagicCancellation.lean",),
            (o + "spinorial_pair_dynamics_current.py",),
        ),
        EquationRelation(
            "dirac_clifford_algebra",
            "alpha_i^2=beta^2=1 and the Clifford anticommutators",
            "the same canonical Dirac-representation matrices are used numerically",
            "exact_structure",
            "the matrix representation agrees; the disagreement begins in interactions, carriers, and observables",
            (f + "Dirac/FourSpinorDiracHamiltonian.lean",),
            (o + "spatial_3d_types.py",),
        ),
    )


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(c in "0123456789abcdef" for c in value.lower())


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.formal-numerical-equation-contract.v1",
        "formal_repository": FORMAL_REPOSITORY,
        "formal_branch": FORMAL_BRANCH,
        "formal_sources": [dict(item) for item in FORMAL_SOURCES],
        "openwave_sources": [dict(item) for item in OPENWAVE_SOURCES],
        "relations": [asdict(item) for item in equation_relations()],
        "authority_boundary": {
            "lean_kernel_is_proof_authority": True,
            "openwave_is_numerical_model_authority": True,
            "structural_similarity_is_not_equation_identity": True,
            "criterion_promotion_allowed": False,
        },
    }


def contract_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_formal_numerical_equation_contract() -> dict[str, Any]:
    payload = canonical_payload()
    rows = equation_relations()
    counts = {relation: sum(row.relation == relation for row in rows) for relation in (
        "exact_structure",
        "conditional_bridge",
        "formal_term_missing_numerically",
        "numerical_term_not_in_formal_carrier",
        "carrier_mismatch",
        "parameter_mismatch",
        "observable_domain_mismatch",
        "discrete_operator_mismatch",
    )}
    acceptance = {
        "current_formal_branch_is_explicit": FORMAL_BRANCH == "entropic-physlib-linear-full",
        "all_formal_sources_are_blob_pinned": all(_is_sha(item["blob"]) for item in FORMAL_SOURCES),
        "all_openwave_sources_are_blob_pinned": all(_is_sha(item["blob"]) for item in OPENWAVE_SOURCES),
        "hartree_omission_is_explicit": any(row.identifier == "binding_interaction" and row.relation == "formal_term_missing_numerically" for row in rows),
        "mass_map_mismatch_is_explicit": any(row.identifier == "schrodinger_mass_map" and row.relation == "parameter_mismatch" for row in rows),
        "operator_family_mismatch_is_explicit": any(row.identifier == "discrete_differential_complex" and row.relation == "discrete_operator_mismatch" for row in rows),
        "dirac_and_bmt_domain_mismatches_are_explicit": sum(row.relation == "observable_domain_mismatch" for row in rows) >= 2,
        "exact_clifford_overlap_is_preserved": any(row.identifier == "dirac_clifford_algebra" and row.relation == "exact_structure" for row in rows),
        "contract_promotes_no_criterion": not payload["authority_boundary"]["criterion_promotion_allowed"],
        "fingerprint_is_deterministic": contract_fingerprint(payload) == contract_fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.99a",
        "relation_counts": counts,
        "fingerprint": contract_fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "openwave_legacy_results_are_direct_numerical_tests_of_current_formal_equations": False,
            "formal_and_numerical_equations_are_now_machine_mapped": True,
            "criterion_rows_promoted": [],
            "physical_identity_changed": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
