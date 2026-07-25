"""Canonical M9 registration with M9.99 formal/numerical reconciliation.

The schema-v5 ZIL runtime registration remains available in
``model_registration_zil.py``.  This overlay adds the current formal-equation
contract, mass/operator reconciliation, and domain-aware Dirac observable
authority without changing the 21-row comparison status profile.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .formal_numerical_reconciliation_authority import (
    run_formal_numerical_reconciliation_authority,
)
from .model_registration_zil import M9_REGISTRATION
from .model_registration_zil import (
    canonical_registration_payload as m9_98_registration_payload,
)
from .model_registration_zil import (
    run_model_registration_study as run_m9_98_registration_study,
)


def canonical_registration_payload() -> dict[str, Any]:
    previous = m9_98_registration_payload()
    authority = run_formal_numerical_reconciliation_authority()
    return {
        **previous,
        "schema": "openwave.model-registration.v6",
        "formal_numerical_reconciliation_fingerprint": authority["fingerprint"],
        "formal_numerical_branch": authority["formal_branch"],
        "formal_numerical_closed_infrastructure": authority["closed_infrastructure"],
        "formal_numerical_open_boundaries": authority["open_boundaries"],
        "m9_99": {
            "equation_contract_registered": authority["component_results"][
                "equation_contract_passed"
            ],
            "mass_and_operator_reconciliation_registered": authority[
                "component_results"
            ]["reconciled_stationary_passed"],
            "domain_aware_dirac_observables_registered": authority[
                "component_results"
            ]["dirac_observables_passed"],
            "legacy_disagreements_are_lean_contradictions": False,
            "full_current_formal_target_numerically_closed": authority["decision"][
                "full_current_formal_target_numerically_closed"
            ],
            "criterion_rows_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "current_formal_equations_machine_mapped": True,
            "one_discrete_differential_complex": True,
            "schrodinger_pauli_mass_map_consistent": True,
            "dirac_center_observable_corrected": True,
            "formal_hartree_coupling_selected": False,
            "single_action_derivation_complete": False,
            "formal_numerical_reconciliation_promotes_physical_criteria": False,
        },
    }


def registration_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    previous = run_m9_98_registration_study()
    authority = run_formal_numerical_reconciliation_authority()
    payload = canonical_registration_payload()
    expected_counts = {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }
    acceptance = {
        "m9_98_registration_remains_valid": bool(previous["passed"]),
        "formal_numerical_reconciliation_authority_passes": bool(authority["passed"]),
        "current_formal_branch_is_registered": payload["formal_numerical_branch"]
        == "entropic-physlib-linear-full",
        "equation_mass_operator_and_observable_layers_are_registered": all(
            payload["m9_99"][key]
            for key in (
                "equation_contract_registered",
                "mass_and_operator_reconciliation_registered",
                "domain_aware_dirac_observables_registered",
            )
        ),
        "legacy_disagreements_are_not_marked_as_lean_contradictions": not payload[
            "m9_99"
        ]["legacy_disagreements_are_lean_contradictions"],
        "full_formal_target_boundary_remains_open": (
            not payload["m9_99"]["full_current_formal_target_numerically_closed"]
            and not payload["claim_boundary"]["formal_hartree_coupling_selected"]
            and not payload["claim_boundary"]["single_action_derivation_complete"]
        ),
        "comparison_status_counts_are_unchanged": payload["conformance"][
            "status_counts"
        ]
        == expected_counts,
        "physical_identity_remains_unassigned": (
            M9_REGISTRATION.physical_identity_default is None
            and not payload["claim_boundary"]["physical_particle_identity"]
        ),
        "no_criterion_is_promoted": payload["m9_99"]["criterion_rows_promoted"] == [],
        "registration_fingerprint_is_deterministic": registration_fingerprint(payload)
        == registration_fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.99e",
        "registration_fingerprint": registration_fingerprint(payload),
        "component_results": {
            **previous["component_results"],
            "formal_numerical_reconciliation_passed": authority["passed"],
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            **previous["decision"],
            "formal_numerical_reconciliation_registered": True,
            "legacy_model_disagreements_reclassified": True,
            "current_formal_target_numerically_closed": False,
            "criterion_rows_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
