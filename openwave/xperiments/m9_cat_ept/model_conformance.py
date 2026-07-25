"""README/MODELS-aligned CAT/EPT conformance profile through M9.92."""
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
C = Criterion

CRITERIA: tuple[Criterion, ...] = (
    C("charge_quantization", "particles", "Charge quantization", "validated", (
        ROOT + "topological_charge.py", ROOT + "charge_quantization_closure.py",
        FINDINGS + "m9_26_method_note.md", FINDINGS + "m9_90_method_note.md", FORMAL_STATUS),
      "Validated in-platform for the literal quantization criterion. The field-derived winding is integer-valued, contour/phase/resolution/perturbation robust, additive, conjugation odd, and quantized in thirds with an exact Fock-space charge grading. The winding unit is not thereby identified with a measured elementary electric charge, and spontaneous sector selection is not derived."),
    C("electron_rest_energy", "particles", "Electron rest energy (mass)", "partial", (ROOT + "scale_selection.py", FINDINGS + "m9_27_method_note.md", ROOT + "physical_calibration_ledger.py", FINDINGS + "m9_62_method_note.md"), "A dimensionless interior scale and localized branch exist. The mass anchor remains calibration-required; no out-of-sample rest-mass prediction is established."),
    C("de_broglie_clock", "particles", "de Broglie clock (Zitterbewegung)", "partial", (ROOT + "intrinsic_clock_reduction.py", ROOT + "replacement_mode_prediction.py", ROOT + "independent_mode_robustness.py", ROOT + "minimizing_orbit_identification.py", FINDINGS + "m9_65_method_note.md", FINDINGS + "m9_68_method_note.md", FINDINGS + "m9_71_method_note.md", FINDINGS + "m9_74_method_note.md", FINDINGS + "m9_80_method_note.md", FORMAL_STATUS), "PhysLib proves a scoped operational entropic/physical proper-time equality. The first Gaussian prediction failed. The frozen stationary-branch ratio passes internal held-out tests, but physical Zitterbewegung identity, independent calibration, and external evidence remain open."),
    C("particle_stability", "particles", "Particle stability (Derrick escape)", "validated", (
        ROOT + "stationary_non_gaussian_branch.py", ROOT + "h1_concentration_closure.py",
        ROOT + "global_mild_orbit_campaign.py", ROOT + "duhamel_fixed_point_campaign.py",
        ROOT + "recentered_conservation_closure.py", ROOT + "minimizing_orbit_identification.py",
        ROOT + "rellich_hartree_closure.py", ROOT + "local_interaction_no_loss_closure.py",
        ROOT + "branch_identity_certificate.py", ROOT + "live_flow_construction.py",
        ROOT + "conservative_flow_composition.py", ROOT + "identified_standing_wave_orbit.py",
        FINDINGS + "m9_69_method_note.md", FINDINGS + "m9_72_method_note.md",
        FINDINGS + "m9_73_method_note.md", FINDINGS + "m9_75_method_note.md",
        FINDINGS + "m9_76_method_note.md", FINDINGS + "m9_77_method_note.md",
        FINDINGS + "m9_78_method_note.md", FINDINGS + "m9_79_method_note.md",
        FINDINGS + "m9_80_method_note.md", FINDINGS + "m9_84_method_note.md",
        FINDINGS + "m9_85_method_note.md", FINDINGS + "m9_86_method_note.md",
        FINDINGS + "m9_87_method_note.md", FINDINGS + "m9_88_method_note.md",
        FINDINGS + "m9_89_method_note.md", FORMAL_STATUS),
      "Validated in-platform for the literal Derrick-escape criterion. The live formal stack contains the complete H1 carrier, genuine free H1 unitary group, localized Rellich/Hartree/no-loss chain, compact minimizing orbit, uniform orbital-stability theorem, and identified-branch constructor. OpenWave constructs the global spectral split flow, preserves mass, obtains second-order energy refinement, keeps chirp/radial/quadrupole/noise perturbations in bounded localized H1 tubes, and evolves M9.69 in one computed standing-wave phase orbit on nested grids. This is not physical-particle identification, calibration, external validation, or a claim that every continuum nonlinear model is globally well posed."),
    C("magnetic_moment_spin", "particles", "Magnetic moment and spin J", "partial", (ROOT + "spin_magnetic_observables.py", FINDINGS + "m9_29_method_note.md", ROOT + "physical_calibration_ledger.py"), "Spin and Pauli-current magnetic-moment controls exist; an emergent calibrated electron g factor remains open."),
    C("spin_half_statistics", "particles", "Spin-1/2 statistics (720-degree return)", "validated", (ROOT + "spin_magnetic_observables.py", ROOT + "spin_statistics_closure.py", FINDINGS + "m9_81_method_note.md", FORMAL_STATUS), "Validated in-platform for the literal criterion: 2pi sign reversal, 4pi return, fermion exchange phase minus one, antisymmetry, exchange involution, and identical-state exclusion close. Physical electron identity is not derived."),
    C("antimatter_annihilation", "particles", "Antimatter and annihilation", "partial", (ROOT + "capture_annihilation.py", FINDINGS + "m9_31_method_note.md"), "A reduced opposite-sector model captures, annihilates, and transfers energy to radiation; full-PDE particle annihilation is not established."),
    C("lepton_mass_spectrum", "particles", "Lepton mass spectrum (mu, tau)", "negative", (ROOT + "lepton_hierarchy_audit.py", FINDINGS + "m9_39_method_note.md", ROOT + "physical_calibration_ledger.py"), "Tested low-parameter hierarchy laws fail predictive gates; no out-of-sample muon/tau hierarchy is selected."),
    C("dark_matter", "particles", "Dark matter candidate", "partial", (ROOT + "dark_sector_survey.py", FINDINGS + "m9_45_method_note.md"), "A neutral fixed-charge variational candidate exists; abundance and phenomenology remain open."),
    C("quarks", "particles", "Quarks", "partial", (ROOT + "quark_color_sector.py", FINDINGS + "m9_46_method_note.md", ROOT + "research/zil/m9_46_quark_color.zc"), "Finite SU(3), singlet, Wilson-loop, fractional-charge, and CKM controls exist; dynamical QCD and physical hadron spectra remain open."),
    C("baryons", "particles", "Baryons (p, n)", "partial", (ROOT + "composite_graph.py", FINDINGS + "m9_33_method_note.md"), "A charged-triplet graph binds and preserves ledgers, but no physical baryon spectrum or quark dynamics is established."),
    C("mesons", "particles", "Mesons (pi, K)", "partial", (ROOT + "composite_graph.py", FINDINGS + "m9_33_method_note.md"), "A neutral-pair graph binds and preserves ledgers, but no physical meson spectrum or decay channel is established."),
    C("electric_force", "forces", "Electric force (Coulomb 1/r)", "partial", (ROOT + "two_body_forces.py", ROOT + "spatial_3d_maxwell_dirac.py", FINDINGS + "m9_30_method_note.md", ROOT + "physical_calibration_ledger.py"), "A regularized inverse-square asymptote exists; a force between calibrated stable emergent charges remains open."),
    C("magnetic_force", "forces", "Magnetic force", "partial", (ROOT + "two_body_forces.py", ROOT + "spin_magnetic_observables.py", ROOT + "spatial_3d_maxwell_dirac.py", FINDINGS + "m9_30_method_note.md"), "A regularized dipole r^-4 asymptote exists; a calibrated particle-level magnetic interaction remains open."),
    C("strong_force", "forces", "Strong force / confinement", "partial", (ROOT + "confinement_sector.py", FINDINGS + "m9_40_method_note.md"), "Cornell/flux-tube and string-breaking controls exist; dynamical QCD and jointly predicted tension/breaking remain open."),
    C("weak_force", "forces", "Weak force", "partial", (ROOT + "weak_chiral_sector.py", FINDINGS + "m9_41_method_note.md"), "A reduced left-selective transition/decay ledger exists; electroweak gauge dynamics and physical rates remain open."),
    C("gravity", "forces", "Gravity", "partial", (ROOT + "geometry_backreaction.py", ROOT + "equivalence_principle.py", ROOT + "formal_action_generator_bridge.py", ROOT + "physical_calibration_ledger.py", FORMAL_STATUS), "Weak-field and equivalence-principle controls and scoped Einstein-Maxwell-entropic interfaces exist. A calibrated coupled physical evolution remains open."),
    C("em_waves", "waves", "EM waves (Maxwell)", "validated", (ROOT + "wave_reductions.py", ROOT + "maxwell_wave_closure.py", FINDINGS + "m9_82_method_note.md", FORMAL_STATUS), "Validated in-platform for the literal free-wave criterion. Photon quantization, full coupled emergence, and physical-unit calibration remain open."),
    C("klein_gordon", "waves", "Quantum wave equation (Klein-Gordon)", "validated", (ROOT + "wave_reductions.py", ROOT + "klein_gordon_closure.py", FINDINGS + "m9_43_method_note.md", FINDINGS + "m9_91_method_note.md", FORMAL_STATUS), "Validated in-platform for the free massive Klein-Gordon criterion. Exact spectral evolution conserves energy, closes the massive dispersion and massless limit, and independently satisfies finite-mode composition, reversal, and quadratic-energy gates. Interacting scalar QFT, physical particle identity, and mass calibration remain open."),
    C("orbital_quantization", "waves", "Orbital quantization (atomic structure)", "validated", (ROOT + "orbital_quantization.py", ROOT + "orbital_quantization_closure.py", FINDINGS + "m9_32_method_note.md", FINDINGS + "m9_92_method_note.md", FORMAL_STATUS), "Validated in-platform for dimensionless Coulomb orbital quantization. The radial hydrogenic ladder, integer nodes, orthogonality, stationarity, refinement, domain stability, and 2s/2p and 3s/3p/3d degeneracies close, with formal Coulomb/O(4)/Gegenbauer support. Emergent particles, radiative transitions, and physical atomic units remain open."),
    C("thermal_field", "thermal", "Heat / thermal-field sector", "validated", (ROOT + "thermal_field.py", ROOT + "thermal_sector_closure.py", FINDINGS + "m9_83_method_note.md", FORMAL_STATUS), "Validated in-platform for the explicit dimensionless thermal criterion. Microscopic CAT/EPT thermodynamics, material calibration, quantum thermalization, and relativistic heat conduction remain open."),
)

