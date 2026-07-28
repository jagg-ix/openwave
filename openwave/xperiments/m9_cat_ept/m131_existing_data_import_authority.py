"""M9.131 composed authority for source integrity, adapters, and leakage-safe publication."""
from __future__ import annotations

from .existing_data_source_manifest_m131 import run_source_manifest_verifier
from .existing_data_adapters_m131 import run_dataset_adapters
from .existing_data_publication_audit_m131 import run_leakage_publication_audit


def run_m131_existing_data_import_authority() -> dict:
    manifest = run_source_manifest_verifier()
    adapters = run_dataset_adapters()
    audit = run_leakage_publication_audit()
    requirements = {
        "source_manifest_ready": manifest["passed"],
        "dataset_adapters_ready": adapters["passed"],
        "leakage_audit_ready": audit["passed"],
        "real_source_artifacts_imported": False,
        "real_digests_verified": False,
        "real_heldout_report_complete": False,
    }
    internal_ready = all(requirements[name] for name in ("source_manifest_ready","dataset_adapters_ready","leakage_audit_ready"))
    physical_ready = all(requirements.values())
    acceptance = {
        "internal_pipeline_ready": internal_ready,
        "physical_gate_fails_closed": not physical_ready,
        "real_data_blockers_are_explicit": all(not requirements[name] for name in ("real_source_artifacts_imported","real_digests_verified","real_heldout_report_complete")),
    }
    return {"schema":"openwave.m9.m131-existing-data-import-authority.v1","task":"M9.131","manifest":manifest,"adapters":adapters,"audit":audit,"requirements":requirements,"internal_ready":internal_ready,"physical_ready":physical_ready,"acceptance":acceptance,"passed":all(acceptance.values()),"decision":{"mergeable_methodology_ready":True,"external_validation_complete":False}}
