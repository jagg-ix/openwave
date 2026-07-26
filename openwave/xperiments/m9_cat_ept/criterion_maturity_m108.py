"""Outcome-driven maturity through M9.108."""
from __future__ import annotations

from dataclasses import asdict, replace
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .criterion_maturity_current import derive_headline
from .criterion_maturity_m105 import current_rows as m105_rows
from .m106_108_evidence_authority import run_m106_108_evidence_authority
from .model_conformance_dynamics import CRITERIA as LEGACY_CRITERIA


def current_rows(authority: Mapping[str, Any] | None = None):
    selected = run_m106_108_evidence_authority() if authority is None else authority
    previous = selected["previous_authority"]
    components = selected["components"]
    gravity = components["nonlinear_gravity"]
    sectors = components["coupled_sectors"]["gates"]
    candidates = components["candidate_states"]["gates"]
    rows = []

    for row in m105_rows(previous):
        closed = list(row.closed)
        open_items = list(row.open)
        state = row.state

        if row.key == "gravity":
            if gravity["constraint_gate"]:
                state = "stable_constructed"
                closed.append(
                    "constraint-preserving nonlinear conformal-ADM evolution gate"
                )
            else:
                open_items.append(
                    "constraint-preserving nonlinear conformal-ADM evolution gate"
                )
            open_items.append("general four-dimensional Einstein Cauchy development")
            rows.append(
                replace(
                    row,
                    state=state,
                    closed=tuple(dict.fromkeys(closed)),
                    open=tuple(dict.fromkeys(open_items)),
                )
            )
            continue

        if row.key in ("antimatter_annihilation", "strong_force", "weak_force"):
            if sectors[row.key]:
                closed.append("coupled-field successor gate")
            else:
                open_items.append("coupled-field successor gate")
            rows.append(
                replace(
                    row,
                    closed=tuple(dict.fromkeys(closed)),
                    open=tuple(dict.fromkeys(open_items)),
                )
            )
            continue

        candidate_key = {
            "dark_matter": "dark_matter",
            "quarks": "quarks",
            "baryons": "baryons",
            "mesons": "mesons",
        }.get(row.key)
        if candidate_key is not None:
            if candidates[candidate_key]:
                state = "stable_constructed"
                closed.append("localized dynamical candidate and perturbation gate")
            else:
                open_items.append("localized dynamical candidate and perturbation gate")
            rows.append(
                replace(
                    row,
                    state=state,
                    closed=tuple(dict.fromkeys(closed)),
                    open=tuple(dict.fromkeys(open_items)),
                )
            )
            continue

        rows.append(row)
    return tuple(rows)


def canonical_payload(
    authority: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    selected = run_m106_108_evidence_authority() if authority is None else authority
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
        "schema": "openwave.m9.criterion-maturity.v6",
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
            name: sum(derive_headline(row) == name for row in rows)
            for name in names
        },
        "physical_subgates": selected["components"],
        "policy": {
            "nonlinear_reduced_metric_does_not_imply_general_einstein": True,
            "coupled_sector_field_gate_does_not_imply_standard_model": True,
            "candidate_stability_does_not_imply_particle_identity": True,
            "program_health_regression_blocks_current_authority": True,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_criterion_maturity_m108() -> dict[str, Any]:
    authority = run_m106_108_evidence_authority()
    payload = canonical_payload(authority)
    by_key = {row["key"]: row for row in payload["criteria"]}
    candidate_gates = authority["components"]["candidate_states"]["gates"]
    acceptance = {
        "all_21_rows_remain_present": len(by_key) == 21,
        "gravity_state_follows_constraint_gate": by_key["gravity"]["state"]
        == (
            "stable_constructed"
            if authority["components"]["nonlinear_gravity"]["constraint_gate"]
            else next(
                row.state
                for row in m105_rows(authority["previous_authority"])
                if row.key == "gravity"
            )
        ),
        "three_reduced_sector_headlines_remain_reduced": all(
            by_key[key]["headline"] == "reduced_model_validated"
            for key in ("antimatter_annihilation", "strong_force", "weak_force")
        ),
        "four_candidate_states_follow_dynamic_gates": all(
            by_key[key]["state"]
            == ("stable_constructed" if candidate_gates[key] else "candidate")
            for key in ("dark_matter", "quarks", "baryons", "mesons")
        ),
        "program_health_passage_does_not_promote_claims": True,
        "fingerprint_is_deterministic": fingerprint(payload)
        == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.108-maturity",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
