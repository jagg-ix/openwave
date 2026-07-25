"""README/MODELS-aligned CAT/EPT conformance profile through M9.86."""
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
    C("charge_quantization", "particles", "Charge quantization", "partial", (ROOT + "topological_charge.py", FINDINGS + "m9_26_method_note.md"), "Integer winding is field-derived and robust, but the sector is seeded and is not identified with elementary electric charge."),
    C("electron_rest_energy", "particles", "Electron rest energy (mass)", "partial", (ROOT + "scale_selection.py", FINDINGS + "m9_27_method_note.md", ROOT + "physical_calibration_ledger.py", FINDINGS + "m9_62_method_note.md"), "A dimensionless interior scale and localized branch exist. The mass anchor remains calibration-required; no out-of-sample rest-mass prediction is established."),
    C("de_broglie_clock", "particles", "de Broglie clock (Zitterbewegung)", "partial", (ROOT + "intrinsic_clock_reduction.py", ROOT + "imaginary_action_backreaction.py", ROOT + "entropic_integrator.py", ROOT + "physical_calibration_ledger.py", ROOT + "preregistered_breathing_prediction.py", ROOT + "independent_breathing_comparison.py", ROOT + "replacement_mode_prediction.py", ROOT + "independent_mode_robustness.py", ROOT + "minimizing_orbit_identification.py", FINDINGS + "m9_65_method_note.md", FINDINGS + "m9_68_method_note.md", FINDINGS + "m9_71_method_note.md", FINDINGS + "m9_74_method_note.md", FINDINGS + "m9_80_method_note.md", FORMAL_STATUS), "PhysLib proves a scoped operational entropic/physical proper-time equality. The M9.65 Gaussian breathing prediction fails its no-refit comparison. The M9.71 stationary-branch ratio 1.074356835825 passes held-out grids and the independent M9.74 radial-amplitude/periodogram test. M9.80 preserves the immutable record but blocks external comparison until analytic branch identity, particle identity, independent calibration, and an external dataset exist. No physical Zitterbewegung identification is established."),
    C("particle_stability", "particles", "Particle stability (Derrick escape)", "partial", (ROOT + "minimizer_3d.py", ROOT + "stability_campaign_3d.py", ROOT + "unified_self_binding_3d.py", ROOT + "non_gaussian_self_binding.py", ROOT + "action_derived_binding.py", ROOT + "binding_axiom_selection.py", ROOT + "orbital_compactness_bridge.py", ROOT + "coefficient_self_consistency.py", ROOT + "cubic_quintic_continuum.py", ROOT + "selection_condition_derivation_audit.py", ROOT + "h1_orbital_adversarial.py", ROOT + "stationary_non_gaussian_branch.py", ROOT + "h1_kernel_certificate.py", ROOT + "h1_concentration_closure.py", ROOT + "hminus_one_mild_flow_audit.py", ROOT + "recentered_compactness_audit.py", ROOT + "global_mild_orbit_campaign.py", ROOT + "duhamel_fixed_point_campaign.py", ROOT + "recentered_conservation_closure.py", ROOT + "minimizing_orbit_identification.py", ROOT + "rellich_hartree_closure.py", ROOT + "local_interaction_no_loss_closure.py", ROOT + "branch_identity_certificate.py", FINDINGS + "m9_49_method_note.md", FINDINGS + "m9_52_method_note.md", FINDINGS + "m9_59_method_note.md", FINDINGS + "m9_60_method_note.md", FINDINGS + "m9_61_method_note.md", FINDINGS + "m9_63_method_note.md", FINDINGS + "m9_64_method_note.md", FINDINGS + "m9_66_method_note.md", FINDINGS + "m9_67_method_note.md", FINDINGS + "m9_69_method_note.md", FINDINGS + "m9_70_method_note.md", FINDINGS + "m9_72_method_note.md", FINDINGS + "m9_73_method_note.md", FINDINGS + "m9_75_method_note.md", FINDINGS + "m9_76_method_note.md", FINDINGS + "m9_77_method_note.md", FINDINGS + "m9_78_method_note.md", FINDINGS + "m9_79_method_note.md", FINDINGS + "m9_80_method_note.md", FINDINGS + "m9_84_method_note.md", FINDINGS + "m9_85_method_note.md", FINDINGS + "m9_86_method_note.md"), "The original action disperses, while M9.69 constructs a localized non-Gaussian stationary branch. The live formal stack proves the complete H1/Born carrier, interaction no-loss, compact minimizing orbits, orbital-stability composition, and now the local-Rellich plus recentered-tail plus L3 route to strong L^(6/5) Born-density and Hartree convergence. M9.78-M9.80 qualify finite Duhamel evolution, dynamic recentering, conservation, and local minimizing-orbit curvature. M9.84 executes the new Rellich, tail, interpolation, L^(6/5), and Hartree premises on four nested grids. M9.85 qualifies quartic/sextic local interaction convergence, combined target-interaction convergence, normalization, energy-split closure, and decreasing H1 no-loss distance. M9.86 freezes a reproducible 32-cubed branch feature fingerprint and obtains improving nested-grid and independent-seed candidate identity. The continuum energy-critical Duhamel theorem, model-level Rellich/tightness and local-interaction proofs, continuum conservation, analytic minimizing-orbit identity, calibration, and a physical particle remain open."),
    C("magnetic_moment_spin", "particles", "Magnetic moment and spin J", "partial", (ROOT + "spin_magnetic_observables.py", FINDINGS + "m9_29_method_note.md", ROOT + "physical_calibration_ledger.py"), "Spin and Pauli-current magnetic-moment controls exist; no stable calibrated state or emergent electron g factor is established."),
    C("spin_half_statistics", "particles", "Spin-1/2 statistics (720-degree return)", "validated", (ROOT + "spin_magnetic_observables.py", ROOT + "spin_statistics_closure.py", FINDINGS + "m9_29_method_note.md", FINDINGS + "m9_81_method_note.md", FORMAL_STATUS), "Validated in-platform for the literal criterion: the localized spinor changes sign after 2pi and returns after 4pi; the two-state amplitude is antisymmetric under exchange; identical-state antisymmetrization vanishes; and PhysLib supplies the fermion exchange phase minus one. The fermionic assignment of a specific CAT/EPT particle and physical electron identity are not derived."),
    C("antimatter_annihilation", "particles", "Antimatter and annihilation", "partial", (ROOT + "capture_annihilation.py", FINDINGS + "m9_31_method_note.md"), "A reduced opposite-sector model captures, annihilates, and transfers energy to radiation; full-PDE particle annihilation is not established."),
    C("lepton_mass_spectrum", "particles", "Lepton mass spectrum (mu, tau)", "negative", (ROOT + "lepton_hierarchy_audit.py", FINDINGS + "m9_39_method_note.md", ROOT + "physical_calibration_ledger.py"), "Tested low-parameter hierarchy laws fail predictive gates; no out-of-sample muon/tau hierarchy with residual degrees of freedom is selected."),
    C("dark_matter", "particles", "Dark matter candidate", "partial", (ROOT + "dark_sector_survey.py", FINDINGS + "m9_45_method_note.md"), "A neutral fixed-charge variational candidate exists; full-PDE stability, abundance, and phenomenology remain open."),
    C("quarks", "particles", "Quarks", "partial", (ROOT + "quark_color_sector.py", FINDINGS + "m9_46_method_note.md", ROOT + "research/zil/m9_46_quark_color.zc"), "Finite SU(3), singlet, Wilson-loop, fractional-charge, and CKM controls exist; dynamical QCD and physical hadron spectra remain open."),
    C("baryons", "particles", "Baryons (p, n)", "partial", (ROOT + "composite_graph.py", FINDINGS + "m9_33_method_note.md"), "A charged-triplet graph binds and preserves ledgers, but no physical baryon spectrum or quark dynamics is established."),
    C("mesons", "particles", "Mesons (pi, K)", "partial", (ROOT + "composite_graph.py", FINDINGS + "m9_33_method_note.md"), "A neutral-pair graph binds and preserves ledgers, but no physical meson spectrum or decay channel is established."),
    C("electric_force", "forces", "Electric force (Coulomb 1/r)", "partial", (ROOT + "two_body_forces.py", ROOT + "spatial_3d_maxwell_dirac.py", FINDINGS + "m9_30_method_note.md", ROOT + "physical_calibration_ledger.py"), "A regularized inverse-square asymptote exists; a force between calibrated stable emergent charges remains open."),
    C("magnetic_force", "forces", "Magnetic force", "partial", (ROOT + "two_body_forces.py", ROOT + "spin_magnetic_observables.py", ROOT + "spatial_3d_maxwell_dirac.py", FINDINGS + "m9_30_method_note.md"), "A regularized dipole r^-4 asymptote exists; a calibrated particle-level magnetic interaction remains open."),
    C("strong_force", "forces", "Strong force / confinement", "partial", (ROOT + "confinement_sector.py", FINDINGS + "m9_40_method_note.md"), "Cornell/flux-tube and string-breaking controls exist; dynamical QCD and jointly predicted tension/breaking remain open."),
    C("weak_force", "forces", "Weak force", "partial", (ROOT + "weak_chiral_sector.py", FINDINGS + "m9_41_method_note.md"), "A reduced left-selective transition/decay ledger exists; electroweak gauge dynamics and physical rates remain open."),
    C("gravity", "forces", "Gravity", "partial", (ROOT + "geometry_backreaction.py", ROOT + "equivalence_principle.py", ROOT + "formal_action_generator_bridge.py", ROOT + "physical_calibration_ledger.py", FORMAL_STATUS), "OpenWave has weak-field and equivalence-principle controls. PhysLib provides scoped metric-built Einstein-Maxwell-entropic action/PDE, ADM, maximal-development, cubic-semiflow, H1 variational, and clock interfaces. A calibrated coupled physical evolution remains open."),
    C("em_waves", "waves", "EM waves (Maxwell)", "validated", (ROOT + "wave_reductions.py", ROOT + "spatial_3d_controls.py", ROOT + "formal_action_generator_bridge.py", ROOT + "maxwell_wave_closure.py", FINDINGS + "m9_82_method_note.md", FORMAL_STATUS), "Validated in-platform for the literal free-wave criterion: OpenWave supplies exact transverse Maxwell evolution with energy, speed, massless-wave, and resolution controls; PhysLib constructs a smooth source-free harmonic solution and proves it is a plane wave. Photon quantization, emergence from the full coupled CAT/EPT dynamics, and physical-unit calibration remain open."),
    C("klein_gordon", "waves", "Quantum wave equation (Klein-Gordon)", "partial", (ROOT + "wave_reductions.py", FINDINGS + "m9_43_method_note.md"), "A massive spectral dispersion reduction exists; a native calibrated particle sector remains open."),
    C("orbital_quantization", "waves", "Orbital quantization (atomic structure)", "partial", (ROOT + "orbital_quantization.py", FINDINGS + "m9_32_method_note.md"), "A converged Coulomb-like radial ladder exists; native calibrated atomic structure remains open."),
    C("thermal_field", "thermal", "Heat / thermal-field sector", "validated", (ROOT + "thermal_field.py", ROOT + "thermal_sector_closure.py", FINDINGS + "m9_44_method_note.md", FINDINGS + "m9_83_method_note.md", ROOT + "physical_calibration_ledger.py", FORMAL_STATUS), "Validated in-platform for the explicit dimensionless thermal criterion: exact spectral heat flow conserves total heat, increases entropy, dissipates variance, obeys mode-decay and semigroup laws, freezes at zero diffusivity, and is resolution stable; PhysLib formalizes the finite spectral heat semigroup and zero-mode conservation. Microscopic CAT/EPT thermodynamics, material calibration, quantum thermalization, and relativistic heat conduction remain open."),
)

