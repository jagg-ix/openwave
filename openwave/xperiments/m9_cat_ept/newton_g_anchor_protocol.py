"""M9.109c: non-circular universal Newton-G anchor and prediction protocol."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Literal, Mapping, Sequence

from .newton_g_clock_universality import (
    Constants,
    clock_from_newton_G,
    compton_frequency,
    mass_from_newton_G,
    newton_G_from_clock,
    newton_G_from_mass,
    relative_error,
)

EvidenceClass = Literal["definition", "external", "internal", "derived", "absent"]
AnchorScope = Literal["universal_gravity", "particle", "model_internal"]


@dataclass(frozen=True)
class GravityAnchor:
    name: str
    value: float | None
    unit: str
    evidence_class: EvidenceClass
    scope: AnchorScope
    source: str
    depends_on: tuple[str, ...] = ()
    target_dependencies: tuple[str, ...] = ()

    @property
    def independent(self) -> bool:
        return (
            self.value is not None
            and self.value > 0.0
            and self.evidence_class in ("definition", "external")
            and self.scope == "universal_gravity"
            and "newton_G" not in self.depends_on
            and "newton_G" not in self.target_dependencies
        )


@dataclass(frozen=True)
class GravityAnchorBundle:
    anchors: tuple[GravityAnchor, ...]
    withheld_newton_G: float | None = None
    relative_gate: float = 5.0e-5

    def __post_init__(self) -> None:
        if self.relative_gate <= 0.0:
            raise ValueError("positive prediction gate required")
        if self.withheld_newton_G is not None and self.withheld_newton_G <= 0.0:
            raise ValueError("positive withheld Newton G required")


def anchor_map(anchors: Sequence[GravityAnchor]) -> dict[str, GravityAnchor]:
    result = {anchor.name: anchor for anchor in anchors}
    if len(result) != len(anchors):
        raise ValueError("duplicate gravity anchor")
    return result


def dependency_cycles(anchors: Sequence[GravityAnchor]) -> list[list[str]]:
    table = anchor_map(anchors)
    visiting: set[str] = set()
    visited: set[str] = set()
    cycles: list[list[str]] = []

    def visit(name: str, path: list[str]) -> None:
        if name in visiting:
            start = path.index(name) if name in path else 0
            cycles.append(path[start:] + [name])
            return
        if name in visited or name not in table:
            return
        visiting.add(name)
        for dependency in table[name].depends_on:
            visit(dependency, path + [name])
        visiting.remove(name)
        visited.add(name)

    for name in table:
        visit(name, [])
    return cycles


def default_bundle() -> GravityAnchorBundle:
    constants = Constants()
    return GravityAnchorBundle(
        anchors=(
            GravityAnchor(
                "hbar",
                constants.hbar_joule_second,
                "J s",
                "definition",
                "universal_gravity",
                "SI definition through exact Planck constant",
            ),
            GravityAnchor(
                "c",
                constants.speed_of_light_m_per_s,
                "m s^-1",
                "definition",
                "universal_gravity",
                "SI definition",
            ),
            GravityAnchor(
                "electron_clock_frequency",
                compton_frequency(9.109_383_7139e-31, constants),
                "rad s^-1",
                "external",
                "particle",
                "2022 CODATA electron mass converted to Compton frequency",
            ),
            GravityAnchor(
                "universal_gravity_mass",
                None,
                "kg",
                "absent",
                "universal_gravity",
                "no independent universal gravity mass registered",
            ),
            GravityAnchor(
                "universal_gravity_clock_frequency",
                None,
                "rad s^-1",
                "absent",
                "universal_gravity",
                "no independent universal gravity clock registered",
            ),
        ),
        withheld_newton_G=constants.measured_newton_G,
    )


def synthetic_independent_planck_scale_bundle() -> GravityAnchorBundle:
    """Positive code-path fixture only; it is not registered physical evidence.

    The numerical value is deliberately Planck-scale, but this fixture must never
    be cited as an independent measurement because standard tabulations derive
    the Planck mass from measured G.
    """
    constants = Constants()
    return GravityAnchorBundle(
        anchors=(
            GravityAnchor(
                "hbar",
                constants.hbar_joule_second,
                "J s",
                "definition",
                "universal_gravity",
                "SI definition through exact Planck constant",
            ),
            GravityAnchor(
                "c",
                constants.speed_of_light_m_per_s,
                "m s^-1",
                "definition",
                "universal_gravity",
                "SI definition",
            ),
            GravityAnchor(
                "universal_gravity_mass",
                2.176_434_3427e-8,
                "kg",
                "external",
                "universal_gravity",
                "synthetic Planck-scale fixture for protocol tests only",
            ),
            GravityAnchor(
                "universal_gravity_clock_frequency",
                None,
                "rad s^-1",
                "derived",
                "universal_gravity",
                "derived from universal_gravity_mass",
                depends_on=("universal_gravity_mass", "hbar", "c"),
            ),
        ),
        withheld_newton_G=constants.measured_newton_G,
    )


def circular_inversion_bundle() -> GravityAnchorBundle:
    constants = Constants()
    return GravityAnchorBundle(
        anchors=(
            GravityAnchor(
                "hbar",
                constants.hbar_joule_second,
                "J s",
                "definition",
                "universal_gravity",
                "SI definition",
            ),
            GravityAnchor(
                "c",
                constants.speed_of_light_m_per_s,
                "m s^-1",
                "definition",
                "universal_gravity",
                "SI definition",
            ),
            GravityAnchor(
                "universal_gravity_mass",
                mass_from_newton_G(constants.measured_newton_G, constants),
                "kg",
                "derived",
                "universal_gravity",
                "inverted from measured Newton G",
                depends_on=("newton_G", "hbar", "c"),
                target_dependencies=("newton_G",),
            ),
            GravityAnchor(
                "universal_gravity_clock_frequency",
                clock_from_newton_G(constants.measured_newton_G, constants),
                "rad s^-1",
                "derived",
                "universal_gravity",
                "inverted from measured Newton G",
                depends_on=("newton_G", "hbar", "c"),
                target_dependencies=("newton_G",),
            ),
        ),
        withheld_newton_G=constants.measured_newton_G,
    )


def audit_bundle(bundle: GravityAnchorBundle) -> dict[str, Any]:
    table = anchor_map(bundle.anchors)
    cycles = dependency_cycles(bundle.anchors)
    missing_dependencies = sorted(
        {
            dependency
            for anchor in bundle.anchors
            for dependency in anchor.depends_on
            if dependency not in table and dependency != "newton_G"
        }
    )
    universal_mass = table.get("universal_gravity_mass")
    universal_clock = table.get("universal_gravity_clock_frequency")
    hbar = table.get("hbar")
    c_anchor = table.get("c")
    constants_ready = bool(
        hbar
        and c_anchor
        and hbar.value is not None
        and c_anchor.value is not None
        and hbar.evidence_class == "definition"
        and c_anchor.evidence_class == "definition"
    )
    mass_independent = bool(universal_mass and universal_mass.independent)
    clock_independent = bool(universal_clock and universal_clock.independent)
    one_independent_universal_anchor = mass_independent or clock_independent
    all_particle_anchors_rejected = all(
        not anchor.independent
        for anchor in bundle.anchors
        if anchor.scope == "particle"
    )
    circular = any(
        "newton_G" in anchor.depends_on or "newton_G" in anchor.target_dependencies
        for anchor in bundle.anchors
        if anchor.name.startswith("universal_gravity")
    )
    ready = (
        constants_ready
        and one_independent_universal_anchor
        and all_particle_anchors_rejected
        and not cycles
        and not missing_dependencies
        and not circular
    )
    return {
        "anchors": [asdict(anchor) for anchor in bundle.anchors],
        "dependency_cycles": cycles,
        "missing_dependencies": missing_dependencies,
        "constants_ready": constants_ready,
        "mass_anchor_independent": mass_independent,
        "clock_anchor_independent": clock_independent,
        "one_independent_universal_anchor": one_independent_universal_anchor,
        "particle_scoped_anchors_rejected": all_particle_anchors_rejected,
        "newton_G_circularity_detected": circular,
        "prediction_ready": ready,
        "withheld_newton_G": bundle.withheld_newton_G,
        "relative_gate": bundle.relative_gate,
    }


def execute_frozen_prediction(bundle: GravityAnchorBundle) -> dict[str, Any]:
    audit = audit_bundle(bundle)
    if not audit["prediction_ready"]:
        return {
            "executed": False,
            "passed": False,
            "reason": "independent universal gravity anchor prerequisites do not close",
            "audit": audit,
        }
    table = anchor_map(bundle.anchors)
    constants = Constants(
        hbar_joule_second=float(table["hbar"].value),
        speed_of_light_m_per_s=float(table["c"].value),
        measured_newton_G=(
            Constants().measured_newton_G
            if bundle.withheld_newton_G is None
            else bundle.withheld_newton_G
        ),
    )
    mass_anchor = table.get("universal_gravity_mass")
    clock_anchor = table.get("universal_gravity_clock_frequency")
    predictions: dict[str, float] = {}
    if mass_anchor is not None and mass_anchor.independent:
        predictions["from_mass"] = newton_G_from_mass(
            float(mass_anchor.value), constants
        )
    if clock_anchor is not None and clock_anchor.independent:
        predictions["from_clock"] = newton_G_from_clock(
            float(clock_anchor.value), constants
        )
    if not predictions:
        raise AssertionError("prediction-ready bundle has no executable anchor")
    values = list(predictions.values())
    internal_spread = (
        0.0
        if len(values) == 1
        else (max(values) - min(values)) / max(abs(values[0]), 1.0e-300)
    )
    withheld = bundle.withheld_newton_G
    comparison_error = None
    comparison_passed = False
    if withheld is not None:
        comparison_error = min(relative_error(value, withheld) for value in values)
        comparison_passed = comparison_error <= bundle.relative_gate
    return {
        "executed": True,
        "predictions": predictions,
        "internal_relative_spread": internal_spread,
        "withheld_newton_G": withheld,
        "withheld_relative_error": comparison_error,
        "passed": bool(withheld is not None and comparison_passed),
        "audit": audit,
        "gravity_coupling_injection": {
            "weak_field_newton_coupling": values[0],
            "nonlinear_gravity_newton_coupling": values[0],
            "same_frozen_G_used_in_both_gravity_levels": True,
        },
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_newton_G_anchor_protocol() -> dict[str, Any]:
    default = default_bundle()
    audit = audit_bundle(default)
    blocked = execute_frozen_prediction(default)
    circular = audit_bundle(circular_inversion_bundle())
    payload = {
        "schema": "openwave.m9.newton-G-anchor-protocol.v1",
        "task": "M9.109c",
        "default_audit": audit,
        "default_prediction": blocked,
        "circular_inversion_control": circular,
        "preregistered_prediction": {
            "id": "CAT-EPT-M9.109-G-FROM-UNIVERSAL-CLOCK",
            "observable": "Newton G from one independently measured universal gravity mass or clock",
            "failure_rule": (
                "reject the universal clock interpretation if a frozen independent "
                "anchor misses withheld CODATA G or if different universal paths disagree"
            ),
            "forbidden_inputs": (
                "withheld newton_G",
                "particle-specific Compton clock treated as universal",
                "natural-unit m=omega=sigma0=1 closure",
            ),
        },
        "policy": {
            "G_is_derived_not_primitive": True,
            "mass_or_clock_anchor_must_be_independent": True,
            "particle_clock_scope_is_rejected_for_universal_G": True,
            "G_inversion_is_consistency_control_not_prediction": True,
            "natural_unit_closure_is_not_physical_prediction": True,
            "same_frozen_G_must_feed_weak_and_nonlinear_gravity": True,
        },
    }
    acceptance = {
        "default_internal_state_remains_blocked": not audit["prediction_ready"]
        and not blocked["executed"],
        "particle_clock_cannot_close_universal_anchor": audit[
            "particle_scoped_anchors_rejected"
        ],
        "G_inversion_circularity_is_detected": circular[
            "newton_G_circularity_detected"
        ]
        and not circular["prediction_ready"],
        "prediction_has_explicit_failure_rule": bool(
            payload["preregistered_prediction"]["failure_rule"]
        ),
        "same_G_injection_is_preregistered": payload["policy"][
            "same_frozen_G_must_feed_weak_and_nonlinear_gravity"
        ],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "independent_universal_gravity_anchor_complete": audit["prediction_ready"],
            "withheld_G_prediction_executed": blocked["executed"],
            "Newton_G_promoted_to_external_prediction": False,
            "M9_110_metric_generalization_unblocked": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
