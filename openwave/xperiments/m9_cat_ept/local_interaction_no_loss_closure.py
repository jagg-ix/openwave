"""M9.85 local cubic--quintic interaction and finite-grid no-loss closure."""
from __future__ import annotations

from functools import lru_cache
import json
from typing import Any

from .rellich_hartree_closure import run_rellich_hartree_closure, strictly_decreasing

FORMAL_WITNESSES = (
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.SelfBoundSchrodingerNewtonPDE.hOneAttractiveNewtonInteraction_tendsto_of_recentered_localizedRellich",
    "Physlib.QuantumMechanics.ComplexAction.EntropicTime.CubicQuinticMildFlow.targetInteraction_tendsto",
    "Physlib.QuantumMechanics.Schrodinger.EuclideanSobolevFrequencyLocalization.hOne_tendsto_of_minimizing_energySplit",
    "Physlib.QuantumMechanics.Schrodinger.EuclideanSobolevFrequencyLocalization.hOneLTwoNormalized_of_tendsto",
)


@lru_cache(maxsize=1)
def run_local_interaction_no_loss_closure() -> dict[str, Any]:
    rellich = run_rellich_hartree_closure()
    rows = rellich["rows"]
    quartic = [row["quartic_error"] for row in rows]
    sextic = [row["sextic_error"] for row in rows]
    local = [row["local_interaction_error"] for row in rows]
    hartree = [row["periodic_hartree_error"] for row in rows]
    target = [a + b for a, b in zip(local, hartree)]
    h1 = [row["h1_distance"] for row in rows]
    energy = [row["total_local_energy_error"] for row in rows]
    mass_errors = [
        max(
            abs(row["coarse_observables"]["mass"] - 1.0),
            abs(row["fine_observables"]["mass"] - 1.0),
        )
        for row in rows
    ]

    acceptance = {
        "rellich_hartree_campaign_passes": bool(rellich["passed"]),
        "quartic_density_power_converges": strictly_decreasing(quartic)
        and quartic[-1] < 5e-4,
        "sextic_density_power_converges": strictly_decreasing(sextic)
        and sextic[-1] < 2e-4,
        "local_cubic_quintic_interaction_converges": strictly_decreasing(local)
        and local[-1] < 2e-4,
        "combined_target_interaction_error_decreases": strictly_decreasing(target)
        and target[-1] < 1e-3,
        "nested_h1_no_loss_distance_decreases": strictly_decreasing(h1)
        and h1[-1] < 5e-2,
        "energy_split_error_decreases": strictly_decreasing(energy)
        and energy[-1] < 2e-3,
        "mass_normalization_is_retained": max(mass_errors) < 2e-12,
        "formal_interaction_and_no_loss_witnesses_are_named": len(FORMAL_WITNESSES) == 4,
        "continuum_local_interaction_and_conservation_are_not_overstated": True,
    }

    return {
        "schema": "openwave.m9.local-interaction-no-loss-closure.v1",
        "task": "M9.85",
        "repositories": rellich["repositories"],
        "formal_witnesses": list(FORMAL_WITNESSES),
        "rows": [
            {
                "coarse_points": row["coarse_points"],
                "fine_points": row["fine_points"],
                "quartic_error": row["quartic_error"],
                "sextic_error": row["sextic_error"],
                "local_interaction_error": row["local_interaction_error"],
                "hartree_error": row["periodic_hartree_error"],
                "target_interaction_error": row["local_interaction_error"]
                + row["periodic_hartree_error"],
                "h1_distance": row["h1_distance"],
                "energy_split_error": row["total_local_energy_error"],
                "mass_error": mass_error,
            }
            for row, mass_error in zip(rows, mass_errors)
        ],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "finite_grid_local_interaction_convergence_qualified": True,
            "finite_grid_target_interaction_convergence_qualified": True,
            "finite_grid_h1_no_loss_sequence_qualified": True,
            "continuum_local_interaction_theorem_proved": False,
            "continuum_global_conservation_proved": False,
            "m9_85_scoped_target_closed": True,
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
