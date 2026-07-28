"""M9.131 authority for source manifests and published summary evidence."""
from __future__ import annotations

from .m130_existing_data_authority import run_m130_existing_data_authority
from .published_source_manifests_m131 import run_published_source_manifests
from .published_summary_ingestion_m131 import run_published_summary_ingestion
from .published_summary_evaluators_m131 import run_published_summary_evaluators


def run_m131_published_summary_authority() -> dict:
    previous = run_m130_existing_data_authority()
    manifests = run_published_source_manifests()
    ingestion = run_published_summary_ingestion()
    evaluators = run_published_summary_evaluators()
    requirements = {
        "m130_pipeline_ready": previous["passed"],
        "canonical_publication_manifests_ready": manifests["passed"],
        "published_summary_rows_ingested": ingestion["passed"],
        "summary_level_evaluators_pass": evaluators["passed"],
        "raw_source_file_digests_verified": manifests["raw_source_file_digests_verified"],
        "raw_observation_rows_ingested": ingestion["raw_observation_rows_ingested"],
        "real_raw_leave_one_carrier_out_result": False,
    }
    internal_ready = all(requirements[name] for name in (
        "m130_pipeline_ready",
        "canonical_publication_manifests_ready",
        "published_summary_rows_ingested",
        "summary_level_evaluators_pass",
    ))
    physical_ready = all(requirements.values())
    acceptance = {
        "published_summary_methodology_ready": internal_ready,
        "physical_promotion_fails_closed": not physical_ready,
        "raw_data_blockers_are_explicit": all(not requirements[name] for name in (
            "raw_source_file_digests_verified",
            "raw_observation_rows_ingested",
            "real_raw_leave_one_carrier_out_result",
        )),
    }
    return {
        "schema": "openwave.m9.m131-published-summary-authority.v1",
        "task": "M9.131",
        "previous_authority": previous,
        "manifests": manifests,
        "ingestion": ingestion,
        "evaluators": evaluators,
        "requirements": requirements,
        "internal_ready": internal_ready,
        "physical_ready": physical_ready,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "published_summary_evidence_is_executable": True,
            "raw_data_external_validation_complete": False,
            "new_experiment_required_before_raw_reanalysis": False,
        },
    }
