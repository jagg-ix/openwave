from __future__ import annotations
from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .gauge_sector_open_decay import run_gauge_sector_open_decay


@dataclass(frozen=True)
class CalibrationHoldoutConfig:
    protocol_id: str = "m9.121-blind-calibration-v1"
    target_observables: tuple[str, ...] = (
        "strong_decay_width",
        "electroweak_decay_width",
    )
    required_anchor_role: str = "independent_external_scale"
    prediction_unit: str = "model_time_inverse"


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def prediction_payload(decay: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": "openwave.m9.blind-prediction-payload.v1",
        "strong": {
            "gap_model_units": decay["strong"]["omega_model_units"],
            "rate_model_units": decay["strong"]["gamma_model_units"],
            "lifetime_model_units": decay["strong"]["lifetime_model_units"],
        },
        "electroweak": {
            "gap_model_units": decay["electroweak"]["omega_model_units"],
            "rate_model_units": decay["electroweak"]["gamma_model_units"],
            "lifetime_model_units": decay["electroweak"]["lifetime_model_units"],
        },
        "physical_scale": None,
        "physical_units": None,
    }


def evaluate_plan(plan: Mapping[str, Any]) -> dict[str, Any]:
    anchor = plan["anchor"]
    holdout = plan["holdout"]
    anchor_ready = bool(anchor.get("independent")) and anchor.get("value") is not None
    target_leakage = bool(anchor.get("uses_target_observable")) or bool(
        holdout.get("used_for_fit")
    )
    commitment_matches = fingerprint(plan["prediction"]) == plan["commitment"]
    external_ready = (
        anchor_ready
        and not target_leakage
        and commitment_matches
        and bool(holdout.get("revealed"))
    )
    return {
        "anchor_ready": anchor_ready,
        "target_leakage": target_leakage,
        "commitment_matches": commitment_matches,
        "heldout_revealed": bool(holdout.get("revealed")),
        "external_validation_ready": external_ready,
    }


def run_with_decay(decay: Mapping[str, Any]) -> dict[str, Any]:
    cfg = CalibrationHoldoutConfig()
    prediction = prediction_payload(decay)
    commitment = fingerprint(prediction)
    plan = {
        "schema": "openwave.m9.calibration-holdout-plan.v1",
        "protocol": asdict(cfg),
        "prediction": prediction,
        "commitment": commitment,
        "anchor": {
            "name": "independent_physical_scale",
            "role": cfg.required_anchor_role,
            "value": None,
            "unit": None,
            "source": None,
            "independent": False,
            "uses_target_observable": False,
        },
        "holdout": {
            "observables": cfg.target_observables,
            "source": None,
            "used_for_fit": False,
            "revealed": False,
        },
    }
    evaluation = evaluate_plan(plan)
    leaked = json.loads(json.dumps(plan))
    leaked["anchor"]["uses_target_observable"] = True
    leaked["anchor"]["independent"] = True
    leaked["anchor"]["value"] = 1.0
    leaked["holdout"]["revealed"] = True
    missing_commitment = json.loads(json.dumps(plan))
    missing_commitment["commitment"] = "0" * 64
    payload = {
        "schema": "openwave.m9.calibration-holdout-protocol.v1",
        "task": "M9.121b",
        "plan": plan,
        "evaluation": evaluation,
        "claim_boundary": {
            "protocol_construction_is_physical_calibration": False,
            "sealed_prediction_is_external_validation": False,
            "model_unit_rate_is_physical_unit_rate": False,
            "missing_anchor_is_silently_inferred": False,
        },
    }
    acceptance = {
        "M9_121a_decay_authority_passes": bool(decay["passed"]),
        "prediction_commitment_is_deterministic": commitment == fingerprint(prediction),
        "target_observables_are_excluded_from_fit": not evaluation["target_leakage"],
        "missing_external_anchor_blocks_calibration": not evaluation["anchor_ready"]
        and not evaluation["external_validation_ready"],
        "target_leakage_is_rejected": evaluate_plan(leaked)["target_leakage"]
        and not evaluate_plan(leaked)["external_validation_ready"],
        "commitment_tampering_is_rejected": not evaluate_plan(missing_commitment)[
            "commitment_matches"
        ],
        "prediction_remains_in_model_units": prediction["physical_scale"] is None
        and prediction["physical_units"] is None,
        "no_calibration_or_validation_claim_is_promoted": not any(
            payload["claim_boundary"].values()
        ),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "blind_prediction_commitment_constructed": True,
            "holdout_safe_calibration_protocol_constructed": True,
            "independent_physical_anchor_supplied": False,
            "heldout_observation_revealed": False,
            "physical_calibration_complete": False,
            "external_validation_complete": False,
        },
    }


@lru_cache(maxsize=1)
def run_calibration_holdout_protocol() -> dict[str, Any]:
    return run_with_decay(run_gauge_sector_open_decay())


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
