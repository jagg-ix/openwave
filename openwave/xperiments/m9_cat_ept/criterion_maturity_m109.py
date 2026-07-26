"""Outcome-driven maturity through M9.109 Newton-G clock anchoring."""
from __future__ import annotations

from dataclasses import asdict, replace
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity_current import derive_headline
from .criterion_maturity_m108 import current_rows as m108_rows
from .m109_evidence_authority import run_m109_evidence_authority
from .model_conformance_dynamics import CRITERIA as LEGACY_CRITERIA


def current_rows(authority: Mapping[str, Any] | None = None):
    selected = run_m109_evidence_authority() if authority is None else authority
    rows = []
    anchor = selected["components"]["universal_anchor"]
    for row in m108_rows(selected["previous_authority"]):
        closed = list(row.closed)
        open_items = list(row.open)
        calibration = row.calibration
        prediction = row.prediction
        if row.key == "gravity":
            closed.extend(
                (
                    "Newton G canonicalized as derived rather than primitive",
                    "mass, clock-frequency and inference-width G maps reconciled",
                    "species-specific particle-clock universality rejected",
                )
            )
            if anchor["independent_anchor_ready"]:
                calibration = "calibrated"
                closed.append("independent universal gravity anchor")
            else:
                open_items.append("independent universal Planck-scale gravity anchor")
            if anchor["withheld_G_prediction_executed"]:
                prediction = "external_validated"
                closed.append("withheld Newton-G prediction")
            else:
                open_items.append("withheld Newton-G prediction")
            rows.append(
                replace(
                    row,
                    calibration=calibration,
                    prediction=prediction,
                    closed=tuple(dict.fromkeys(closed)),
                    open=tuple(dict.fromkeys(open_items)),
                )
            )
            continue
        if row.key in ("de_broglie_clock", "electron_rest_energy"):
            closed.append(
                "Compton anchor removes the free internal clock frequency once mass is fixed"
            )
            open_items.append("independent derivation or measurement of the mass value")
            rows.append(
                replace(
                    row,
                    closed=tuple(dict.fromkeys(closed)),
                    open=tuple(dict.fromkeys(open_items)),
                )
            )
            continue
        rows.append(row)
    return tuple(rows)


def canonical_payload(authority: Mapping[str, Any] | None = None) -> dict[str, Any]:
    selected = run_m109_evidence_authority() if authority is None else authority
    rows = current_rows(selected)
    legacy = {row.key: row.status for row in LEGACY_CRITERIA}
    names = (
        "validated_in_scope",
        "conditional_validated",
        "reduced_model_validated",
        "calibration_pending",
        "candidate",
        "negative",
    )
    return {
        "schema": "openwave.m9.criterion-maturity.v7",
        "physlib_head": selected["physlib_head"],
        "zil_head": selected["zil_head"],
        "criteria": [
            {
                **asdict(row),
                "headline": derive_headline(row),
                "legacy_status": legacy[row.key],
            }
            for row in rows
        ],
        "headline_counts": {
            name: sum(derive_headline(row) == name for row in rows) for name in names
        },
        "physical_subgates": selected["components"],
        "policy": {
            "derived_G_does_not_imply_predicted_G": True,
            "clock_anchor_does_not_derive_mass_value": True,
            "particle_clock_does_not_define_universal_G": True,
            "gravity_calibration_requires_independent_universal_anchor": True,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_criterion_maturity_m109() -> dict[str, Any]:
    authority = run_m109_evidence_authority()
    payload = canonical_payload(authority)
    by_key = {row["key"]: row for row in payload["criteria"]}
    anchor = authority["components"]["universal_anchor"]
    acceptance = {
        "all_21_rows_remain_present": len(by_key) == 21,
        "gravity_records_G_as_derived": any(
            "derived rather than primitive" in item for item in by_key["gravity"]["closed"]
        ),
        "gravity_calibration_follows_universal_anchor": (
            by_key["gravity"]["calibration"] == "calibrated"
        )
        == bool(anchor["independent_anchor_ready"]),
        "unexecuted_G_prediction_does_not_advance_prediction_axis": (
            by_key["gravity"]["prediction"] != "external_validated"
        )
        or bool(anchor["withheld_G_prediction_executed"]),
        "clock_anchor_does_not_promote_mass_identity": by_key["electron_rest_energy"][
            "identity"
        ]
        == "open",
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.109-maturity",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
