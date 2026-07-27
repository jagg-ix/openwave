import json

from openwave.xperiments.m9_cat_ept.calibration_holdout_protocol import (
    evaluate_plan,
    run_calibration_holdout_protocol,
)
from openwave.xperiments.m9_cat_ept.physical_promotion_gate import (
    EXTERNAL_REQUIREMENTS,
    evaluate_relations,
    run_physical_promotion_gate,
)


def test_calibration_protocol_rejects_target_leakage_and_tampering() -> None:
    result = run_calibration_holdout_protocol()
    plan = result["plan"]

    leaked = json.loads(json.dumps(plan))
    leaked["anchor"]["independent"] = True
    leaked["anchor"]["value"] = 1.0
    leaked["anchor"]["uses_target_observable"] = True
    leaked["holdout"]["revealed"] = True
    assert evaluate_plan(leaked)["target_leakage"]
    assert not evaluate_plan(leaked)["external_validation_ready"]

    tampered = json.loads(json.dumps(plan))
    tampered["prediction"]["strong"]["rate_model_units"] *= 1.01
    assert not evaluate_plan(tampered)["commitment_matches"]


def test_calibration_protocol_remains_in_model_units() -> None:
    result = run_calibration_holdout_protocol()
    prediction = result["plan"]["prediction"]
    assert result["passed"]
    assert prediction["physical_scale"] is None
    assert prediction["physical_units"] is None
    assert not result["decision"]["independent_physical_anchor_supplied"]
    assert not result["decision"]["external_validation_complete"]


def test_external_promotion_requires_every_relation() -> None:
    complete = set(EXTERNAL_REQUIREMENTS)
    assert evaluate_relations(complete, EXTERNAL_REQUIREMENTS)["passed"]
    for requirement in EXTERNAL_REQUIREMENTS:
        assert not evaluate_relations(
            complete - {requirement}, EXTERNAL_REQUIREMENTS
        )["passed"]


def test_current_state_passes_internal_but_not_external_promotion() -> None:
    result = run_physical_promotion_gate()
    assert result["passed"]
    assert result["internal_evaluation"]["passed"]
    assert not result["external_evaluation"]["passed"]
    assert result["decision"]["physical_promotion_gate_is_fail_closed"]
    assert not result["decision"]["external_physical_promotion_allowed"]
    assert not any(result["claim_boundary"].values())
