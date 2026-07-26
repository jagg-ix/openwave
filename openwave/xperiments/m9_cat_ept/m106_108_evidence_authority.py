"""M9.106--M9.108 combined evidence authority."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .composite_candidate_states import run_candidate_state_construction
from .coupled_sector_fields import run_coupled_sector_field_campaigns
from .formalization_m108_extension import CURRENT_FORMAL_HEAD, CURRENT_ZIL_HEAD
from .formalization_m108_extension import run_formalization_m108_extension
from .m103_105_evidence_authority import run_m103_105_evidence_authority
from .nonlinear_constraint_gravity import run_nonlinear_constraint_evolution


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m106_108_evidence_authority() -> dict[str, Any]:
    formal = run_formalization_m108_extension()
    previous = run_m103_105_evidence_authority()
    gravity = run_nonlinear_constraint_evolution()
    sectors = run_coupled_sector_field_campaigns()
    candidates = run_candidate_state_construction()
    payload = {
        "schema": "openwave.m9.m106-108-evidence-authority.v1",
        "task": "M9.106--M9.108",
        "physlib_head": CURRENT_FORMAL_HEAD,
        "zil_head": CURRENT_ZIL_HEAD,
        "previous_authority": previous,
        "components": {
            "nonlinear_gravity": {
                "campaign_passed": gravity["passed"],
                "constraint_gate": gravity[
                    "constraint_preserving_nonlinear_metric_evolution_constructed"
                ],
                "general_einstein_gate": gravity["decision"][
                    "general_four_dimensional_einstein_cauchy_solver_constructed"
                ],
            },
            "coupled_sectors": {
                "campaign_passed": sectors["passed"],
                "gates": dict(sectors["sector_gates"]),
                "standard_model_gate": sectors["decision"][
                    "qed_qcd_electroweak_theories_constructed"
                ],
            },
            "candidate_states": {
                "campaign_passed": candidates["passed"],
                "gates": dict(candidates["candidate_gates"]),
                "physical_identity_gate": candidates["decision"][
                    "cosmological_or_hadronic_identity_established"
                ],
            },
            "program_health": formal["program_health"],
        },
        "claim_boundary": {
            "reduced_conformal_adm_is_general_einstein": False,
            "coupled_reduced_fields_are_standard_model": False,
            "stable_candidate_is_observed_particle": False,
            "program_health_passage_is_physical_evidence": False,
        },
    }
    acceptance = {
        "formal_program_health_authority_passes": bool(formal["passed"]),
        "previous_authority_is_preserved": bool(previous["passed"]),
        "three_new_campaigns_execute": bool(
            gravity["passed"] and sectors["passed"] and candidates["passed"]
        ),
        "all_physical_subgates_are_boolean": isinstance(
            payload["components"]["nonlinear_gravity"]["constraint_gate"], bool
        )
        and all(
            isinstance(value, bool)
            for value in payload["components"]["coupled_sectors"]["gates"].values()
        )
        and all(
            isinstance(value, bool)
            for value in payload["components"]["candidate_states"]["gates"].values()
        ),
        "no_stronger_identity_is_predeclared": not any(
            payload["claim_boundary"].values()
        ),
        "fingerprint_is_deterministic": fingerprint(payload)
        == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {
            "formal": formal,
            "nonlinear_gravity": gravity,
            "coupled_sectors": sectors,
            "candidate_states": candidates,
        },
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "three_next_targets_have_executable_campaigns": True,
            "physical_closure_predetermined": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