EXPECTED_VISIBLE_CRITERIA = 21
DOCUMENTED_SUMMARY_TOTAL = 21
MISSING_EXPLICIT_CRITERION = None
PROMOTED_KEYS = {
    "charge_quantization",
    "particle_stability",
    "spin_half_statistics",
    "em_waves",
    "klein_gordon",
    "orbital_quantization",
    "thermal_field",
}


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
    return {"schema": "openwave.m9.models-conformance.v12", "model": "M9 CAT/EPT", "criteria": [asdict(item) for item in CRITERIA], "audit": validate_profile()}


def fingerprint() -> str:
    return sha256(json.dumps(canonical_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_conformance_study() -> dict[str, Any]:
    payload = canonical_payload()
    by_key = {item["key"]: item for item in payload["criteria"]}
    acceptance = {
        "all_explicit_rows_covered": payload["audit"]["criterion_count"] == 21,
        "domain_partition_closes": payload["audit"]["domain_counts"] == {"particles": 12, "forces": 5, "waves": 3, "thermal": 1},
        "nonplanned_cells_have_evidence": all(item["status"] == "not_yet" or bool(item["evidence"]) for item in payload["criteria"]),
        "single_honest_negative_preserved": sum(item["status"] == "negative" for item in payload["criteria"]) == 1,
        "summary_total_closes": payload["audit"]["matrix_total_mismatch"] == 0,
        "deterministic_fingerprint": fingerprint() == fingerprint(),
        "m9_92_status_counts": payload["audit"]["status_counts"] == {"validated": 7, "partial": 13, "negative": 1, "not_yet": 0},
        "exactly_the_audited_seven_rows_are_validated": {item["key"] for item in payload["criteria"] if item["status"] == "validated"} == PROMOTED_KEYS,
        "charge_promotion_keeps_identity_boundary": "not thereby identified" in by_key["charge_quantization"]["finding"],
        "klein_gordon_promotion_keeps_interaction_boundary": "Interacting scalar QFT" in by_key["klein_gordon"]["finding"],
        "orbital_promotion_keeps_physical_boundary": "Emergent particles" in by_key["orbital_quantization"]["finding"],
        "stability_promotion_keeps_physical_boundary": "not physical-particle identification" in by_key["particle_stability"]["finding"],
        "spin_promotion_keeps_particle_identity_boundary": "Physical electron identity" in by_key["spin_half_statistics"]["finding"],
        "maxwell_promotion_keeps_photon_boundary": "Photon quantization" in by_key["em_waves"]["finding"],
        "thermal_promotion_keeps_microscopic_boundary": "Microscopic CAT/EPT thermodynamics" in by_key["thermal_field"]["finding"],
        "internal_mode_success_not_promoted_to_validation": by_key["de_broglie_clock"]["status"] == "partial",
    }
    return {**payload, "fingerprint": fingerprint(), "acceptance": acceptance, "passed": all(acceptance.values()), "repository_profile": "MODELS_M9.md"}


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
