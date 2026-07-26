"""M9.102c: executable, hash-verified snapshots for the M9.101 campaigns.

M9.101 exposed runners but did not commit post-merge numerical result ledgers.
This module turns one fresh execution into four complete JSON snapshots plus a
deterministic manifest.  Verification checks schemas, required quantitative
fields, component hashes, and the distinction between campaign passage and the
nested physical sub-gates.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .clock_action_rate_calibration import run_clock_action_rate_calibration
from .coupled_gauge_spinor_hartree_action import (
    run_coupled_gauge_spinor_hartree_action,
)
from .covariant_packet_tbmt import run_covariant_packet_tbmt
from .electrogravitic_weak_field_evolution import (
    run_electrogravitic_weak_field_evolution,
)
from .formalization_m102_extension import (
    CURRENT_FORMAL_HEAD,
    HISTORICAL_FORMAL_HEAD,
)

OPENWAVE_HEAD = "fe9c98a94a0f233c9dda842fa144ae181d01c9e5"

CAMPAIGNS = {
    "coupled_action": {
        "schema": "openwave.m9.coupled-gauge-spinor-hartree-action.v1",
        "filename": "m9_101_coupled_action.json",
        "required_paths": (
            ("passed",),
            ("initial", "action", "total"),
            ("final", "action", "total"),
            ("final", "symmetry_reduced", "relative_projected_residual"),
            ("final", "symmetry_reduced", "spin_sector_leakage"),
            ("final", "winding", "integer_winding"),
            ("symmetry_reduced_stationary_branch_constructed",),
            ("decision", "unrestricted_stable_charged_branch_constructed"),
        ),
    },
    "packet_tbmt": {
        "schema": "openwave.m9.covariant-packet-tbmt.v1",
        "filename": "m9_101_packet_tbmt.json",
        "required_paths": (
            ("passed",),
            ("interaction_packet_tbmt_rate",),
            ("interaction_dirac_generator_rate",),
            ("legacy_rest_frame_rate",),
            ("relative_errors", "local_packet_tbmt_vs_generator"),
            ("relative_errors", "legacy_rest_frame_vs_generator"),
            ("local_packet_improves_on_rest_frame",),
            ("local_packet_tbmt_closes_on_current_packet",),
            ("pair_velocity_audit",),
        ),
    },
    "clock": {
        "schema": "openwave.m9.clock-action-rate-calibration.v1",
        "filename": "m9_101_clock_calibration.json",
        "required_paths": (
            ("passed",),
            ("measured_internal_frequency",),
            ("action_rate",),
            ("compton_clock_mass",),
            ("isolated_yukawa",),
            ("observed_mean_entropy_rate",),
            ("entropy_action_unit",),
            ("entropy_rate_modulation_fraction",),
            ("held_out",),
            ("decision", "external_clock_or_mass_calibration_complete"),
        ),
    },
    "gravity": {
        "schema": "openwave.m9.electrogravitic-weak-field-evolution.v1",
        "filename": "m9_101_weak_field_gravity.json",
        "required_paths": (
            ("passed",),
            ("records",),
            ("maximum_pre_normalization_norm_drift",),
            ("equivalence_probe_error",),
            ("decision", "end_to_end_weak_field_electrogravitic_evolution_constructed"),
            ("decision", "full_nonlinear_four_dimensional_einstein_evolution_constructed"),
        ),
    },
}


def _json_default(value: object) -> object:
    if hasattr(value, "tolist"):
        return value.tolist()  # type: ignore[no-any-return]
    if hasattr(value, "item"):
        return value.item()  # type: ignore[no-any-return]
    raise TypeError(f"not JSON serializable: {type(value).__name__}")


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        default=_json_default,
    ).encode()


def _hash(value: object) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()


def _lookup(payload: Mapping[str, Any], path: Sequence[str]) -> Any:
    value: Any = payload
    for key in path:
        if not isinstance(value, Mapping) or key not in value:
            raise KeyError(".".join(path))
        value = value[key]
    return value


def validate_component(name: str, payload: Mapping[str, Any]) -> list[str]:
    if name not in CAMPAIGNS:
        return [f"unknown campaign: {name}"]
    specification = CAMPAIGNS[name]
    errors: list[str] = []
    if payload.get("schema") != specification["schema"]:
        errors.append(
            f"{name}: schema {payload.get('schema')!r} != {specification['schema']!r}"
        )
    for path in specification["required_paths"]:
        try:
            _lookup(payload, path)
        except KeyError:
            errors.append(f"{name}: missing {'.'.join(path)}")
    if not isinstance(payload.get("passed"), bool):
        errors.append(f"{name}: passed must be Boolean")
    if name == "clock" and not isinstance(payload.get("held_out"), list):
        errors.append("clock: held_out must be a list")
    if name == "gravity":
        records = payload.get("records")
        if not isinstance(records, list) or not records:
            errors.append("gravity: records must be a nonempty list")
    return errors


@lru_cache(maxsize=1)
def component_payloads() -> dict[str, dict[str, Any]]:
    return {
        "coupled_action": run_coupled_gauge_spinor_hartree_action(),
        "packet_tbmt": run_covariant_packet_tbmt(),
        "clock": run_clock_action_rate_calibration(),
        "gravity": run_electrogravitic_weak_field_evolution(),
    }


def quantitative_summary(payloads: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    action = payloads["coupled_action"]
    packet = payloads["packet_tbmt"]
    clock = payloads["clock"]
    gravity = payloads["gravity"]
    records = gravity["records"]
    return {
        "coupled_action": {
            "campaign_passed": action["passed"],
            "initial_total_action": action["initial"]["action"]["total"],
            "final_total_action": action["final"]["action"]["total"],
            "action_nonincrease": action["action_nonincrease"],
            "projected_stationary_residual": action["final"]["symmetry_reduced"]["relative_projected_residual"],
            "spin_sector_leakage": action["final"]["symmetry_reduced"]["spin_sector_leakage"],
            "measured_winding": action["final"]["winding"]["integer_winding"],
            "symmetry_reduced_state_gate": action["symmetry_reduced_stationary_branch_constructed"],
            "unrestricted_state_gate": action["decision"]["unrestricted_stable_charged_branch_constructed"],
        },
        "packet_tbmt": {
            "campaign_passed": packet["passed"],
            "packet_vs_generator_error": packet["relative_errors"]["local_packet_tbmt_vs_generator"],
            "rest_vs_generator_error": packet["relative_errors"]["legacy_rest_frame_vs_generator"],
            "finite_time_vs_generator_error": packet["relative_errors"]["finite_time_vs_generator"],
            "improves_on_rest_frame": packet["local_packet_improves_on_rest_frame"],
            "reduction_gate": packet["local_packet_tbmt_closes_on_current_packet"],
            "pair_velocity_audit": packet["pair_velocity_audit"],
        },
        "clock": {
            "campaign_passed": clock["passed"],
            "measured_internal_frequency": clock["measured_internal_frequency"],
            "action_rate": clock["action_rate"],
            "compton_clock_mass": clock["compton_clock_mass"],
            "isolated_yukawa": clock["isolated_yukawa"],
            "observed_mean_entropy_rate": clock["observed_mean_entropy_rate"],
            "entropy_action_unit": clock["entropy_action_unit"],
            "entropy_rate_modulation_fraction": clock["entropy_rate_modulation_fraction"],
            "held_out": clock["held_out"],
            "external_calibration_gate": clock["decision"]["external_clock_or_mass_calibration_complete"],
        },
        "gravity": {
            "campaign_passed": gravity["passed"],
            "maximum_einstein00_residual": max(row["einstein00_relative_residual"] for row in records),
            "maximum_gauss_residual": max(row["gauss_relative_residual"] for row in records),
            "maximum_ampere_residual": max(row["ampere_relative_residual"] for row in records),
            "maximum_magnetic_divergence": max(row["magnetic_divergence_max"] for row in records),
            "minimum_g00": min(row["minimum_g00"] for row in records),
            "maximum_metric_perturbation": max(row["maximum_metric_perturbation"] for row in records),
            "maximum_norm_error": max(abs(row["norm"] - 1.0) for row in records),
            "maximum_pre_normalization_norm_drift": gravity["maximum_pre_normalization_norm_drift"],
            "equivalence_probe_error": gravity["equivalence_probe_error"],
            "full_einstein_state_gate": gravity["decision"]["full_nonlinear_four_dimensional_einstein_evolution_constructed"],
        },
    }


def canonical_manifest(
    payloads: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    selected = component_payloads() if payloads is None else payloads
    validation = {
        name: validate_component(name, selected[name]) for name in CAMPAIGNS
    }
    return {
        "schema": "openwave.m9.m101-reproducibility-manifest.v1",
        "openwave_head": OPENWAVE_HEAD,
        "historical_formal_head": HISTORICAL_FORMAL_HEAD,
        "current_formal_head": CURRENT_FORMAL_HEAD,
        "components": {
            name: {
                "schema": selected[name].get("schema"),
                "filename": CAMPAIGNS[name]["filename"],
                "sha256": _hash(selected[name]),
                "validation_errors": validation[name],
            }
            for name in CAMPAIGNS
        },
        "quantitative_summary": quantitative_summary(selected),
        "policy": {
            "campaign_passage_is_not_physical_subgate_closure": True,
            "full_component_payloads_are_preserved": True,
            "historical_and_current_formal_heads_are_distinct": True,
            "committed_post_merge_reference_snapshots_present": False,
            "fresh_snapshot_generation_and_verification_available": True,
        },
    }


def write_snapshot_bundle(output_directory: str | Path) -> dict[str, Any]:
    directory = Path(output_directory)
    directory.mkdir(parents=True, exist_ok=True)
    payloads = component_payloads()
    manifest = canonical_manifest(payloads)
    for name, specification in CAMPAIGNS.items():
        path = directory / specification["filename"]
        path.write_text(
            json.dumps(
                payloads[name], indent=2, sort_keys=True, default=_json_default
            )
            + "\n",
            encoding="utf-8",
        )
    (directory / "m9_101_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True, default=_json_default) + "\n",
        encoding="utf-8",
    )
    return manifest


def verify_snapshot_bundle(output_directory: str | Path) -> dict[str, Any]:
    directory = Path(output_directory)
    manifest_path = directory / "m9_101_manifest.json"
    if not manifest_path.is_file():
        return {"passed": False, "errors": ["missing m9_101_manifest.json"]}
    stored_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    payloads: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for name, specification in CAMPAIGNS.items():
        path = directory / specification["filename"]
        if not path.is_file():
            errors.append(f"missing {specification['filename']}")
            continue
        payloads[name] = json.loads(path.read_text(encoding="utf-8"))
        errors.extend(validate_component(name, payloads[name]))
        expected_hash = stored_manifest.get("components", {}).get(name, {}).get("sha256")
        actual_hash = _hash(payloads[name])
        if expected_hash != actual_hash:
            errors.append(f"{name}: sha256 mismatch")
    if len(payloads) == len(CAMPAIGNS):
        rebuilt = canonical_manifest(payloads)
        if rebuilt["quantitative_summary"] != stored_manifest.get("quantitative_summary"):
            errors.append("quantitative summary mismatch")
        if stored_manifest.get("openwave_head") != OPENWAVE_HEAD:
            errors.append("OpenWave head mismatch")
    return {
        "schema": "openwave.m9.m101-reproducibility-verification.v1",
        "directory": str(directory),
        "errors": errors,
        "passed": not errors,
    }


@lru_cache(maxsize=1)
def run_m101_reproducibility_contract() -> dict[str, Any]:
    payloads = component_payloads()
    manifest = canonical_manifest(payloads)
    validation_errors = [
        error
        for component in manifest["components"].values()
        for error in component["validation_errors"]
    ]
    summary = manifest["quantitative_summary"]
    acceptance = {
        "all_four_component_schemas_and_fields_validate": not validation_errors,
        "all_four_component_hashes_are_exact": all(
            len(component["sha256"]) == 64
            for component in manifest["components"].values()
        ),
        "campaign_and_subgate_results_are_both_exposed": (
            "campaign_passed" in summary["coupled_action"]
            and "symmetry_reduced_state_gate" in summary["coupled_action"]
            and "campaign_passed" in summary["packet_tbmt"]
            and "reduction_gate" in summary["packet_tbmt"]
        ),
        "historical_and_current_formal_heads_are_separate": (
            manifest["historical_formal_head"] != manifest["current_formal_head"]
        ),
        "quantitative_summary_is_deterministic": (
            canonical_manifest(payloads)["quantitative_summary"]
            == manifest["quantitative_summary"]
        ),
        "component_hashes_are_deterministic": all(
            component["sha256"] == _hash(payloads[name])
            for name, component in manifest["components"].items()
        ),
    }
    return {
        **manifest,
        "task": "M9.102c",
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "fresh_quantitative_snapshot_contract_completed": True,
            "committed_post_merge_reference_snapshots_added": False,
            "campaign_passage_promoted_to_physical_closure": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=_json_default) + "\n"
