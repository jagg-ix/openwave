"""README/MODELS-aligned CAT/EPT conformance profile through M9.65."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Literal

Status = Literal["validated", "partial", "negative", "not_yet"]


@dataclass(frozen=True)
class Criterion:
    key: str
    domain: str
    label: str
    status: Status
    evidence: tuple[str, ...]
    finding: str


ROOT = "openwave/xperiments/m9_cat_ept/"
FINDINGS = ROOT + "research/findings/"
FORMAL_STATUS = ROOT + "research/formal_status_matrix.md"

CRITERIA: tuple[Criterion, ...] = (
    Criterion("charge_quantization", "particles", "Charge quantization", "partial", (ROOT + "topological_charge.py", FINDINGS + "m9_26_method_note.md"), "Integer winding is field-derived and robust, but the sector is seeded and is not identified with elementary electric charge."),
    Criterion("electron_rest_energy", "particles", "Electron rest energy (mass)", "partial", (ROOT + "scale_selection.py", FINDINGS + "m9_27_method_note.md", ROOT + "physical_calibration_ledger.py", FINDINGS + "m9_62_method_note.md"), "A dimensionless interior scale and localized branch exist. The mass anchor remains calibration-required; no out-of-sample rest-mass prediction is established."),
    Criterion("de_broglie_clock", "particles", "de Broglie clock (Zitterbewegung)", "partial", (ROOT + "intrinsic_clock_reduction.py", ROOT + "imaginary_action_backreaction.py", ROOT + "entropic_integrator.py", ROOT + "physical_calibration_ledger.py", ROOT + "preregistered_breathing_prediction.py", FINDINGS + "m9_65_method_note.md", FORMAL_STATUS), "PhysLib proves a scoped operational entropic/physical proper-time equality under its explicit action-rate calibration. M9.65 freezes a breathing-frequency/Compton-frequency ratio, but it is untested and is not yet a physical Zitterbewegung identification."),
    Criterion("particle_stability", "particles", "Particle stability (Derrick escape)", "partial", (ROOT + "minimizer_3d.py", ROOT + "stability_campaign_3d.py", ROOT + "unified_self_binding_3d.py", ROOT + "non_gaussian_self_binding.py", ROOT + "action_derived_binding.py", ROOT + "binding_axiom_selection.py", ROOT + "orbital_compactness_bridge.py", ROOT + "coefficient_self_consistency.py", ROOT + "cubic_quintic_continuum.py", FINDINGS + "m9_49_method_note.md", FINDINGS + "m9_52_method_note.md", FINDINGS + "m9_59_method_note.md", FINDINGS + "m9_60_method_note.md", FINDINGS + "m9_61_method_note.md", FINDINGS + "m9_63_method_note.md", FINDINGS + "m9_64_method_note.md"), "The original action disperses. M9.63 selects a coefficient pair under two declared self-consistency conditions and retains the finite-grid branch. M9.64 adds an exact coercive energy bound, nested mass/energy-stable flow, and bounded small scale perturbations. A kernel theorem for every H1 perturbation and a physical particle remain open."),
    Criterion("magnetic_moment_spin", "particles", "Magnetic moment and spin J", "partial", (ROOT + "spin_magnetic_observables.py", FINDINGS + "m9_29_method_note.md", ROOT + "physical_calibration_ledger.py"), "Spin and Pauli-current magnetic-moment controls exist; no stable calibrated state or emergent electron g factor is established."),
    Criterion("spin_half_statistics", "particles", "Spin-1/2 statistics (720-degree return)", "partial", (ROOT + "spin_magnetic_observables.py", FINDINGS + "m9_29_method_note.md"), "The spinor changes sign after 2pi and returns after 4pi, but exchange antisymmetry is not established."),
    Criterion("antimatter_annihilation", "particles", "Antimatter and annihilation", "partial", (ROOT + "capture_annihilation.py", FINDINGS + "m9_31_method_note.md"), "A reduced opposite-sector model captures, annihilates, and transfers energy to radiation; full-PDE particle annihilation is not established."),
    Criterion("lepton_mass_spectrum", "particles", "Lepton mass spectrum (mu, tau)", "negative", (ROOT + "lepton_hierarchy_audit.py", FINDINGS + "m9_39_method_note.md", ROOT + "physical_calibration_ledger.py"), "Tested low-parameter hierarchy laws fail predictive gates; no out-of-sample muon/tau hierarchy with residual degrees of freedom is selected."),
    Criterion("dark_matter", "particles", "Dark matter candidate", "partial", (ROOT + "dark_sector_survey.py", FINDINGS + "m9_45_method_note.md"), "A neutral fixed-charge variational candidate exists; full-PDE stability, abundance, and phenomenology remain open."),
    Criterion("quarks", "particles", "Quarks", "partial", (ROOT + "quark_color_sector.py", FINDINGS + "m9_46_method_note.md", ROOT + "research/zil/m9_46_quark_color.zc"), "Finite SU(3), singlet, Wilson-loop, fractional-charge, and CKM controls exist; dynamical QCD and physical hadron spectra remain open."),
    Criterion("baryons", "particles", "Baryons (p, n)", "partial", (ROOT + "composite_graph.py", FINDINGS + "m9_33_method_note.md"), "A charged-triplet graph binds and preserves ledgers, but no physical baryon spectrum or quark dynamics is established."),
    Criterion("mesons", "particles", "Mesons (pi, K)", "partial", (ROOT + "composite_graph.py", FINDINGS + "m9_33_method_note.md"), "A neutral-pair graph binds and preserves ledgers, but no physical meson spectrum or decay channel is established."),
    Criterion("electric_force", "forces", "Electric force (Coulomb 1/r)", "partial", (ROOT + "two_body_forces.py", ROOT + "spatial_3d_maxwell_dirac.py", FINDINGS + "m9_30_method_note.md", ROOT + "physical_calibration_ledger.py"), "A regularized inverse-square asymptote exists; a force between calibrated stable emergent charges remains open."),
    Criterion("magnetic_force", "forces", "Magnetic force", "partial", (ROOT + "two_body_forces.py", ROOT + "spin_magnetic_observables.py", ROOT + "spatial_3d_maxwell_dirac.py", FINDINGS + "m9_30_method_note.md"), "A regularized dipole r^-4 asymptote exists; a calibrated particle-level magnetic interaction remains open."),
    Criterion("strong_force", "forces", "Strong force / confinement", "partial", (ROOT + "confinement_sector.py", FINDINGS + "m9_40_method_note.md"), "Cornell/flux-tube and string-breaking controls exist; dynamical QCD and jointly predicted tension/breaking remain open."),
    Criterion("weak_force", "forces", "Weak force", "partial", (ROOT + "weak_chiral_sector.py", FINDINGS + "m9_41_method_note.md"), "A reduced left-selective transition/decay ledger exists; electroweak gauge dynamics and physical rates remain open."),
    Criterion("gravity", "forces", "Gravity", "partial", (ROOT + "geometry_backreaction.py", ROOT + "equivalence_principle.py", ROOT + "formal_action_generator_bridge.py", ROOT + "physical_calibration_ledger.py", FORMAL_STATUS), "OpenWave has weak-field and equivalence-principle controls. PhysLib provides scoped metric-built Einstein-Maxwell-entropic action/PDE, ADM, maximal-development, and clock interfaces. A calibrated coupled physical evolution remains open."),
    Criterion("em_waves", "waves", "EM waves (Maxwell)", "partial", (ROOT + "wave_reductions.py", ROOT + "spatial_3d_controls.py", ROOT + "formal_action_generator_bridge.py", FORMAL_STATUS), "Transverse Maxwell and massless reductions are computationally qualified; scoped intrinsic/distributional formal interfaces exist. Common calibrated Cauchy data remain open."),
    Criterion("klein_gordon", "waves", "Quantum wave equation (Klein-Gordon)", "partial", (ROOT + "wave_reductions.py", FINDINGS + "m9_43_method_note.md"), "A massive spectral dispersion reduction exists; a native calibrated particle sector remains open."),
    Criterion("orbital_quantization", "waves", "Orbital quantization (atomic structure)", "partial", (ROOT + "orbital_quantization.py", FINDINGS + "m9_32_method_note.md"), "A converged Coulomb-like radial ladder exists; native calibrated atomic structure remains open."),
    Criterion("thermal_field", "thermal", "Heat / thermal-field sector", "partial", (ROOT + "thermal_field.py", FINDINGS + "m9_44_method_note.md", ROOT + "physical_calibration_ledger.py"), "Heat conservation, entropy growth, and diffusion-dissipation controls exist; calibrated microscopic CAT/EPT thermodynamics remain open."),
)

EXPECTED_VISIBLE_CRITERIA = 21
DOCUMENTED_SUMMARY_TOTAL = 21
MISSING_EXPLICIT_CRITERION = None


def validate_profile(criteria: tuple[Criterion, ...] = CRITERIA) -> dict[str, Any]:
    keys = [item.key for item in criteria]
    labels = [item.label for item in criteria]
    if len(keys) != len(set(keys)) or len(labels) != len(set(labels)):
        raise ValueError("duplicate criterion")
    if len(criteria) != EXPECTED_VISIBLE_CRITERIA:
        raise ValueError("profile must cover 21 explicit rows")
    if any(item.status != "not_yet" and not item.evidence for item in criteria):
        raise ValueError("non-planned status lacks evidence")
    domains = {domain: sum(item.domain == domain for item in criteria) for domain in ("particles", "forces", "waves", "thermal")}
    counts = {status: sum(item.status == status for item in criteria) for status in ("validated", "partial", "negative", "not_yet")}
    return {"valid": True, "criterion_count": len(criteria), "domain_counts": domains, "status_counts": counts, "documented_summary_total": DOCUMENTED_SUMMARY_TOTAL, "matrix_total_mismatch": DOCUMENTED_SUMMARY_TOTAL - len(criteria), "missing_explicit_criterion": MISSING_EXPLICIT_CRITERION}


def canonical_payload() -> dict[str, Any]:
    return {"schema": "openwave.m9.models-conformance.v4", "model": "M9 CAT/EPT", "criteria": [asdict(item) for item in CRITERIA], "audit": validate_profile()}


def fingerprint() -> str:
    return sha256(json.dumps(canonical_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_conformance_study() -> dict[str, Any]:
    payload = canonical_payload()
    stability = next(item for item in payload["criteria"] if item["key"] == "particle_stability")
    clock = next(item for item in payload["criteria"] if item["key"] == "de_broglie_clock")
    acceptance = {
        "all_explicit_rows_covered": payload["audit"]["criterion_count"] == 21,
        "domain_partition_closes": payload["audit"]["domain_counts"] == {"particles": 12, "forces": 5, "waves": 3, "thermal": 1},
        "nonplanned_cells_have_evidence": all(item["status"] == "not_yet" or bool(item["evidence"]) for item in payload["criteria"]),
        "single_honest_negative_preserved": sum(item["status"] == "negative" for item in payload["criteria"]) == 1,
        "summary_total_closes": payload["audit"]["matrix_total_mismatch"] == 0,
        "thermal_criterion_is_explicit": any(item["key"] == "thermal_field" for item in payload["criteria"]),
        "deterministic_fingerprint": fingerprint() == fingerprint(),
        "m9_65_status_counts": payload["audit"]["status_counts"] == {"validated": 0, "partial": 20, "negative": 1, "not_yet": 0},
        "m9_63_64_stability_evidence_present": all(any(name in path for path in stability["evidence"]) for name in ("m9_63_method_note.md", "m9_64_method_note.md")),
        "m9_65_prediction_evidence_present": any("m9_65_method_note.md" in path for path in clock["evidence"]),
        "prediction_not_promoted_to_validation": clock["status"] == "partial",
    }
    return {**payload, "fingerprint": fingerprint(), "acceptance": acceptance, "passed": all(acceptance.values()), "repository_profile": "MODELS_M9.md"}


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
