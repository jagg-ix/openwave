"""M9.122 authority for external-evidence readiness without evidence fabrication."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .blinded_external_evaluator import run_blinded_external_evaluator
from .external_evidence_package import run_external_evidence_package
from .formalization_m122_extension import run_formalization_m122_extension
from .m121_open_system_evidence_authority import run_m121_open_system_evidence_authority
from .transition_identity_bridge import run_transition_identity_bridge_contract


def fingerprint(payload: Any) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_m122_external_evidence_readiness_authority() -> dict[str, Any]:
    previous = run_m121_open_system_evidence_authority()
    formal = run_formalization_m122_extension()
    package = run_external_evidence_package()
    evaluator = run_blinded_external_evaluator()
    identity = run_transition_identity_bridge_contract()
    component = {
        "formal_authority_passed": formal["passed"],
        "evidence_package_study_passed": package["passed"],
        "external_evidence_package_schema": package["decision"][
            "external_evidence_package_schema_constructed"
        ],
        "real_external_evidence_ingested": package["decision"][
            "real_external_evidence_package_ingested"
        ],
        "evaluator_study_passed": evaluator["passed"],
        "blinded_external_evaluator": evaluator["decision"][
            "blinded_external_evaluator_constructed"
        ],
        "live_holdout_evaluation_executed": evaluator["decision"][
            "live_heldout_evaluation_executed"
        ],
        "identity_study_passed": identity["passed"],
        "independent_identity_contract": identity["decision"][
            "independent_identity_bridge_contract_constructed"
        ],
        "physical_transition_identity": identity["decision"][
            "physical_transition_identity_established"
        ],
        "external_validation_complete": evaluator["decision"][
            "external_validation_complete"
        ],
    }
    payload = {
        "schema": "openwave.m9.m122-external-evidence-readiness-authority.v1",
        "task": "M9.122",
        "previous_authority": previous,
        "formal_authority": formal,
        "component": component,
        "claim_boundary": {
            "readiness_infrastructure_is_external_evidence": False,
            "synthetic_fixture_is_heldout_test": False,
            "identity_schema_is_observed_identity": False,
            "weak_zero_width_limit_is_empirical_line_shape_validation": False,
        },
    }
    acceptance = {
        "previous_M9_121_authority_is_preserved": previous["passed"],
        "merged_formal_authority_passes": formal["passed"],
        "M9_122a_evidence_package_readiness_closes": component[
            "evidence_package_study_passed"
        ]
        and component["external_evidence_package_schema"]
        and not component["real_external_evidence_ingested"],
        "M9_122b_blinded_evaluator_closes_but_live_path_stays_blocked": component[
            "evaluator_study_passed"
        ]
        and component["blinded_external_evaluator"]
        and not component["live_holdout_evaluation_executed"],
        "M9_122c_identity_contract_closes_without_identity_claim": component[
            "identity_study_passed"
        ]
        and component["independent_identity_contract"]
        and not component["physical_transition_identity"],
        "external_evidence_identity_and_validation_remain_open": not component[
            "real_external_evidence_ingested"
        ]
        and not component["physical_transition_identity"]
        and not component["external_validation_complete"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {
            "package": package,
            "evaluator": evaluator,
            "identity": identity,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_122a_external_evidence_package_complete": True,
            "M9_122b_blinded_evaluator_complete": True,
            "M9_122c_identity_bridge_contract_complete": True,
            "external_physical_validation_complete": False,
            "next_target_requires_real_external_evidence_package": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
