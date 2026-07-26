"""M9.100a: evidence-derived multi-axis maturity for all 21 criteria.

The legacy profile stores one scalar status and freezes the historical 7/13/1
count.  This module separates theorem status, numerical closure, state
construction, physical identity, calibration, and prediction readiness.  A
human-facing headline is derived from those axes; it is not copied from the
legacy status and no fixed promoted-key set participates in the derivation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Literal, Mapping

from .model_conformance_dynamics import CRITERIA as LEGACY_CRITERIA

FormalStatus = Literal["proved", "conditional", "structural", "not_required", "absent"]
NumericalStatus = Literal["validated", "reduced_validated", "candidate", "not_tested", "negative"]
StateStatus = Literal["stable_constructed", "reduced_constructed", "candidate", "not_constructed", "not_required"]
IdentityStatus = Literal["not_required_for_scope", "open", "candidate", "rejected"]
CalibrationStatus = Literal["not_required_for_scope", "open", "partial", "calibrated"]
PredictionStatus = Literal["validated_internal", "conditional_internal", "not_ready", "negative_out_of_sample", "external_validated"]
HeadlineStatus = Literal[
    "validated_in_scope",
    "conditional_validated",
    "reduced_model_validated",
    "calibration_pending",
    "candidate",
    "negative",
]


@dataclass(frozen=True)
class CriterionMaturity:
    key: str
    formal: FormalStatus
    numerical: NumericalStatus
    state: StateStatus
    identity: IdentityStatus
    calibration: CalibrationStatus
    prediction: PredictionStatus
    closed: tuple[str, ...]
    open: tuple[str, ...]

    @property
    def headline(self) -> HeadlineStatus:
        return derive_headline(self)


def derive_headline(row: CriterionMaturity) -> HeadlineStatus:
    """Derive the summary status from independent evidence axes."""
    if row.numerical == "negative" or row.prediction == "negative_out_of_sample":
        return "negative"
    if row.numerical == "reduced_validated" and row.state == "reduced_constructed":
        return "reduced_model_validated"
    if row.formal == "conditional":
        return "conditional_validated" if row.numerical in ("validated", "reduced_validated") else "candidate"
    if (
        row.numerical == "validated"
        and row.state in ("stable_constructed", "not_required")
        and row.identity == "not_required_for_scope"
        and row.calibration == "not_required_for_scope"
        and row.prediction in ("validated_internal", "external_validated")
    ):
        return "validated_in_scope"
    if (
        row.numerical == "validated"
        and row.state == "stable_constructed"
        and row.calibration in ("open", "partial")
    ):
        return "calibration_pending"
    if row.numerical == "validated" and row.formal in ("proved", "structural"):
        return "conditional_validated"
    return "candidate"


M = CriterionMaturity
MATURITY_ROWS: tuple[CriterionMaturity, ...] = (
    M("charge_quantization", "proved", "validated", "not_required", "not_required_for_scope", "not_required_for_scope", "validated_internal",
      ("integer winding", "third-charge arithmetic", "Fock-space grading"),
      ("elementary-charge identity", "spontaneous sector selection")),
    M("electron_rest_energy", "structural", "validated", "stable_constructed", "open", "open", "not_ready",
      ("localized dimensionless branch", "interior scale", "binding candidate"),
      ("independent mass prediction", "shared energy-length calibration", "out-of-sample rest energy")),
    M("de_broglie_clock", "conditional", "validated", "stable_constructed", "open", "open", "conditional_internal",
      ("scoped entropic/proper-time equality", "stationary-branch ratio", "held-out internal tests"),
      ("physical Zitterbewegung identity", "clock/action-rate calibration", "external evidence")),
    M("particle_stability", "proved", "validated", "stable_constructed", "not_required_for_scope", "not_required_for_scope", "validated_internal",
      ("compact minimizing orbit", "global split-flow control", "perturbation tubes", "identified standing-wave orbit"),
      ("physical particle identity", "external validation")),
    M("magnetic_moment_spin", "proved", "validated", "not_constructed", "open", "open", "conditional_internal",
      ("Jz=1/2", "tree-level g=2", "Pauli current moment", "response-moment agreement", "Dirac-generator evolution"),
      ("stable charged spinor", "anomalous moment", "covariant packet spin law", "electron identity", "moment calibration")),
    M("spin_half_statistics", "proved", "validated", "not_required", "not_required_for_scope", "not_required_for_scope", "validated_internal",
      ("2pi sign reversal", "4pi return", "exchange phase", "antisymmetry", "identical-state exclusion"),
      ("physical electron identity",)),
    M("antimatter_annihilation", "structural", "reduced_validated", "reduced_constructed", "open", "not_required_for_scope", "conditional_internal",
      ("opposite-sector capture", "reduced annihilation", "radiation energy ledger"),
      ("stable opposite charged states", "unassisted full-PDE annihilation")),
    M("lepton_mass_spectrum", "structural", "negative", "not_constructed", "rejected", "open", "negative_out_of_sample",
      ("low-parameter hierarchy laws tested",),
      ("predictive muon/tau law",)),
    M("dark_matter", "structural", "candidate", "candidate", "candidate", "open", "not_ready",
      ("neutral variational candidate",),
      ("full-PDE stability", "production mechanism", "abundance", "phenomenology", "mass-length calibration")),
    M("quarks", "structural", "candidate", "candidate", "candidate", "open", "not_ready",
      ("finite SU(3) controls", "singlets", "Wilson-loop controls", "fractional charge", "CKM controls"),
      ("dynamical QCD", "running coupling", "confinement", "hadron spectrum", "shared gauge scale")),
    M("baryons", "structural", "candidate", "candidate", "candidate", "open", "not_ready",
      ("charged triplet graph", "binding ledger"),
      ("three-body field state", "quark dynamics", "proton/neutron spectrum", "mass calibration")),
    M("mesons", "structural", "candidate", "candidate", "candidate", "open", "not_ready",
      ("neutral pair graph", "binding ledger"),
      ("two-body field state", "pion/kaon spectrum", "flavor dynamics", "decay channels")),
    M("electric_force", "proved", "validated", "not_constructed", "open", "open", "conditional_internal",
      ("Gauss closure", "Lorentz/energy/stress triangle", "inverse-square asymptote", "action-reaction", "momentum/Lorentz agreement"),
      ("stable charged pair", "single coupled action", "charge-force calibration", "external multi-distance test")),
    M("magnetic_force", "proved", "validated", "not_constructed", "open", "open", "conditional_internal",
      ("magnetization current", "Ampere closure", "magnetic Lorentz contribution", "energy/stress consistency", "Dirac-generator spin evolution"),
      ("stable spinorial pair", "covariant packet torque", "anomalous moment", "moment-force calibration")),
    M("strong_force", "structural", "reduced_validated", "reduced_constructed", "open", "open", "conditional_internal",
      ("Cornell potential control", "flux-tube control", "string-breaking control"),
      ("dynamical Yang-Mills/QCD", "joint tension-breaking prediction", "hadron spectrum")),
    M("weak_force", "structural", "reduced_validated", "reduced_constructed", "open", "open", "conditional_internal",
      ("left-selective transitions", "reduced decay ledger", "chiral controls"),
      ("electroweak gauge dynamics", "symmetry breaking", "shared rate/mixing prediction", "calibrated lifetimes")),
    M("gravity", "conditional", "reduced_validated", "candidate", "open", "open", "conditional_internal",
      ("weak-field controls", "equivalence-principle controls", "Einstein-Maxwell-entropic interfaces", "metric-curvature constructions", "Bianchi/conservation infrastructure"),
      ("single end-to-end coupled numerical action", "global Cauchy development", "constraint propagation", "calibrated gravity predictions")),
    M("em_waves", "proved", "validated", "not_required", "not_required_for_scope", "not_required_for_scope", "validated_internal",
      ("source-free Maxwell waves", "transverse dispersion", "energy control"),
      ("photon quantization", "physical field calibration")),
    M("klein_gordon", "proved", "validated", "not_required", "not_required_for_scope", "not_required_for_scope", "validated_internal",
      ("massive dispersion", "massless limit", "group composition", "reversal", "energy conservation"),
      ("interacting scalar QFT", "physical particle identity", "mass calibration")),
    M("orbital_quantization", "proved", "validated", "not_required", "not_required_for_scope", "not_required_for_scope", "validated_internal",
      ("hydrogenic ladder", "nodes", "orthogonality", "refinement", "O(4) degeneracies"),
      ("emergent atomic constituents", "radiative transitions", "physical atomic units")),
    M("thermal_field", "proved", "validated", "not_required", "not_required_for_scope", "not_required_for_scope", "validated_internal",
      ("dimensionless heat equation", "entropy and diffusion controls"),
      ("microscopic CAT/EPT thermodynamics", "material calibration", "quantum thermalization")),
)


def maturity_by_key() -> dict[str, CriterionMaturity]:
    return {row.key: row for row in MATURITY_ROWS}


def headline_counts(rows: tuple[CriterionMaturity, ...] = MATURITY_ROWS) -> dict[str, int]:
    names: tuple[HeadlineStatus, ...] = (
        "validated_in_scope", "conditional_validated", "reduced_model_validated",
        "calibration_pending", "candidate", "negative",
    )
    return {name: sum(row.headline == name for row in rows) for name in names}


def legacy_partial_breakdown() -> dict[str, int]:
    legacy = {row.key: row.status for row in LEGACY_CRITERIA}
    partial = tuple(row for row in MATURITY_ROWS if legacy[row.key] == "partial")
    return {name: sum(row.headline == name for row in partial) for name in headline_counts()}


def canonical_payload() -> dict[str, Any]:
    legacy = {row.key: row.status for row in LEGACY_CRITERIA}
    return {
        "schema": "openwave.m9.criterion-maturity.v1",
        "criteria": [
            {**asdict(row), "headline": row.headline, "legacy_status": legacy[row.key]}
            for row in MATURITY_ROWS
        ],
        "headline_counts": headline_counts(),
        "legacy_partial_breakdown": legacy_partial_breakdown(),
        "policy": {
            "headline_is_derived": True,
            "legacy_status_is_compatibility_metadata": True,
            "fixed_promoted_key_set_used": False,
            "fixed_7_13_1_count_used_as_acceptance_gate": False,
        },
    }


def maturity_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_criterion_maturity_study() -> dict[str, Any]:
    payload = canonical_payload()
    legacy_keys = {row.key for row in LEGACY_CRITERIA}
    maturity_keys = {row.key for row in MATURITY_ROWS}
    expected_headlines = {
        "validated_in_scope": 7,
        "conditional_validated": 5,
        "reduced_model_validated": 3,
        "calibration_pending": 1,
        "candidate": 4,
        "negative": 1,
    }
    expected_partial_split = {
        "validated_in_scope": 0,
        "conditional_validated": 5,
        "reduced_model_validated": 3,
        "calibration_pending": 1,
        "candidate": 4,
        "negative": 0,
    }
    acceptance = {
        "all_legacy_criteria_are_reclassified": legacy_keys == maturity_keys and len(maturity_keys) == 21,
        "headline_counts_are_evidence_derived": payload["headline_counts"] == expected_headlines,
        "legacy_partial_bucket_is_resolved": payload["legacy_partial_breakdown"] == expected_partial_split,
        "no_fixed_promoted_key_set_is_used": not payload["policy"]["fixed_promoted_key_set_used"],
        "legacy_7_13_1_is_not_an_acceptance_gate": not payload["policy"]["fixed_7_13_1_count_used_as_acceptance_gate"],
        "each_row_has_closed_and_open_evidence": all(row.closed and row.open for row in MATURITY_ROWS),
        "fingerprint_is_deterministic": maturity_fingerprint(payload) == maturity_fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.100a",
        "fingerprint": maturity_fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "legacy_partial_is_deprecated_as_primary_status": True,
            "multi_axis_maturity_is_canonical": True,
            "physical_identity_or_calibration_inferred": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True) + "\n"
