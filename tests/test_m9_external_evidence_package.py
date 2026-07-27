from copy import deepcopy

from openwave.xperiments.m9_cat_ept.calibration_holdout_protocol import (
    run_calibration_holdout_protocol,
)
from openwave.xperiments.m9_cat_ept.external_evidence_package import (
    incomplete_package_template,
    run_external_evidence_package,
    synthetic_complete_package,
    validate_external_evidence_package,
)


def test_live_package_is_blocked_and_synthetic_fixture_is_nonphysical() -> None:
    protocol = run_calibration_holdout_protocol()
    commitment = protocol["plan"]["commitment"]
    live = validate_external_evidence_package(
        incomplete_package_template(protocol), expected_commitment=commitment
    )
    fixture = validate_external_evidence_package(
        synthetic_complete_package(protocol), expected_commitment=commitment
    )

    assert not live["passed"]
    assert not fixture["passed"]
    assert fixture["checks"]["identity_bridge_structurally_valid"]
    assert not fixture["identity"]["physical_identity_ready"]


def test_package_tampering_and_reveal_order_are_rejected() -> None:
    protocol = run_calibration_holdout_protocol()
    commitment = protocol["plan"]["commitment"]
    package = synthetic_complete_package(protocol)

    tampered = deepcopy(package)
    tampered["anchor"]["artifact"]["payload"]["seconds_per_model_time"] *= 2
    assert not validate_external_evidence_package(
        tampered, expected_commitment=commitment
    )["passed"]

    reversed_order = deepcopy(package)
    reversed_order["evidence_revealed_at"] = "2026-07-26T00:00:00+00:00"
    assert not validate_external_evidence_package(
        reversed_order, expected_commitment=commitment
    )["passed"]


def test_external_evidence_package_study_passes_without_ingestion_claim() -> None:
    result = run_external_evidence_package()
    assert result["passed"]
    assert result["decision"]["external_evidence_package_schema_constructed"]
    assert not result["decision"]["real_external_evidence_package_ingested"]
    assert not result["decision"]["external_physical_evidence_complete"]
