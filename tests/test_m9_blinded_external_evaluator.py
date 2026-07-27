from copy import deepcopy

from openwave.xperiments.m9_cat_ept.blinded_external_evaluator import (
    evaluate_package,
    run_blinded_external_evaluator,
)
from openwave.xperiments.m9_cat_ept.calibration_holdout_protocol import (
    run_calibration_holdout_protocol,
)
from openwave.xperiments.m9_cat_ept.external_evidence_package import (
    fingerprint,
    incomplete_package_template,
    synthetic_complete_package,
    validate_identity_bridge,
)
from openwave.xperiments.m9_cat_ept.transition_identity_bridge import (
    run_transition_identity_bridge_contract,
    synthetic_bridge,
)


def test_blinded_evaluator_blocks_live_and_exercises_synthetic_metrics() -> None:
    protocol = run_calibration_holdout_protocol()
    prediction = protocol["plan"]["prediction"]
    commitment = protocol["plan"]["commitment"]

    live = evaluate_package(
        prediction=prediction,
        commitment=commitment,
        package=incomplete_package_template(protocol),
    )
    fixture = evaluate_package(
        prediction=prediction,
        commitment=commitment,
        package=synthetic_complete_package(protocol),
    )
    assert live["status"] == "blocked"
    assert fixture["status"] == "evaluated"
    assert fixture["all_within_threshold"]
    assert fixture["synthetic_fixture"]
    assert not fixture["heldout_test_executed"]
    assert not fixture["external_validation_complete"]


def test_identity_contract_rejects_labels() -> None:
    bridge = synthetic_bridge()
    assert validate_identity_bridge(bridge)["passed"]

    label_only = deepcopy(bridge)
    label_only["artifact"]["payload"]["label_only"] = True
    label_only["artifact"]["payload_sha256"] = fingerprint(
        label_only["artifact"]["payload"]
    )
    assert not validate_identity_bridge(label_only)["passed"]


def test_evaluator_and_identity_studies_pass_without_external_promotion() -> None:
    evaluator = run_blinded_external_evaluator()
    identity = run_transition_identity_bridge_contract()
    assert evaluator["passed"]
    assert identity["passed"]
    assert not evaluator["decision"]["live_heldout_evaluation_executed"]
    assert not evaluator["decision"]["external_validation_complete"]
    assert not identity["decision"]["physical_transition_identity_established"]
