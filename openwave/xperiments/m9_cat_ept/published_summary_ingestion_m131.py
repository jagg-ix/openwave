"""M9.131b: published table, fit-parameter, and summary-bound ingestion.

Rows are restricted to values explicitly reported in publication text or tables.
Equation-derived trajectories are marked as reconstructions and are not raw
experimental observations.
"""
from __future__ import annotations

from math import exp
from typing import Any

from .published_source_manifests_m131 import canonical_manifests


MOREVA_2017_K3 = (
    {"omega_dt": 0.2, "theory": 1.159, "observed": 1.138, "uncertainty": 0.004},
    {"omega_dt": 0.5, "theory": 1.499, "observed": 1.538, "uncertainty": 0.018},
    {"omega_dt": 0.7, "theory": 1.282, "observed": 1.238, "uncertainty": 0.018},
)

GUSTAVSSON_2016 = {
    "mean_quasiparticle_number": 2.5,
    "single_quasiparticle_relaxation_us": 23.0,
    "residual_relaxation_us": 55.0,
    "qubit_frequency_ghz": 5.4,
}

LU_2003 = {
    "inelastic_scattering_time_lower_bound_us": 10.0,
    "statement": "long (10 microseconds or more) inelastic scattering times in nearly isolated dots",
}


def quasiparticle_decay(time_us: float) -> float:
    nqp = GUSTAVSSON_2016["mean_quasiparticle_number"]
    t1qp = GUSTAVSSON_2016["single_quasiparticle_relaxation_us"]
    t1r = GUSTAVSSON_2016["residual_relaxation_us"]
    return exp(nqp * (exp(-time_us / t1qp) - 1.0)) * exp(-time_us / t1r)


def published_summary_rows() -> tuple[dict[str, Any], ...]:
    relational = tuple(
        {
            "observation_id": f"moreva-2017-k3-{index}",
            "source_id": "moreva-2017-multitime",
            "carrier": "single-photon-position-clock",
            "domain": "leggett-garg-correlation",
            "x": row["omega_dt"],
            "y": row["observed"],
            "uncertainty": row["uncertainty"],
            "theory": row["theory"],
            "units": {"x": "dimensionless", "y": "K3"},
            "evidence_level": "published-table",
        }
        for index, row in enumerate(MOREVA_2017_K3)
    )
    qubit = tuple(
        {
            "observation_id": f"gustavsson-2016-fit-{int(time_us)}us",
            "source_id": "gustavsson-2016-qubit",
            "carrier": "superconducting-flux-qubit",
            "domain": "quasiparticle-relaxation-fit",
            "x": time_us,
            "y": quasiparticle_decay(time_us),
            "uncertainty": 0.0,
            "units": {"x": "microsecond", "y": "normalized-population"},
            "evidence_level": "equation-reconstruction-from-published-fit",
        }
        for time_us in (0.0, 8.0, 16.0, 26.0, 55.0)
    )
    dot = (
        {
            "observation_id": "lu-2003-inelastic-lower-bound",
            "source_id": "lu-2003-dot",
            "carrier": "quantum-dot-charge-state",
            "domain": "inelastic-scattering-bound",
            "x": 0.0,
            "y": LU_2003["inelastic_scattering_time_lower_bound_us"],
            "uncertainty": 0.0,
            "units": {"x": "not-applicable", "y": "microsecond"},
            "evidence_level": "published-summary-bound",
        },
    )
    return relational + qubit + dot


def run_published_summary_ingestion() -> dict[str, Any]:
    rows = published_summary_rows()
    source_ids = {row["source_id"] for row in rows}
    registered = {row["source_id"] for row in canonical_manifests()}
    acceptance = {
        "published_K3_table_rows_ingested": sum(row["evidence_level"] == "published-table" for row in rows) == 3,
        "published_qubit_fit_parameters_reconstructed": sum(
            row["evidence_level"] == "equation-reconstruction-from-published-fit" for row in rows
        ) == 5,
        "published_quantum_dot_bound_ingested": any(
            row["evidence_level"] == "published-summary-bound" for row in rows
        ),
        "all_row_sources_are_registered": source_ids <= registered,
        "raw_observation_rows_are_not_claimed": not any(
            row["evidence_level"] == "raw-observation" for row in rows
        ),
    }
    return {
        "schema": "openwave.m9.published-summary-ingestion.v1",
        "task": "M9.131b",
        "rows": rows,
        "source_ids": tuple(sorted(source_ids)),
        "raw_observation_rows_ingested": False,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
    }
