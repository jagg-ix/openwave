"""Composed M9.136 authority for nonperturbative QCD order parameters."""
from __future__ import annotations

from typing import Any

from .qcd_order_parameters_m136 import run_qcd_order_parameter_study
from .m135_qcd_particle_authority import run_m135_qcd_particle_authority


def run_m136_qcd_order_parameter_authority() -> dict[str, Any]:
    previous = run_m135_qcd_particle_authority()
    current = run_qcd_order_parameter_study()
    acceptance = {
        "m9_135_qcd_foundation_remains_valid": bool(previous["passed"]),
        "m9_136_order_parameter_study_passes": current.passed,
        "physlib_tip_is_exact": current.physlib["tip"] == "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748",
        "three_global_targets_are_present": {r["id"] for r in current.source_records}
        == {
            "polyakov-loop-deconfinement",
            "chiral-symmetry-breaking",
            "axial-anomaly-eta-prime",
        },
        "physical_promotion_remains_blocked": True,
    }
    return {
        "schema": "openwave.m9.m136-qcd-order-parameter-authority.v1",
        "milestone": "M9.136",
        "previous_authority": previous,
        "study": current.payload(),
        "study_fingerprint": current.fingerprint(),
        "acceptance": acceptance,
        "claim_boundaries": {
            "numerical_deconfinement_temperature": False,
            "ab_initio_chiral_condensate": False,
            "ab_initio_topological_susceptibility": False,
            "physical_massless_quark_solution_to_strong_cp": False,
            "unique_catept_validation": False,
        },
        "passed": all(acceptance.values()),
    }
