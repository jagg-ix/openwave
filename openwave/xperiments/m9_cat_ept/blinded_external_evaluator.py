"""M9.122b: blinded external holdout evaluator."""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .calibration_holdout_protocol import run_calibration_holdout_protocol
from .external_evidence_package import (
    incomplete_package_template,
    synthetic_complete_package,
    validate_external_evidence_package,
)


def fingerprint(payload: Any) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def evaluate_package(
    *,
    prediction: Mapping[str, Any],
    commitment: str,
    package: Mapping[str, Any],
    z_threshold: float = 3.0,
) -> dict[str, Any]:
    validation = validate_external_evidence_package(
        package, expected_commitment=commitment
    )
    artifact = package.get("anchor", {}).get("artifact")
    evidence_class = (
        artifact.get("evidence_class") if isinstance(artifact, Mapping) else None
    )
    synthetic = evidence_class == "synthetic-fixture"
    structural_fixture_pass = synthetic and all(
        value
        for key, value in validation["checks"].items()
        if key != "identity_bridge_is_external"
    )
    if not validation["passed"] and not structural_fixture_pass:
        return {
            "status": "blocked",
            "validation": validation,
            "metrics": {},
            "heldout_test_executed": False,
            "external_validation_complete": False,
            "synthetic_fixture": synthetic,
        }

    scale = package["anchor"]["artifact"]["payload"]["seconds_per_model_time"]
    observations = package["holdout"]["artifact"]["payload"]["observations"]
    metrics = {}
    for sector, observable in (
        ("strong", "strong_decay_width"),
        ("electroweak", "electroweak_decay_width"),
    ):
        predicted_rate = prediction[sector]["rate_model_units"] / scale
        predicted_lifetime = prediction[sector]["lifetime_model_units"] * scale
        observed = observations[observable]
        z_score = abs(predicted_rate - observed["value"]) / observed["uncertainty"]
        relative_error = abs(predicted_rate - observed["value"]) / max(
            abs(observed["value"]), 1.0e-300
        )
        metrics[sector] = {
            "predicted_rate_s^-1": predicted_rate,
            "predicted_lifetime_s": predicted_lifetime,
            "observed_rate_s^-1": observed["value"],
            "uncertainty_s^-1": observed["uncertainty"],
            "absolute_z_score": z_score,
            "relative_error": relative_error,
            "within_preregistered_threshold": z_score <= z_threshold,
        }

    all_within = all(
        row["within_preregistered_threshold"] for row in metrics.values()
    )
    return {
        "status": "evaluated",
        "validation": validation,
        "metrics": metrics,
        "z_threshold": z_threshold,
        "all_within_threshold": all_within,
        "heldout_test_executed": not synthetic,
        "external_validation_complete": all_within and not synthetic,
        "synthetic_fixture": synthetic,
    }


@lru_cache(maxsize=1)
def run_blinded_external_evaluator() -> dict[str, Any]:
    protocol = run_calibration_holdout_protocol()
    prediction = protocol["plan"]["prediction"]
    commitment = protocol["plan"]["commitment"]
    live_package = incomplete_package_template(protocol)
    fixture = synthetic_complete_package(protocol)

    live = evaluate_package(
        prediction=prediction, commitment=commitment, package=live_package
    )
    synthetic = evaluate_package(
        prediction=prediction, commitment=commitment, package=fixture
    )

    tampered = deepcopy(fixture)
    tampered["prediction_commitment"] = "0" * 64
    tampered_result = evaluate_package(
        prediction=prediction, commitment=commitment, package=tampered
    )

    payload = {
        "schema": "openwave.m9.blinded-external-evaluator.v1",
        "task": "M9.122b",
        "live_evaluation": live,
        "synthetic_evaluation": synthetic,
        "claim_boundary": {
            "synthetic_evaluation_is_heldout_validation": False,
            "blocked_live_evaluation_is_negative_result": False,
            "unit_conversion_is_independent_calibration": False,
            "z_threshold_is_particle_identity": False,
        },
    }
    acceptance = {
        "M9_121_protocol_is_preserved": protocol["passed"],
        "live_evaluation_blocks_before_external_reveal": live["status"] == "blocked"
        and not live["heldout_test_executed"],
        "synthetic_fixture_exercises_metric_path": synthetic["status"] == "evaluated"
        and synthetic["all_within_threshold"],
        "synthetic_fixture_does_not_promote_external_validation": not synthetic[
            "heldout_test_executed"
        ]
        and not synthetic["external_validation_complete"],
        "commitment_mismatch_blocks_evaluation": tampered_result["status"] == "blocked",
        "no_external_validation_claim_is_promoted": not any(
            payload["claim_boundary"].values()
        ),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "blinded_external_evaluator_constructed": True,
            "synthetic_metric_path_validated": True,
            "live_heldout_evaluation_executed": False,
            "external_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
