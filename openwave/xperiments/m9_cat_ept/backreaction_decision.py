"""M9.18: compare selected CAT/EPT back-reaction interfaces.

The decision contrasts three already-qualified controls:

* M9.15 trace-decreasing imaginary-action amplitude loss;
* M9.16 trace-preserving Lindblad dephasing;
* M9.17 matter-to-reservoir spatial transfer.

The goal is discrimination, not promotion.  Monotone operational clocks are
recorded, but no unique back-reaction or physical-time identification is accepted.
"""

from __future__ import annotations

from functools import lru_cache
import json
import math
from typing import Any

from .imaginary_action_backreaction import initial_state as amplitude_initial_state
from .imaginary_action_backreaction import run_imaginary_action_study
from .lindblad_information_loss import initial_density, run_lindblad_information_study
from .reservoir_backreaction import run_reservoir_backreaction_study


def initial_coherence_l1() -> float:
    rho = initial_density()
    return 2.0 * abs(complex(rho[0, 1]))


def normalized_amplitude_purity() -> float:
    # A single unnormalized state remains rank one after normalization.
    state = amplitude_initial_state()
    return float(abs((state.conj() @ state)) ** 2)


def build_falsification_table() -> list[dict[str, Any]]:
    return [
        {
            "observable": "accessible matter trace / norm",
            "imaginary_action": "decreases",
            "lindblad_dephasing": "preserved",
            "explicit_reservoir": "matter decreases",
        },
        {
            "observable": "extended matter plus reservoir trace",
            "imaginary_action": "no reservoir ledger in the selected model",
            "lindblad_dephasing": "preserved without reservoir transfer",
            "explicit_reservoir": "preserved with recorded transfer",
        },
        {
            "observable": "normalized purity",
            "imaginary_action": "remains one for scalar amplitude loss",
            "lindblad_dephasing": "decreases",
            "explicit_reservoir": "not a reduced-density dephasing claim",
        },
        {
            "observable": "zero-coupling limit",
            "imaginary_action": "unitary state evolution",
            "lindblad_dephasing": "unitary density evolution",
            "explicit_reservoir": "closed spatial Dirac transport",
        },
    ]


@lru_cache(maxsize=1)
def run_backreaction_decision() -> dict[str, Any]:
    amplitude = run_imaginary_action_study()
    lindblad = run_lindblad_information_study()
    reservoir = run_reservoir_backreaction_study()

    amplitude_norm = float(amplitude["finest"]["final_norm"])
    amplitude_tau = float(amplitude["finest"]["final_tau_ent"])
    amplitude_purity = normalized_amplitude_purity()

    lindblad_trace_error = float(lindblad["finest"]["max_trace_error"])
    lindblad_purity = float(lindblad["finest"]["final_purity"])
    lindblad_coherence = float(lindblad["finest"]["final_coherence_l1"])
    coherence0 = initial_coherence_l1()
    lindblad_tau = -0.5 * math.log(lindblad_coherence / coherence0)

    reservoir_summary = reservoir["long_run"]
    reservoir_matter = float(reservoir_summary["final"]["matter_probability"])
    reservoir_transfer = float(reservoir_summary["final"]["reservoir_probability"])
    reservoir_extended_error = float(reservoir_summary["max_extended_probability_error"])
    reservoir_tau = float(reservoir_summary["final"]["tau_ent"])

    signatures = {
        "imaginary_action": {
            "matter_trace": amplitude_norm,
            "extended_trace_available": False,
            "normalized_purity": amplitude_purity,
            "operational_tau": amplitude_tau,
        },
        "lindblad_dephasing": {
            "matter_trace": 1.0,
            "trace_error": lindblad_trace_error,
            "normalized_purity": lindblad_purity,
            "coherence_l1": lindblad_coherence,
            "operational_tau": lindblad_tau,
        },
        "explicit_reservoir": {
            "matter_trace": reservoir_matter,
            "reservoir_transfer": reservoir_transfer,
            "extended_trace": reservoir_matter + reservoir_transfer,
            "extended_trace_error": reservoir_extended_error,
            "operational_tau": reservoir_tau,
        },
    }

    discrimination = {
        "amplitude_vs_lindblad_trace_margin": 1.0 - amplitude_norm,
        "amplitude_vs_lindblad_purity_margin": amplitude_purity - lindblad_purity,
        "reservoir_transfer_margin": reservoir_transfer,
        "amplitude_vs_reservoir_tau_difference": abs(amplitude_tau - reservoir_tau),
        "lindblad_vs_reservoir_tau_difference": abs(lindblad_tau - reservoir_tau),
        "amplitude_vs_lindblad_tau_difference": abs(amplitude_tau - lindblad_tau),
    }

    falsification_table = build_falsification_table()
    unique_backreaction_selected = False
    physical_time_identified = False
    acceptance = {
        "all_component_studies_pass": amplitude["passed"] and lindblad["passed"] and reservoir["passed"],
        "amplitude_loss_has_trace_signature": discrimination["amplitude_vs_lindblad_trace_margin"] >= 0.5,
        "dephasing_has_purity_signature": discrimination["amplitude_vs_lindblad_purity_margin"] >= 0.3,
        "reservoir_transfer_is_explicit": (
            discrimination["reservoir_transfer_margin"] >= 0.5
            and reservoir_extended_error <= 5.0e-8
        ),
        "operational_clocks_are_not_numerically_identical": max(
            discrimination["amplitude_vs_reservoir_tau_difference"],
            discrimination["lindblad_vs_reservoir_tau_difference"],
            discrimination["amplitude_vs_lindblad_tau_difference"],
        ) >= 0.1,
        "zero_coupling_limits_close": (
            amplitude["acceptance"]["zero_loss_reduces_to_unitary"]
            and lindblad["acceptance"]["zero_loss_reduces_to_unitary"]
            and reservoir["acceptance"]["zero_loss_reduces_to_closed_transport"]
        ),
        "falsification_table_complete": len(falsification_table) == 4,
        "no_unique_backreaction_promoted": not unique_backreaction_selected,
        "no_physical_time_identity_promoted": not physical_time_identified,
    }

    return {
        "schema": "openwave.m9.backreaction-decision-result.v1",
        "task": "M9.18",
        "component_tasks": ["M9.15", "M9.16", "M9.17"],
        "signatures": signatures,
        "discrimination": discrimination,
        "falsification_table": falsification_table,
        "unique_backreaction_selected": unique_backreaction_selected,
        "physical_time_identified": physical_time_identified,
        "decision": (
            "The selected imaginary-action, Lindblad, and explicit-reservoir interfaces "
            "are operationally distinguishable. Monotonicity alone does not select one "
            "mechanism or identify physical time."
        ),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "distinct trace, purity, and reservoir-transfer signatures",
                "a falsifiable comparison among three selected back-reaction interfaces",
                "closed zero-coupling limits for all three controls",
                "an explicit negative uniqueness and physical-time decision",
            ],
            "does_not_establish": [
                "which interface is realized in Nature",
                "that any operational monotone is a unique physical time",
                "microscopic derivation of the selected rates or reservoir",
                "particle identity, calibrated units, or experimental agreement",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
