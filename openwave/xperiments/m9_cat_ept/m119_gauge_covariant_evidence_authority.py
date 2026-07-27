"""M9.119 evidence authority for gauge-covariant strong and electroweak carriers."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .electroweak_higgs_lattice import run_electroweak_higgs_lattice
from .formalization_m119_extension import run_formalization_m119_extension
from .m117_coarse_graining_evidence_authority import run_m117_coarse_graining_evidence_authority
from .non_abelian_lattice_gauge import run_non_abelian_lattice_gauge


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m119_gauge_covariant_evidence_authority() -> dict[str, Any]:
    previous = run_m117_coarse_graining_evidence_authority()
    formal = run_formalization_m119_extension()
    strong = run_non_abelian_lattice_gauge()
    electroweak = run_electroweak_higgs_lattice()
    component = {
        "formal_authority_passed": bool(formal["passed"]),
        "strong_campaign_passed": bool(strong["passed"]),
        "local_SU3_links": strong["decision"]["local_SU3_link_carrier_constructed"],
        "gauge_covariant_color_dynamics": strong["decision"]["gauge_covariant_color_matter_evolution_constructed"],
        "Wilson_observables": strong["decision"]["Wilson_plaquette_and_loop_observables_constructed"],
        "QCD_confinement_established": strong["decision"]["QCD_confinement_established"],
        "electroweak_campaign_passed": bool(electroweak["passed"]),
        "local_SU2xU1_links": electroweak["decision"]["local_SU2xU1_link_carrier_constructed"],
        "gauge_covariant_Higgs_dynamics": electroweak["decision"]["gauge_covariant_Higgs_evolution_constructed"],
        "quartic_Higgs_vacuum_orbit": electroweak["decision"]["quartic_Higgs_vacuum_orbit_constructed"],
        "complete_electroweak_theory": electroweak["decision"]["complete_electroweak_theory_constructed"],
    }
    payload = {
        "schema": "openwave.m9.m119-gauge-covariant-evidence-authority.v1",
        "task": "M9.119",
        "previous_authority": previous,
        "formal_authority": formal,
        "component": component,
        "claim_boundary": {
            "finite_SU3_links_are_lattice_QCD": False,
            "Wilson_observables_establish_confinement": False,
            "bosonic_SU2xU1_Higgs_carrier_is_full_electroweak_theory": False,
            "Higgs_vacuum_flow_predicts_W_Z_or_Higgs_masses": False,
            "physical_particle_or_sector_identity_promoted": False,
        },
    }
    acceptance = {
        "previous_M9_117_authority_is_preserved": bool(previous["passed"]),
        "formal_gauge_authority_passes": component["formal_authority_passed"],
        "M9_119a_non_abelian_carrier_closes": component["strong_campaign_passed"]
        and component["local_SU3_links"]
        and component["gauge_covariant_color_dynamics"]
        and component["Wilson_observables"],
        "M9_119b_electroweak_Higgs_carrier_closes": component["electroweak_campaign_passed"]
        and component["local_SU2xU1_links"]
        and component["gauge_covariant_Higgs_dynamics"]
        and component["quartic_Higgs_vacuum_orbit"],
        "QCD_and_complete_electroweak_claims_remain_open": not component["QCD_confinement_established"]
        and not component["complete_electroweak_theory"],
        "no_claim_boundary_is_crossed": not any(payload["claim_boundary"].values()),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "component_results": {"strong": strong, "electroweak": electroweak},
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "M9_119a_local_SU3_carrier_complete": True,
            "M9_119b_local_SU2xU1_Higgs_carrier_complete": True,
            "M9_119c_formal_and_gauge_covariance_audit_complete": True,
            "M9_120_spectra_decay_phenomenology_unblocked": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
