"""M9.122a: fail-closed external evidence package schema and validator."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from functools import lru_cache
from hashlib import sha256
import json
import re
from typing import Any, Mapping

from .calibration_holdout_protocol import run_calibration_holdout_protocol

SCHEMA = "openwave.m9.external-evidence-package.v1"
TARGET_OBSERVABLES = ("strong_decay_width", "electroweak_decay_width")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()


def fingerprint(payload: Any) -> str:
    return sha256(canonical_bytes(payload)).hexdigest()


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def artifact(
    *,
    name: str,
    role: str,
    source: str,
    payload: Mapping[str, Any],
    independent: bool,
    uses_target_observable: bool = False,
    evidence_class: str = "external-observation",
) -> dict[str, Any]:
    material = deepcopy(dict(payload))
    return {
        "name": name,
        "role": role,
        "source": source,
        "payload": material,
        "payload_sha256": fingerprint(material),
        "independent": independent,
        "uses_target_observable": uses_target_observable,
        "evidence_class": evidence_class,
    }


def validate_artifact(value: Any) -> dict[str, Any]:
    record = value if isinstance(value, Mapping) else {}
    digest = record.get("payload_sha256")
    checks = {
        "record_is_mapping": isinstance(value, Mapping),
        "name_present": bool(record.get("name")),
        "role_present": bool(record.get("role")),
        "source_present": bool(record.get("source")),
        "payload_present": isinstance(record.get("payload"), Mapping),
        "digest_is_sha256": isinstance(digest, str) and bool(_SHA256.fullmatch(digest)),
        "digest_matches_payload": isinstance(record.get("payload"), Mapping)
        and digest == fingerprint(record["payload"]),
    }
    return {"passed": all(checks.values()), "checks": checks}


def seal_package(package: Mapping[str, Any]) -> dict[str, Any]:
    result = deepcopy(dict(package))
    result.pop("package_sha256", None)
    result["package_sha256"] = fingerprint(result)
    return result


def validate_identity_bridge(bridge: Any) -> dict[str, Any]:
    record = bridge if isinstance(bridge, Mapping) else {}
    artifact_record = record.get("artifact") if isinstance(record.get("artifact"), Mapping) else {}
    artifact_result = validate_artifact(artifact_record)
    payload = artifact_record.get("payload", {}) if isinstance(artifact_record.get("payload"), Mapping) else {}
    discriminants = payload.get("discriminants", {})
    required = ("gauge_sector", "quantum_numbers", "selection_rule", "symmetry_representation")
    sector_checks = []
    for sector in ("strong", "electroweak"):
        values = discriminants.get(sector, {}) if isinstance(discriminants, Mapping) else {}
        sector_checks.append(all(bool(values.get(key)) for key in required))
    checks = {
        "artifact_valid": artifact_result["passed"],
        "independent": bool(artifact_record.get("independent")),
        "not_label_only": not bool(payload.get("label_only", True)),
        "model_transition_ids_present": all(
            bool(payload.get("model_transition_ids", {}).get(sector))
            for sector in ("strong", "electroweak")
        ),
        "observed_channels_present": all(
            bool(payload.get("observed_channels", {}).get(sector))
            for sector in ("strong", "electroweak")
        ),
        "required_discriminants_present": all(sector_checks),
        "negative_controls_present": bool(payload.get("negative_controls")),
    }
    structural = all(checks.values())
    physical = structural and artifact_record.get("evidence_class") == "external-observation"
    return {
        "passed": structural,
        "physical_identity_ready": physical,
        "checks": checks,
        "artifact": artifact_result,
    }


def validate_external_evidence_package(
    package: Any, *, expected_commitment: str
) -> dict[str, Any]:
    record = package if isinstance(package, Mapping) else {}
    sealed = deepcopy(dict(record))
    supplied_digest = sealed.pop("package_sha256", None)
    committed = _timestamp(record.get("prediction_committed_at"))
    revealed = _timestamp(record.get("evidence_revealed_at"))

    anchor = record.get("anchor", {}) if isinstance(record.get("anchor"), Mapping) else {}
    holdout = record.get("holdout", {}) if isinstance(record.get("holdout"), Mapping) else {}
    anchor_record = anchor.get("artifact") if isinstance(anchor.get("artifact"), Mapping) else {}
    holdout_record = holdout.get("artifact") if isinstance(holdout.get("artifact"), Mapping) else {}
    anchor_artifact = validate_artifact(anchor_record)
    holdout_artifact = validate_artifact(holdout_record)
    identity = validate_identity_bridge(record.get("identity_bridge"))

    anchor_payload = anchor_record.get("payload", {}) if isinstance(anchor_record.get("payload"), Mapping) else {}
    holdout_payload = holdout_record.get("payload", {}) if isinstance(holdout_record.get("payload"), Mapping) else {}
    observations = holdout_payload.get("observations", {}) if isinstance(holdout_payload, Mapping) else {}

    observation_checks = {}
    for observable in TARGET_OBSERVABLES:
        item = observations.get(observable, {}) if isinstance(observations, Mapping) else {}
        observation_checks[observable] = (
            isinstance(item.get("value"), (int, float))
            and isinstance(item.get("uncertainty"), (int, float))
            and item["uncertainty"] > 0
            and item.get("unit") == "s^-1"
        )

    checks = {
        "record_is_mapping": isinstance(package, Mapping),
        "schema_is_current": record.get("schema") == SCHEMA,
        "package_digest_is_sha256": isinstance(supplied_digest, str)
        and bool(_SHA256.fullmatch(supplied_digest)),
        "package_digest_matches": supplied_digest == fingerprint(sealed),
        "prediction_commitment_matches": record.get("prediction_commitment")
        == expected_commitment,
        "commitment_precedes_reveal": committed is not None
        and revealed is not None
        and committed < revealed,
        "anchor_artifact_valid": anchor_artifact["passed"],
        "anchor_is_independent": bool(anchor_record.get("independent")),
        "anchor_excludes_target_observable": not bool(
            anchor_record.get("uses_target_observable")
        ),
        "positive_time_scale": isinstance(anchor_payload.get("seconds_per_model_time"), (int, float))
        and anchor_payload["seconds_per_model_time"] > 0,
        "holdout_artifact_valid": holdout_artifact["passed"],
        "holdout_revealed": bool(holdout_payload.get("revealed")),
        "holdout_not_used_for_fit": not bool(holdout_payload.get("used_for_fit", True)),
        "holdout_observations_complete": all(observation_checks.values()),
        "identity_bridge_structurally_valid": identity["passed"],
        "identity_bridge_is_external": identity["physical_identity_ready"],
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "observation_checks": observation_checks,
        "identity": identity,
        "anchor_artifact": anchor_artifact,
        "holdout_artifact": holdout_artifact,
        "missing": tuple(name for name, ok in checks.items() if not ok),
    }


def incomplete_package_template(protocol: Mapping[str, Any]) -> dict[str, Any]:
    plan = protocol["plan"]
    return seal_package(
        {
            "schema": SCHEMA,
            "package_id": "m9.122-live-external-evidence",
            "prediction_commitment": plan["commitment"],
            "prediction_committed_at": "2026-07-27T18:29:16+00:00",
            "evidence_revealed_at": None,
            "anchor": {"artifact": None},
            "holdout": {"artifact": None},
            "identity_bridge": {"artifact": None},
        }
    )


def synthetic_complete_package(protocol: Mapping[str, Any]) -> dict[str, Any]:
    plan = protocol["plan"]
    prediction = plan["prediction"]
    seconds_per_model_time = 2.5e-9
    observations = {}
    for sector, observable in (
        ("strong", "strong_decay_width"),
        ("electroweak", "electroweak_decay_width"),
    ):
        predicted = prediction[sector]["rate_model_units"] / seconds_per_model_time
        observations[observable] = {
            "value": predicted * 1.01,
            "uncertainty": predicted * 0.02,
            "unit": "s^-1",
        }

    identity_payload = {
        "label_only": False,
        "model_transition_ids": {
            "strong": "m9.121:strong:dominant-response-transition",
            "electroweak": "m9.121:electroweak:dominant-response-transition",
        },
        "observed_channels": {
            "strong": "synthetic:strong-channel",
            "electroweak": "synthetic:electroweak-channel",
        },
        "discriminants": {
            sector: {
                "gauge_sector": sector,
                "quantum_numbers": "synthetic-complete",
                "selection_rule": "synthetic-compatible",
                "symmetry_representation": "synthetic-representation",
            }
            for sector in ("strong", "electroweak")
        },
        "negative_controls": ["synthetic:wrong-sector", "synthetic:wrong-selection-rule"],
    }
    package = {
        "schema": SCHEMA,
        "package_id": "m9.122-synthetic-fixture",
        "prediction_commitment": plan["commitment"],
        "prediction_committed_at": "2026-07-27T18:29:16+00:00",
        "evidence_revealed_at": "2026-07-28T00:00:00+00:00",
        "anchor": {
            "artifact": artifact(
                name="synthetic-independent-time-scale",
                role="independent_external_scale",
                source="synthetic://m9.122/anchor",
                payload={
                    "seconds_per_model_time": seconds_per_model_time,
                    "unit": "seconds_per_model_time",
                },
                independent=True,
                evidence_class="synthetic-fixture",
            )
        },
        "holdout": {
            "artifact": artifact(
                name="synthetic-heldout-observations",
                role="heldout_observation",
                source="synthetic://m9.122/holdout",
                payload={
                    "revealed": True,
                    "used_for_fit": False,
                    "observations": observations,
                },
                independent=True,
                evidence_class="synthetic-fixture",
            )
        },
        "identity_bridge": {
            "artifact": artifact(
                name="synthetic-transition-identity",
                role="independent_identity_bridge",
                source="synthetic://m9.122/identity",
                payload=identity_payload,
                independent=True,
                evidence_class="synthetic-fixture",
            )
        },
    }
    return seal_package(package)


@lru_cache(maxsize=1)
def run_external_evidence_package() -> dict[str, Any]:
    protocol = run_calibration_holdout_protocol()
    commitment = protocol["plan"]["commitment"]
    live = incomplete_package_template(protocol)
    synthetic = synthetic_complete_package(protocol)

    live_validation = validate_external_evidence_package(
        live, expected_commitment=commitment
    )
    synthetic_validation = validate_external_evidence_package(
        synthetic, expected_commitment=commitment
    )

    synthetic_structural_pass = all(
        value
        for key, value in synthetic_validation["checks"].items()
        if key != "identity_bridge_is_external"
    )

    tampered = deepcopy(synthetic)
    tampered["holdout"]["artifact"]["payload"]["observations"][
        "strong_decay_width"
    ]["value"] *= 2
    reversed_order = deepcopy(synthetic)
    reversed_order["evidence_revealed_at"] = "2026-07-26T00:00:00+00:00"

    payload = {
        "schema": "openwave.m9.external-evidence-package-study.v1",
        "task": "M9.122a",
        "live_template": live,
        "live_validation": live_validation,
        "synthetic_fixture": synthetic,
        "synthetic_validation": synthetic_validation,
        "claim_boundary": {
            "synthetic_fixture_is_external_evidence": False,
            "schema_construction_is_evidence_ingestion": False,
            "artifact_digest_is_source_authenticity": False,
            "structural_identity_contract_is_observed_identity": False,
        },
    }
    acceptance = {
        "M9_121_commitment_is_preserved": protocol["passed"]
        and live["prediction_commitment"] == commitment,
        "live_package_remains_blocked_without_external_inputs": not live_validation[
            "passed"
        ],
        "synthetic_fixture_exercises_complete_structure": synthetic_structural_pass,
        "synthetic_fixture_is_not_physical_identity": not synthetic_validation[
            "identity"
        ]["physical_identity_ready"],
        "payload_tampering_is_rejected": not validate_external_evidence_package(
            tampered, expected_commitment=commitment
        )["passed"],
        "reveal_before_commitment_is_rejected": not validate_external_evidence_package(
            reversed_order, expected_commitment=commitment
        )["passed"],
        "no_external_evidence_claim_is_promoted": not any(
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
            "external_evidence_package_schema_constructed": True,
            "artifact_integrity_and_ordering_checks_constructed": True,
            "real_external_evidence_package_ingested": False,
            "external_physical_evidence_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
