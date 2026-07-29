"""M9.140 canonical CAT/EPT model contract and integration facade.

This module does not introduce a new physical particle identity. It unifies the
existing M9 particle kernel, reduced matter--geometry--entropy evolution,
reduced U(1) evolution, and exact Physlib authority surfaces behind one stable
model-facing API. The three-dimensional charged Pauli--Hartree--U(1) carrier
remains the next implementation target rather than being implied here.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields, is_dataclass
from functools import lru_cache
from hashlib import sha256
import importlib
import json
from typing import Any, Mapping

MILESTONE = "M9.140"
SCHEMA = "openwave.m9.canonical-particle-contract.v1"
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
STABLE_ALIAS_MILESTONE = "M9.126"


@dataclass(frozen=True)
class CanonicalComponent:
    key: str
    role: str
    symbol: str
    source_milestone: str
    carrier: str
    execution_status: str
    physical_promotion: bool = False

    def __post_init__(self) -> None:
        if not all((self.key, self.role, self.symbol, self.source_milestone, self.carrier)):
            raise ValueError("complete canonical component metadata required")
        if ":" not in self.symbol:
            raise ValueError("component symbol must use module:attribute syntax")
        if self.physical_promotion:
            raise ValueError("M9.140 cannot promote a physical particle identity")


COMPONENTS = (
    CanonicalComponent(
        key="particle-kernel",
        role="reusable three-dimensional localized-branch API",
        symbol="openwave.xperiments.m9_cat_ept.particle_model:CatEptParticleModel",
        source_milestone="M9.89",
        carrier="3D complex scalar field",
        execution_status="implemented",
    ),
    CanonicalComponent(
        key="matter-geometry-entropy",
        role="coupled real-action, geometry-feedback, and entropic-time evolution",
        symbol="openwave.xperiments.m9_cat_ept.coupled_cat_ept_evolution_m132:run_with_config",
        source_milestone="M9.132",
        carrier="1D periodic complex field plus scalar geometry",
        execution_status="implemented-reduced",
    ),
    CanonicalComponent(
        key="gauge-matter-geometry-entropy",
        role="covariant U(1), current, geometry, and entropic-time evolution",
        symbol="openwave.xperiments.m9_cat_ept.gauge_coupled_cat_ept_m133:run_with_config",
        source_milestone="M9.133",
        carrier="1D periodic complex field plus reduced U(1)",
        execution_status="implemented-reduced",
    ),
    CanonicalComponent(
        key="formal-numerical-equation-contract",
        role="fail-closed exact source and relation authority",
        symbol=(
            "openwave.xperiments.m9_cat_ept."
            "formal_numerical_equation_contract_current:"
            "run_formal_numerical_equation_contract"
        ),
        source_milestone="M9.99",
        carrier="formal/numerical relation registry",
        execution_status="implemented",
    ),
    CanonicalComponent(
        key="complex-action-entropic-gauge-authority",
        role="complex residual, entropic gradient, and gauge invariance authority",
        symbol=(
            "openwave.xperiments.m9_cat_ept."
            "complex_action_gauge_authority_m138:"
            "run_m138_complex_action_gauge_authority"
        ),
        source_milestone="M9.138",
        carrier="finite theorem consequence checks",
        execution_status="implemented",
    ),
    CanonicalComponent(
        key="global-physlib-sector-authority",
        role="retarded causality, Pauli coupling, and axial-topology authority",
        symbol=(
            "openwave.xperiments.m9_cat_ept."
            "global_physlib_sectors_m139:run_global_physlib_sectors"
        ),
        source_milestone="M9.139",
        carrier="finite theorem consequence checks",
        execution_status="implemented",
    ),
)


ACTION_TERM_MAP = (
    {
        "id": "kinetic-mass-map",
        "sector": "real",
        "formal_target": "nonrelativistic coefficient 1/(2m)",
        "numerical_surfaces": ("particle-kernel", "matter-geometry-entropy", "gauge-matter-geometry-entropy"),
        "status": "mapped-with-carrier-differences",
        "required_gate": "one canonical mass ledger",
    },
    {
        "id": "hartree-binding",
        "sector": "real",
        "formal_target": "attractive Newton/Hartree plus supplied local interaction",
        "numerical_surfaces": ("matter-geometry-entropy", "gauge-matter-geometry-entropy"),
        "status": "implemented-in-reduced-carriers",
        "required_gate": "3D coupled stationary branch",
    },
    {
        "id": "u1-covariant-coupling",
        "sector": "real",
        "formal_target": "F=dA, conserved current, and gauge-invariant coupling",
        "numerical_surfaces": ("gauge-matter-geometry-entropy",),
        "status": "implemented-in-reduced-carrier",
        "required_gate": "shared 3D differential complex and Gauss closure",
    },
    {
        "id": "imaginary-action-relaxation",
        "sector": "imaginary",
        "formal_target": "entropicTimeGradient = E_I / hbar",
        "numerical_surfaces": ("matter-geometry-entropy", "gauge-matter-geometry-entropy"),
        "status": "effective-law-not-yet-derived-from-one-discrete-S_I",
        "required_gate": "explicit discrete imaginary functional and variational derivative",
    },
    {
        "id": "pauli-spin-sector",
        "sector": "real",
        "formal_target": "Foldy--Wouthuysen Pauli, Darwin, and spin-orbit structure",
        "numerical_surfaces": ("particle-kernel",),
        "status": "separate-bridge-not-yet-one-coupled-carrier",
        "required_gate": "3D Pauli--Hartree--U(1) state and stationary solver",
    },
)


NEXT_MODEL_GATES = (
    "one 3D Pauli--Hartree--U(1) state contract",
    "one odd-grid Fourier differential complex",
    "measured nonzero winding embedded in the solved field",
    "constraint-preserving charge/current/Gauss evolution",
    "explicit discrete imaginary action",
    "stable charged stationary branch",
    "grid refinement and perturbation campaign",
    "physical calibration and withheld prediction",
)


def resolve_symbol(spec: str) -> Any:
    module_name, attribute = spec.split(":", 1)
    module = importlib.import_module(module_name)
    return getattr(module, attribute)


def _field_names(spec: str) -> set[str]:
    symbol = resolve_symbol(spec)
    if not is_dataclass(symbol):
        raise TypeError(f"{spec} is not a dataclass")
    return {item.name for item in fields(symbol)}


@dataclass(frozen=True)
class CanonicalCatEptModel:
    """Facade over the existing executable M9 model surfaces."""

    particle_model: Any

    @classmethod
    def repository_default(
        cls, *, winding_sector: int = 0, particle_id: str | None = None
    ) -> "CanonicalCatEptModel":
        particle_cls = resolve_symbol(
            "openwave.xperiments.m9_cat_ept.particle_model:CatEptParticleModel"
        )
        return cls(
            particle_cls.repository_default(
                winding_sector=winding_sector,
                particle_id=particle_id,
            )
        )

    def construct_stationary_state(self, **kwargs: Any) -> Any:
        return self.particle_model.construct_stationary_state(**kwargs)

    def evolve_particle_state(self, state: Any, **kwargs: Any) -> Any:
        return self.particle_model.evolve(state, **kwargs)

    @staticmethod
    def run_matter_geometry_entropy(config: Any | None = None) -> Mapping[str, Any]:
        module = importlib.import_module(
            "openwave.xperiments.m9_cat_ept.coupled_cat_ept_evolution_m132"
        )
        return module.run_with_config(config or module.CoupledCATEPTConfig())

    @staticmethod
    def run_gauge_matter_geometry_entropy(config: Any | None = None) -> Mapping[str, Any]:
        module = importlib.import_module(
            "openwave.xperiments.m9_cat_ept.gauge_coupled_cat_ept_m133"
        )
        return module.run_with_config(config or module.GaugeCATEPTConfig())


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "model": "M9 CAT/EPT",
        "formal_authority": {
            "repository": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "equation_contract": (
                "openwave.xperiments.m9_cat_ept."
                "formal_numerical_equation_contract_current"
            ),
        },
        "lineage": {
            "stable_compatibility_alias": STABLE_ALIAS_MILESTONE,
            "latest_integrated_model": MILESTONE,
            "criterion_statuses_changed": False,
        },
        "components": [asdict(component) for component in COMPONENTS],
        "action_term_map": list(ACTION_TERM_MAP),
        "canonical_api": (
            "openwave.xperiments.m9_cat_ept."
            "canonical_particle_model_m140:CanonicalCatEptModel"
        ),
        "next_model_gates": list(NEXT_MODEL_GATES),
        "claim_boundary": {
            "three_dimensional_coupled_pauli_u1_model_complete": False,
            "stable_charged_stationary_branch_complete": False,
            "physical_particle_identity": False,
            "physical_calibration_complete": False,
            "external_prediction_complete": False,
            "criterion_rows_promoted": [],
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    raw = json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(raw.encode()).hexdigest()


@lru_cache(maxsize=1)
def run_canonical_model_contract() -> dict[str, Any]:
    from .complex_action_gauge_authority_m138 import (
        run_m138_complex_action_gauge_authority,
    )
    from .formal_numerical_equation_contract_current import (
        run_formal_numerical_equation_contract,
    )
    from .global_physlib_sectors_m139 import run_global_physlib_sectors
    from .model_conformance_current import (
        CURRENT_CONFORMANCE_SCHEMA,
        CURRENT_MILESTONE as STABLE_CONFORMANCE_MILESTONE,
    )
    from .model_registration_current import (
        CURRENT_MILESTONE as STABLE_REGISTRATION_MILESTONE,
        CURRENT_SCHEMA as STABLE_REGISTRATION_SCHEMA,
    )

    resolved = {component.key: resolve_symbol(component.symbol) for component in COMPONENTS}
    formal_contract = run_formal_numerical_equation_contract()
    complex_action = run_m138_complex_action_gauge_authority()
    global_sectors = run_global_physlib_sectors()

    particle_fields = _field_names(
        "openwave.xperiments.m9_cat_ept.particle_model:CatEptParticleState"
    )
    coupled_fields = _field_names(
        "openwave.xperiments.m9_cat_ept."
        "coupled_cat_ept_evolution_m132:CoupledCATEPTState"
    )
    gauge_fields = _field_names(
        "openwave.xperiments.m9_cat_ept."
        "gauge_coupled_cat_ept_m133:GaugeCATEPTState"
    )

    payload = canonical_payload()
    acceptance = {
        "all_component_symbols_resolve": len(resolved) == len(COMPONENTS),
        "stable_registration_alias_is_preserved": (
            STABLE_REGISTRATION_MILESTONE == STABLE_ALIAS_MILESTONE
            and STABLE_REGISTRATION_SCHEMA == "openwave.model-registration.v29"
        ),
        "stable_conformance_alias_is_preserved": (
            STABLE_CONFORMANCE_MILESTONE == STABLE_ALIAS_MILESTONE
            and CURRENT_CONFORMANCE_SCHEMA == "openwave.m9.models-conformance.v22"
        ),
        "formal_equation_contract_passes": bool(formal_contract["passed"]),
        "complex_action_authority_passes": bool(complex_action.passed),
        "global_physlib_sector_authority_passes": bool(global_sectors["passed"]),
        "particle_state_retains_3d_and_winding_metadata": {
            "field",
            "spacing",
            "center",
            "declared_winding_sector",
            "winding_embedded",
        }.issubset(particle_fields),
        "matter_geometry_entropy_state_is_registered": {
            "psi",
            "potential",
            "entropic_time",
        }.issubset(coupled_fields),
        "gauge_coupled_state_is_registered": {
            "psi",
            "potential",
            "vector_potential",
            "electric_field",
            "entropic_time",
        }.issubset(gauge_fields),
        "imaginary_action_derivation_gap_is_explicit": any(
            row["id"] == "imaginary-action-relaxation"
            and row["status"].startswith("effective-law")
            for row in payload["action_term_map"]
        ),
        "three_dimensional_coupled_model_remains_open": not payload[
            "claim_boundary"
        ]["three_dimensional_coupled_pauli_u1_model_complete"],
        "no_physical_or_criterion_promotion": (
            not payload["claim_boundary"]["physical_particle_identity"]
            and payload["claim_boundary"]["criterion_rows_promoted"] == []
            and all(not component.physical_promotion for component in COMPONENTS)
        ),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.140a",
        "fingerprint": fingerprint(payload),
        "authority": {
            "formal_equation_contract": formal_contract["fingerprint"],
            "complex_action": complex_action.fingerprint(),
            "global_physlib_sectors": global_sectors["fingerprint"],
        },
        "state_contracts": {
            "particle": sorted(particle_fields),
            "matter_geometry_entropy": sorted(coupled_fields),
            "gauge_matter_geometry_entropy": sorted(gauge_fields),
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "existing_m9_surfaces_are_unified_behind_one_api": True,
            "stable_alias_and_latest_integration_are_distinguished": True,
            "next_required_carrier_is_3d_pauli_hartree_u1": True,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
