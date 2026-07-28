"""M9.130 authority for existing-data normalization, theorem scoring, and cross-carrier generalization."""
from __future__ import annotations

from .existing_data_normalization_m130 import run_existing_data_normalization
from .existing_data_theorem_evaluators_m130 import run_theorem_specific_evaluators
from .cross_carrier_generalization_m130 import run_cross_carrier_generalization


def run_m130_existing_data_authority() -> dict:
    normalization = run_existing_data_normalization()
    evaluators = run_theorem_specific_evaluators()
    generalization = run_cross_carrier_generalization()
    requirements = {
        "canonical_normalization_ready": normalization["passed"],
        "theorem_specific_evaluators_ready": evaluators["passed"],
        "cross_carrier_protocol_ready": generalization["passed"],
        "real_published_rows_ingested": False,
        "source_digests_verified": False,
        "real_leave_one_carrier_out_result": False,
    }
    internal_ready = all(requirements[name] for name in (
        "canonical_normalization_ready",
        "theorem_specific_evaluators_ready",
        "cross_carrier_protocol_ready",
    ))
    physical_ready = all(requirements.values())
    acceptance = {
        "internal_methodology_ready": internal_ready,
        "physical_promotion_fails_closed": not physical_ready,
        "real_data_blockers_are_explicit": all(not requirements[name] for name in (
            "real_published_rows_ingested",
            "source_digests_verified",
            "real_leave_one_carrier_out_result",
        )),
    }
    return {
        "schema": "openwave.m9.m130-existing-data-authority.v1",
        "task": "M9.130",
        "normalization": normalization,
        "evaluators": evaluators,
        "generalization": generalization,
        "requirements": requirements,
        "internal_ready": internal_ready,
        "physical_ready": physical_ready,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "existing_data_pipeline_executable": True,
            "new_experiment_required_before_ingestion": False,
            "external_validation_complete": False,
        },
    }
