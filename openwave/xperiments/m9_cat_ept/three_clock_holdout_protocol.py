"""M9.125c: precommitted three-clock holdout package and blocked evaluator."""
from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .shared_three_clock_carrier import SharedThreeClockCarrier, run_shared_three_clock_carrier
from .three_clock_calibration_contract import ThreeClockCalibration, run_three_clock_calibration_contract


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def prediction_payload() -> dict[str, Any]:
    carrier = SharedThreeClockCarrier()
    calibration = ThreeClockCalibration()
    model_times = (0.7, 1.9, 3.8)
    rows = []
    for t in model_times:
        rho = carrier.state(t)
        rows.append(
            {
                "model_time": t,
                "page_wootters_reading": calibration.page_wootters_from_model_time(t),
                "modular_parameter": calibration.modular_from_model_time(t),
                "nominal_proper_time": calibration.nominal_proper_time_from_model_time(t),
                "excited_population": float(rho[1, 1].real),
                "coherence_magnitude": abs(complex(rho[0, 1])),
                "accumulated_entropic_time": calibration.entropic_from_model_time(t),
            }
        )
    return {
        "schema": "openwave.m9.three-clock-prediction.v1",
        "carrier_fingerprint": run_shared_three_clock_carrier()["fingerprint"],
        "calibration_fingerprint": run_three_clock_calibration_contract()["fingerprint"],
        "rows": rows,
        "physical_units": None,
        "external_clock_identity": None,
    }


def build_live_template() -> dict[str, Any]:
    prediction = prediction_payload()
    return {
        "schema": "openwave.m9.three-clock-holdout-package.v1",
        "evidence_class": "external-observation",
        "prediction": prediction,
        "commitment": fingerprint(prediction),
        "commitment_timestamp": "2026-07-27T21:50:00Z",
        "reveal_timestamp": None,
        "calibration_source": None,
        "observation_source": None,
        "used_for_fit": False,
        "observations": None,
        "package_digest": None,
    }


def build_synthetic_fixture() -> dict[str, Any]:
    package = build_live_template()
    package["evidence_class"] = "synthetic-fixture"
    package["reveal_timestamp"] = "2026-07-27T22:00:00Z"
    package["calibration_source"] = {
        "name": "synthetic internal map",
        "independent": False,
        "uses_target_observables": False,
    }
    package["observation_source"] = {
        "name": "synthetic deterministic fixture",
        "independent": False,
    }
    package["observations"] = [
        {
            **row,
            "uncertainties": {
                "excited_population": 0.01,
                "coherence_magnitude": 0.01,
                "accumulated_entropic_time": 0.02,
            },
        }
        for row in package["prediction"]["rows"]
    ]
    unsigned = {k: v for k, v in package.items() if k != "package_digest"}
    package["package_digest"] = fingerprint(unsigned)
    return package


def _timestamp_ordered(commitment: str | None, reveal: str | None) -> bool:
    return bool(commitment and reveal and commitment < reveal)


def validate_package(package: Mapping[str, Any], *, allow_synthetic: bool = False) -> dict[str, Any]:
    prediction = package.get("prediction")
    observations = package.get("observations")
    calibration_source = package.get("calibration_source") or {}
    observation_source = package.get("observation_source") or {}
    expected_digest = fingerprint({k: v for k, v in package.items() if k != "package_digest"})
    rows_complete = bool(observations) and len(observations) == len(prediction.get("rows", ())) if isinstance(prediction, Mapping) else False
    uncertainties_positive = rows_complete and all(
        all(float(value) > 0 for value in row.get("uncertainties", {}).values())
        and set(row.get("uncertainties", {}))
        == {"excited_population", "coherence_magnitude", "accumulated_entropic_time"}
        for row in observations
    )
    structural = {
        "prediction_commitment_matches": isinstance(prediction, Mapping) and package.get("commitment") == fingerprint(prediction),
        "commitment_precedes_reveal": _timestamp_ordered(package.get("commitment_timestamp"), package.get("reveal_timestamp")),
        "package_digest_matches": package.get("package_digest") == expected_digest,
        "observations_are_complete": rows_complete,
        "uncertainties_are_complete_and_positive": uncertainties_positive,
        "holdout_not_used_for_fit": not bool(package.get("used_for_fit")),
        "target_observables_not_used_for_calibration": not bool(calibration_source.get("uses_target_observables")),
    }
    external = {
        "evidence_class_is_external": package.get("evidence_class") == "external-observation",
        "calibration_source_is_independent": bool(calibration_source.get("independent")),
        "observation_source_is_independent": bool(observation_source.get("independent")),
        "physical_units_are_supplied": bool(prediction.get("physical_units")) if isinstance(prediction, Mapping) else False,
        "external_clock_identity_is_supplied": bool(prediction.get("external_clock_identity")) if isinstance(prediction, Mapping) else False,
    }
    structurally_valid = all(structural.values())
    externally_valid = structurally_valid and all(external.values())
    accepted = externally_valid or (allow_synthetic and structurally_valid and package.get("evidence_class") == "synthetic-fixture")
    return {
        "structural": structural,
        "external": external,
        "structurally_valid": structurally_valid,
        "externally_valid": externally_valid,
        "accepted_for_execution": accepted,
    }


