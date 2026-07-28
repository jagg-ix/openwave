"""M9.130c: leave-one-carrier-out generalization without per-dataset refitting."""
from __future__ import annotations

from typing import Any, Mapping, Sequence


def evaluate_generalization(carriers: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    folds = []
    for heldout in carriers:
        training = [item for item in carriers if item["carrier_id"] != heldout["carrier_id"]]
        frozen_threshold = max(float(item["normalized_error"]) for item in training) * 1.25
        passed = float(heldout["normalized_error"]) <= frozen_threshold
        folds.append({
            "heldout_carrier": heldout["carrier_id"],
            "training_count": len(training),
            "frozen_threshold": frozen_threshold,
            "heldout_error": float(heldout["normalized_error"]),
            "passed": passed,
        })
    return {
        "folds": tuple(folds),
        "all_folds_pass": all(fold["passed"] for fold in folds),
        "no_per_carrier_refit": True,
        "carrier_count": len(carriers),
    }


def run_cross_carrier_generalization() -> dict[str, Any]:
    carriers = (
        {"carrier_id": "moreva-conditioning", "domain": "relational-conditioning", "normalized_error": 0.42},
        {"carrier_id": "moreva-multitime", "domain": "relational-multitime", "normalized_error": 0.51},
        {"carrier_id": "quantum-dot-relaxation", "domain": "binary-relaxation", "normalized_error": 0.47},
        {"carrier_id": "superconducting-qubit", "domain": "open-system-clock", "normalized_error": 0.56},
    )
    result = evaluate_generalization(carriers)
    acceptance = {
        "multiple_physical_carriers_are_represented": result["carrier_count"] >= 4,
        "every_carrier_is_held_out_once": len(result["folds"]) == len(carriers),
        "no_per_carrier_refit": result["no_per_carrier_refit"],
        "fixture_generalizes": result["all_folds_pass"],
    }
    return {
        "schema": "openwave.m9.cross-carrier-generalization.v1",
        "task": "M9.130c",
        "carriers": carriers,
        **result,
        "claim_boundary": {
            "synthetic_cross_carrier_fixture_is_experimental_generalization": False,
            "threshold_rule_is_parameter_free_physics": False,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "generalization_protocol_ready": True,
            "real_cross_carrier_result_available": False,
            "physical_promotion_allowed": False,
        },
    }
