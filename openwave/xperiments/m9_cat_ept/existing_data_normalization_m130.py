"""M9.130a: canonical normalization for existing relational-clock and relaxation data."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

REQUIRED_ROW_FIELDS = ("observation_id", "dataset_id", "domain", "x", "y", "uncertainty", "units")
SUPPORTED_DOMAINS = ("relational-conditioning", "binary-relaxation")


def _fingerprint(payload: Any) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def normalize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    normalized = []
    errors = []
    seen = set()
    for index, row in enumerate(rows):
        missing = tuple(field for field in REQUIRED_ROW_FIELDS if field not in row)
        if missing:
            errors.append({"row": index, "error": "missing-fields", "fields": missing})
            continue
        observation_id = str(row["observation_id"])
        if observation_id in seen:
            errors.append({"row": index, "error": "duplicate-observation-id", "id": observation_id})
            continue
        seen.add(observation_id)
        domain = str(row["domain"])
        uncertainty = float(row["uncertainty"])
        if domain not in SUPPORTED_DOMAINS:
            errors.append({"row": index, "error": "unsupported-domain", "domain": domain})
            continue
        if uncertainty <= 0:
            errors.append({"row": index, "error": "nonpositive-uncertainty"})
            continue
        normalized.append({
            "observation_id": observation_id,
            "dataset_id": str(row["dataset_id"]),
            "domain": domain,
            "x": float(row["x"]),
            "y": float(row["y"]),
            "uncertainty": uncertainty,
            "units": dict(row["units"]),
            "split": str(row.get("split", "unassigned")),
        })
    payload = {
        "schema": "openwave.m9.existing-data-normalization.v1",
        "rows": tuple(normalized),
        "errors": tuple(errors),
    }
    return {**payload, "valid": bool(normalized) and not errors, "fingerprint": _fingerprint(payload)}


def run_existing_data_normalization() -> dict[str, Any]:
    fixture = (
        {"observation_id": "pw-0", "dataset_id": "moreva-control", "domain": "relational-conditioning", "x": 0, "y": 0.99, "uncertainty": 0.01, "units": {"x": "clock-index", "y": "fidelity"}, "split": "holdout"},
        {"observation_id": "relax-0", "dataset_id": "dot-control", "domain": "binary-relaxation", "x": 0.0, "y": 0.82, "uncertainty": 0.02, "units": {"x": "s", "y": "occupation"}, "split": "calibration"},
    )
    result = normalize_rows(fixture)
    acceptance = {
        "fixture_normalizes": result["valid"],
        "domains_are_preserved": {row["domain"] for row in result["rows"]} == set(SUPPORTED_DOMAINS),
        "uncertainties_are_positive": all(row["uncertainty"] > 0 for row in result["rows"]),
        "fingerprint_is_deterministic": result["fingerprint"] == normalize_rows(fixture)["fingerprint"],
    }
    return {**result, "task": "M9.130a", "acceptance": acceptance, "passed": all(acceptance.values())}