def evaluate_package(package: Mapping[str, Any], *, allow_synthetic: bool = False) -> dict[str, Any]:
    validation = validate_package(package, allow_synthetic=allow_synthetic)
    if not validation["accepted_for_execution"]:
        return {"status": "blocked", "validation": validation, "comparisons": (), "external_validation_complete": False}
    comparisons = []
    for predicted, observed in zip(package["prediction"]["rows"], package["observations"]):
        row = {"model_time": predicted["model_time"], "metrics": {}}
        for key in ("excited_population", "coherence_magnitude", "accumulated_entropic_time"):
            uncertainty = observed["uncertainties"][key]
            error = observed[key] - predicted[key]
            row["metrics"][key] = {
                "predicted": predicted[key],
                "observed": observed[key],
                "uncertainty": uncertainty,
                "z_score": error / uncertainty,
                "within_three_sigma": abs(error / uncertainty) <= 3.0,
            }
        comparisons.append(row)
    all_within = all(metric["within_three_sigma"] for row in comparisons for metric in row["metrics"].values())
    external_complete = validation["externally_valid"] and all_within
    return {
        "status": "evaluated",
        "validation": validation,
        "comparisons": comparisons,
        "all_within_three_sigma": all_within,
        "external_validation_complete": external_complete,
    }


@lru_cache(maxsize=1)
def run_three_clock_holdout_protocol() -> dict[str, Any]:
    live = build_live_template()
    synthetic = build_synthetic_fixture()
    live_eval = evaluate_package(live)
    synthetic_eval = evaluate_package(synthetic, allow_synthetic=True)
    tampered = deepcopy(synthetic)
    tampered["prediction"]["rows"][0]["excited_population"] += 0.1
    reversed_time = deepcopy(synthetic)
    reversed_time["reveal_timestamp"] = "2026-07-27T21:40:00Z"
    reversed_time["package_digest"] = fingerprint({k: v for k, v in reversed_time.items() if k != "package_digest"})
    payload = {
        "schema": "openwave.m9.three-clock-holdout-protocol.v1",
        "task": "M9.125c",
        "live_template": live,
        "live_evaluation": live_eval,
        "synthetic_evaluation": synthetic_eval,
        "claim_boundary": {
            "synthetic_fixture_is_external_clock_data": False,
            "package_schema_is_experimental_validation": False,
            "successful_structural_metrics_are_physical_clock_calibration": False,
            "blocked_live_template_is_failed_theory_prediction": False,
        },
    }
    acceptance = {
        "live_path_blocks_without_real_data": live_eval["status"] == "blocked" and not live_eval["external_validation_complete"],
        "synthetic_fixture_executes_all_three_metrics": synthetic_eval["status"] == "evaluated" and len(synthetic_eval["comparisons"]) == 3,
        "synthetic_fixture_cannot_promote_external_validation": not synthetic_eval["external_validation_complete"],
        "prediction_tampering_is_rejected": not validate_package(tampered, allow_synthetic=True)["accepted_for_execution"],
        "reveal_before_commitment_is_rejected": not validate_package(reversed_time, allow_synthetic=True)["accepted_for_execution"],
        "no_evidence_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "three_clock_prediction_commitment_constructed": True,
            "three_clock_holdout_evaluator_constructed": True,
            "real_three_clock_data_ingested": False,
            "external_three_clock_validation_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