EXPECTED_VISIBLE_CRITERIA = 21
DOCUMENTED_SUMMARY_TOTAL = 21
MISSING_EXPLICIT_CRITERION = None
PROMOTED_KEYS = {"spin_half_statistics", "em_waves", "thermal_field"}


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
    return {"schema": "openwave.m9.models-conformance.v10", "model": "M9 CAT/EPT", "criteria": [asdict(item) for item in CRITERIA], "audit": validate_profile()}


def fingerprint() -> str:
    return sha256(json.dumps(canonical_payload(), sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run_conformance_study() -> dict[str, Any]:
    payload = canonical_payload()
    by_key = {item["key"]: item for item in payload["criteria"]}
    stability = by_key["particle_stability"]
    acceptance = {
        "all_explicit_rows_covered": payload["audit"]["criterion_count"] == 21,
        "domain_partition_closes": payload["audit"]["domain_counts"] == {"particles": 12, "forces": 5, "waves": 3, "thermal": 1},
        "nonplanned_cells_have_evidence": all(item["status"] == "not_yet" or bool(item["evidence"]) for item in payload["criteria"]),
        "single_honest_negative_preserved": sum(item["status"] == "negative" for item in payload["criteria"]) == 1,
        "summary_total_closes": payload["audit"]["matrix_total_mismatch"] == 0,
        "deterministic_fingerprint": fingerprint() == fingerprint(),
        "m9_86_status_counts": payload["audit"]["status_counts"] == {"validated": 3, "partial": 17, "negative": 1, "not_yet": 0},
        "exactly_the_audited_three_rows_are_validated": {item["key"] for item in payload["criteria"] if item["status"] == "validated"} == PROMOTED_KEYS,
        "m9_84_86_stability_evidence_present": all(any(name in path for path in stability["evidence"]) for name in ("m9_84_method_note.md", "m9_85_method_note.md", "m9_86_method_note.md")),
        "rellich_and_branch_work_not_promoted_to_continuum": "continuum energy-critical Duhamel theorem" in stability["finding"] and "analytic minimizing-orbit identity" in stability["finding"],
        "spin_promotion_keeps_particle_identity_boundary": "not derived" in by_key["spin_half_statistics"]["finding"],
        "maxwell_promotion_keeps_photon_boundary": "Photon quantization" in by_key["em_waves"]["finding"],
        "thermal_promotion_keeps_microscopic_boundary": "Microscopic CAT/EPT thermodynamics" in by_key["thermal_field"]["finding"],
        "internal_mode_success_not_promoted_to_validation": by_key["de_broglie_clock"]["status"] == "partial",
    }
    return {**payload, "fingerprint": fingerprint(), "acceptance": acceptance, "passed": all(acceptance.values()), "repository_profile": "MODELS_M9.md"}


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
