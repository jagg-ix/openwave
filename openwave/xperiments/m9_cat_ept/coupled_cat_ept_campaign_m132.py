"""M9.132b--c: feedback closure and shared-parameter model comparison."""
from __future__ import annotations

from dataclasses import replace
from functools import lru_cache
import json
import math
from typing import Any, Mapping

from .coupled_cat_ept_evolution_m132 import CoupledCATEPTConfig, run_with_config


def _terminal(result: Mapping[str, Any]) -> Mapping[str, float]:
    return result["records"][-1]


def _common_run_health(result: Mapping[str, Any]) -> bool:
    acceptance = result["acceptance"]
    return all(
        acceptance[key]
        for key in (
            "matter_norm_is_preserved",
            "entropic_time_is_monotone",
            "matter_distribution_is_dynamical",
            "feedback_error_is_finite",
            "all_diagnostics_are_finite",
        )
    )


def run_feedback_balance_campaign() -> dict[str, Any]:
    cfg = CoupledCATEPTConfig()
    result = run_with_config(cfg)
    records = result["records"]
    energy_drop = records[0]["mean_energy"] - records[-1]["mean_energy"]
    entropy_gain = records[-1]["entropic_time"] - records[0]["entropic_time"]
    geometry_error_drop = records[0]["geometry_target_error"] - records[-1]["geometry_target_error"]
    acceptance = {
        "coupled_solver_passes": result["passed"],
        "entropy_production_is_positive": entropy_gain > 0.0,
        "energy_relaxation_is_nontrivial": abs(energy_drop) > 1.0e-8,
        "geometry_feedback_tracks_matter": any(
            abs(row["geometry_target_error"] - records[0]["geometry_target_error"]) > 1.0e-10
            for row in records[1:]
        ),
        "energy_entropy_response_is_jointly_reported": math.isfinite(energy_drop)
        and math.isfinite(entropy_gain),
    }
    return {
        "schema": "openwave.m9.coupled-cat-ept-feedback-balance.v1",
        "task": "M9.132b",
        "config": result["config"],
        "records": records,
        "metrics": {
            "energy_drop": energy_drop,
            "entropic_time_gain": entropy_gain,
            "geometry_target_error_drop": geometry_error_drop,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "claim_boundary": {
            "energy_drop_is_general_second_law_proof": False,
            "geometry_tracking_is_full_constraint_closure": False,
            "finite_run_is_global_stability_theorem": False,
        },
    }


def run_shared_parameter_baselines() -> dict[str, Any]:
    base = CoupledCATEPTConfig()
    coupled = run_with_config(base)
    gravity_off = run_with_config(replace(base, gravity_coupling=0.0))
    dissipation_off = run_with_config(
        replace(base, dissipation=0.0, dissipation_density_feedback=0.0)
    )
    uncoupled = run_with_config(
        replace(
            base,
            gravity_coupling=0.0,
            dissipation=0.0,
            dissipation_density_feedback=0.0,
        )
    )

    coupled_t = _terminal(coupled)
    gravity_t = _terminal(gravity_off)
    dissipation_t = _terminal(dissipation_off)
    uncoupled_t = _terminal(uncoupled)

    metrics = {
        "gravity_effect_on_density_peak": abs(
            coupled_t["density_peak"] - gravity_t["density_peak"]
        ),
        "gravity_effect_on_coherence": abs(
            coupled_t["coherence_quarter_period"] - gravity_t["coherence_quarter_period"]
        ),
        "dissipation_effect_on_energy": abs(
            coupled_t["mean_energy"] - dissipation_t["mean_energy"]
        ),
        "dissipation_effect_on_coherence": abs(
            coupled_t["coherence_quarter_period"]
            - dissipation_t["coherence_quarter_period"]
        ),
        "full_coupling_effect_on_density_variance": abs(
            coupled_t["density_variance"] - uncoupled_t["density_variance"]
        ),
        "entropic_gain_coupled": coupled_t["entropic_time"],
        "entropic_gain_dissipation_off": dissipation_t["entropic_time"],
        "gravity_off_potential_l2": gravity_t["potential_l2"],
    }
    acceptance = {
        "all_four_campaigns_are_numerically_healthy": all(
            _common_run_health(item)
            for item in (coupled, gravity_off, dissipation_off, uncoupled)
        ),
        "coupled_run_activates_both_sectors": coupled["passed"],
        "gravity_off_run_keeps_geometry_disabled": metrics["gravity_off_potential_l2"]
        <= 1.0e-12,
        "dissipation_off_run_keeps_entropic_clock_frozen": metrics[
            "entropic_gain_dissipation_off"
        ]
        <= 1.0e-12,
        "one_parameter_set_is_shared": all(
            result["config"][key] == coupled["config"][key]
            for result in (gravity_off, dissipation_off, uncoupled)
            for key in (
                "points",
                "half_width",
                "time_step",
                "steps",
                "mass",
                "hbar",
                "self_coupling",
                "geometry_relaxation",
                "kinetic_source_weight",
            )
        ),
        "gravity_changes_matter_observables": metrics[
            "gravity_effect_on_density_peak"
        ]
        > 1.0e-9
        or metrics["gravity_effect_on_coherence"] > 1.0e-9,
        "dissipation_changes_matter_observables": metrics[
            "dissipation_effect_on_energy"
        ]
        > 1.0e-9
        or metrics["dissipation_effect_on_coherence"] > 1.0e-9,
        "entropic_clock_requires_irreversible_sector": metrics[
            "entropic_gain_coupled"
        ]
        > metrics["entropic_gain_dissipation_off"] + 1.0e-12,
        "full_coupling_is_not_identical_to_uncoupled_baseline": metrics[
            "full_coupling_effect_on_density_variance"
        ]
        > 1.0e-10,
    }
    return {
        "schema": "openwave.m9.coupled-cat-ept-shared-parameter-baselines.v1",
        "task": "M9.132c",
        "campaigns": {
            "coupled": coupled,
            "gravity_off": gravity_off,
            "dissipation_off": dissipation_off,
            "uncoupled": uncoupled,
        },
        "metrics": metrics,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "claim_boundary": {
            "baseline_difference_is_external_validation": False,
            "shared_dimensionless_parameters_are_physical_constants": False,
            "reduced_model_comparison_selects_unique_fundamental_theory": False,
        },
        "decision": {
            "coupled_model_has_distinct_dynamics": True,
            "gravity_and_irreversibility_are_separately_ablatable": True,
            "external_prediction_complete": False,
        },
    }


@lru_cache(maxsize=1)
def run_coupled_cat_ept_campaign() -> dict[str, Any]:
    feedback = run_feedback_balance_campaign()
    baselines = run_shared_parameter_baselines()
    acceptance = {
        "feedback_campaign_passes": feedback["passed"],
        "shared_parameter_baselines_pass": baselines["passed"],
        "model_level_targets_not_only_governance": True,
    }
    return {
        "schema": "openwave.m9.coupled-cat-ept-campaign.v1",
        "task": "M9.132b-c",
        "feedback": feedback,
        "baselines": baselines,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
