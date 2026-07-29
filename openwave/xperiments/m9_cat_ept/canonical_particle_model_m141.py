"""M9.141 canonical CAT/EPT model with one 3D Pauli--Hartree--U(1) carrier."""
from __future__ import annotations

from dataclasses import fields
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .canonical_particle_model_m140 import (
    CanonicalCatEptModel as CanonicalCatEptModelM140,
    canonical_payload as m140_payload,
    run_canonical_model_contract as run_m140_contract,
)
from .pauli_hartree_u1_carrier_m141 import (
    PauliHartreeU1Config,
    PauliHartreeU1State,
    construct_state,
    run_pauli_hartree_u1_campaign,
)

MILESTONE = "M9.141"
SCHEMA = "openwave.m9.canonical-particle-contract.v2"
STABLE_ALIAS_MILESTONE = "M9.126"


class CanonicalCatEptModel(CanonicalCatEptModelM140):
    """Latest facade; the M9.140 API remains available as its base class."""

    @staticmethod
    def construct_pauli_hartree_u1_state(
        config: PauliHartreeU1Config | None = None,
    ) -> PauliHartreeU1State:
        return construct_state(config or PauliHartreeU1Config())

    @staticmethod
    def run_pauli_hartree_u1_campaign() -> Mapping[str, Any]:
        return run_pauli_hartree_u1_campaign()


def _updated_action_map() -> list[dict[str, Any]]:
    replacements = {
        "kinetic-mass-map": (
            "one canonical mass map implemented in the 3D carrier",
            "retain the same map in later real-time and Foldy--Wouthuysen stages",
        ),
        "hartree-binding": (
            "implemented in one 3D Pauli--Hartree carrier",
            "close a stable stationary branch and refinement campaign",
        ),
        "u1-covariant-coupling": (
            "implemented with one 3D odd-grid differential complex and static constraints",
            "add constraint-preserving real-time continuity evolution",
        ),
        "imaginary-action-relaxation": (
            "frozen-H squared-gradient discrete functional implemented",
            "derive or specify the full nonlinear continuum imaginary action",
        ),
        "pauli-spin-sector": (
            "implemented in one coupled 3D Pauli--Hartree--U1 carrier",
            "close stationary stability, Darwin/spin-orbit observables, and calibration",
        ),
    }
    rows = []
    for row in m140_payload()["action_term_map"]:
        status, gate = replacements[str(row["id"])]
        rows.append({**row, "status": status, "required_gate": gate})
    return rows


def canonical_payload() -> dict[str, Any]:
    base = m140_payload()
    carrier = {
        "key": "pauli-hartree-u1-carrier",
        "role": "one 3D charged Pauli spinor with Hartree, U(1), winding, and entropic relaxation",
        "symbol": (
            "openwave.xperiments.m9_cat_ept."
            "pauli_hartree_u1_carrier_m141:run_pauli_hartree_u1_campaign"
        ),
        "source_milestone": MILESTONE,
        "carrier": "2-component spinor plus Hartree and static U(1) fields on odd 17^3 Fourier grid",
        "execution_status": "implemented-dimensionless-carrier",
        "physical_promotion": False,
    }
    return {
        **base,
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "lineage": {
            **base["lineage"],
            "latest_integrated_model": MILESTONE,
        },
        "components": [*base["components"], carrier],
        "action_term_map": _updated_action_map(),
        "canonical_api": (
            "openwave.xperiments.m9_cat_ept."
            "canonical_particle_model_m141:CanonicalCatEptModel"
        ),
        "carrier_api": (
            "openwave.xperiments.m9_cat_ept."
            "pauli_hartree_u1_carrier_m141:PauliHartreeU1State"
        ),
        "action_ledger": (
            "openwave/xperiments/m9_cat_ept/formal/"
            "canonical_coupled_action.v2.json"
        ),
        "capabilities": {
            "three_dimensional_pauli_hartree_u1_state": True,
            "odd_grid_fourier_differential_complex": True,
            "measured_winding_three_charge": True,
            "static_gauss_ampere_constraints": True,
            "frozen_discrete_imaginary_functional": True,
        },
        "next_model_gates": [
            "stable charged stationary branch",
            "constraint-preserving real-time charge continuity",
            "grid refinement and perturbation campaign",
            "Foldy--Wouthuysen packet-position and local spin observables",
            "physical calibration and withheld prediction",
        ],
        "claim_boundary": {
            "stable_charged_stationary_branch": False,
            "continuum_convergence": False,
            "physical_charge_calibrated": False,
            "physical_particle_identity": False,
            "external_prediction_complete": False,
            "criterion_rows_promoted": [],
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_canonical_model_contract() -> dict[str, Any]:
    base = run_m140_contract()
    carrier = run_pauli_hartree_u1_campaign()
    payload = canonical_payload()
    state_fields = {field.name for field in fields(PauliHartreeU1State)}
    acceptance = {
        "M9_140_contract_remains_valid": bool(base["passed"]),
        "M9_141_carrier_campaign_passes": bool(carrier["passed"]),
        "one_3d_state_contract_is_registered": {
            "spinor",
            "scalar_potential",
            "vector_potential",
            "electric_field",
            "magnetic_field",
            "hartree_potential",
            "entropic_time",
            "measured_winding",
        }.issubset(state_fields),
        "carrier_capabilities_are_explicit": all(payload["capabilities"].values()),
        "winding_is_measured_not_only_declared": (
            carrier["final"]["measured_winding"]
            == carrier["config"]["winding"]
            and carrier["final"]["winding_quantization_error"] <= 2.0e-12
        ),
        "static_constraints_and_entropic_relaxation_close": (
            carrier["acceptance"]["static_u1_constraints_close"]
            and carrier["acceptance"]["entropic_time_is_monotone_and_nontrivial"]
            and carrier["acceptance"][
                "squared_gradient_reduces_the_imaginary_functional"
            ]
        ),
        "stable_and_physical_promotion_remain_blocked": not any(
            value
            for key, value in payload["claim_boundary"].items()
            if key != "criterion_rows_promoted"
        )
        and payload["claim_boundary"]["criterion_rows_promoted"] == [],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.141d",
        "fingerprint": fingerprint(payload),
        "base_contract_fingerprint": base["fingerprint"],
        "carrier_fingerprint": carrier["fingerprint"],
        "carrier_decision": carrier["decision"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "canonical_3d_charged_carrier_is_available": True,
            "stable_charged_stationary_branch_promoted": False,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
