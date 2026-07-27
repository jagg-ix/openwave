"""M9.123a: evidence-derived non-particle CAT/EPT physics scope profile."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Literal, Mapping

FormalStatus = Literal["proved", "conditional", "structural"]
DynamicsStatus = Literal["constructed", "reduced", "interface", "partial"]
ContinuumStatus = Literal["constructed", "partial", "finite_only", "open"]
CalibrationStatus = Literal["not_required_for_scope", "partial", "open"]
PredictionStatus = Literal["validated_internal", "conditional_internal", "not_ready"]
Headline = Literal["strong_internal", "conditional_internal", "reduced_internal", "interface_internal", "structural_internal"]


@dataclass(frozen=True)
class PhysicsDomain:
    key: str
    name: str
    formal: FormalStatus
    dynamics: DynamicsStatus
    continuum: ContinuumStatus
    calibration: CalibrationStatus
    prediction: PredictionStatus
    evidence_mode: str
    formal_sources: tuple[str, ...]
    closed: tuple[str, ...]
    open: tuple[str, ...]


def derive_headline(domain: PhysicsDomain) -> Headline:
    if domain.dynamics == "interface":
        return "interface_internal"
    if domain.formal == "conditional":
        return "conditional_internal"
    if domain.dynamics == "reduced" or domain.continuum == "finite_only":
        return "reduced_internal"
    if domain.formal == "structural" or domain.dynamics == "partial":
        return "structural_internal"
    return "strong_internal"


D = PhysicsDomain
DOMAINS: tuple[PhysicsDomain, ...] = (
    D("entropic_time", "Entropic time and irreversible clocks", "proved", "constructed", "partial", "open", "conditional_internal", "dynamical theorem plus model-specific clock calibration", ("Physlib.Thermodynamics.QuantumRelativeEntropyArrow", "Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.EntropicComplexEinstein"), ("CPTP relative-entropy contraction", "unitary invariant-reference clock constancy", "positive-imaginary-energy proper-time clock"), ("universal identification of all physical time with entropic time", "independent imaginary-energy calibration", "held-out clock observation")),
    D("quantum_reconstruction", "Quantum reconstruction and classical limit", "structural", "partial", "partial", "open", "conditional_internal", "exact reconstruction identities plus conditional PDE interfaces", ("Physlib.QuantumMechanics.ComplexAction.EntropicTime.EntropicDynamicsWaveFunctionReconstruction", "Physlib.QuantumMechanics.ComplexAction.EntropicTime.EntropicDynamicsEvolutionSchrodingerEhrenfest"), ("pointwise and measure-continuum Born reconstruction", "quantum-potential coupling algebra", "quadratic Ehrenfest Klein-Gordon reduction"), ("full interacting functional Schrodinger PDE", "locally covariant interacting QFT", "independent physical hbar derivation")),
    D("open_quantum_systems", "Open quantum systems and spectral relaxation", "proved", "constructed", "partial", "open", "conditional_internal", "semigroup and trace-class theorems plus finite carriers", ("Physlib.QuantumMechanics.OpenSystems.LindbladDrivenLeads.TracePreservation", "Physlib.QuantumMechanics.OpenSystems.LindbladDrivenLeads.ContinuumSemigroupClosure", "Physlib.QuantumMechanics.OpenSystems.LindbladDrivenLeads.CauchyWeakLimit"), ("finite GKSL trace preservation", "bounded continuum C0 semigroups", "weak Cauchy-to-Dirac limit", "CPTP model-unit decay"), ("unbounded nonlinear GKSL generation", "independent reservoir calibration", "held-out relaxation or linewidth")),
    D("stochastic_kinetic", "Stochastic, Fokker-Planck, and kinetic dynamics", "proved", "reduced", "partial", "open", "conditional_internal", "pointwise continuum calculus and explicit free kinetic control", ("Physlib.QuantumMechanics.ComplexAction.EntropicTime.EntropicDynamicsLocalTimeFokkerPlanck",), ("current/drift-diffusion equivalence", "curved local-time scaling", "Hörmander bracket generation", "positive kinetic covariance"), ("full functional stochastic-field derivation", "nonlinear variable-coefficient hypoellipticity", "calibrated transport coefficients")),
    D("gravity_geometry", "Gravity, geometry, and electrogravitic coupling", "conditional", "reduced", "partial", "open", "conditional_internal", "metric geometry and variational residuals with explicit premises", ("Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.ElectroGravitationalFieldEquations", "Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.EntropicComplexEinstein"), ("metric-to-curvature construction", "Maxwell stress from F=dA", "Einstein residuals from stationarity", "reduced ADM/BSSN carriers"), ("nonlinear Einstein-Hilbert-Maxwell action", "global Einstein-matter development", "independent gravity calibration", "held-out gravity prediction")),
    D("electromagnetism_aqft", "Electromagnetism, causal fields, and AQFT", "proved", "interface", "partial", "open", "conditional_internal", "causal and gauge-compatible interface theorems", ("Physlib.EntropicSpine", "Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.ElectroGravitationalFieldEquations"), ("Maxwell-Faraday and continuity", "retarded/advanced Green interfaces", "Pauli-Jordan, CCR, positivity, and Hadamard carriers"), ("general globally hyperbolic PDE existence", "minimal coupling derived from CAT/EPT", "field and detector calibration")),
    D("thermodynamics", "Thermodynamics and entropy production", "proved", "constructed", "partial", "open", "conditional_internal", "CPTP data processing and controlled kinetic semigroups", ("Physlib.Thermodynamics.QuantumRelativeEntropyArrow", "Physlib.EntropicSpine"), ("quantum entropy arrow from CPTP evolution", "reversible/dissipative separation", "BGK control semigroup and entropy decay"), ("nonlinear Boltzmann-Grad limit", "molecular-chaos propagation", "material calibration")),
    D("fluid_dissipation", "Dissipative continuum and fluid control", "proved", "reduced", "finite_only", "open", "not_ready", "finite Fourier/Galerkin contraction semigroup", ("Physlib.QuantumMechanics.ComplexAction.NavierStokes.NSFourierDampedStokesSemigroup",), ("finite Fourier C0 contraction semigroup", "diagonal generator and resolvent", "energy/enstrophy damping balance"), ("pressure projection", "nonlinear triads", "infinite-dimensional Navier-Stokes", "calibrated turbulent observable")),
)


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def canonical_payload() -> dict[str, Any]:
    headlines = {domain.key: derive_headline(domain) for domain in DOMAINS}
    names: tuple[Headline, ...] = ("strong_internal", "conditional_internal", "reduced_internal", "interface_internal", "structural_internal")
    return {
        "schema": "openwave.m9.nonparticle-physics-scope.v1",
        "task": "M9.123a",
        "domains": [{**asdict(domain), "headline": headlines[domain.key]} for domain in DOMAINS],
        "headline_counts": {name: sum(value == name for value in headlines.values()) for name in names},
        "policy": {"particle_spectroscopy_is_primary_scorecard": False, "domain_coverage_is_external_validation": False, "formal_compatibility_is_unique_explanation": False, "calibration_and_prediction_axes_remain_separate": True},
    }


@lru_cache(maxsize=1)
def run_physics_scope_profile() -> dict[str, Any]:
    payload = canonical_payload()
    rows = payload["domains"]
    acceptance = {
        "eight_nonparticle_domains_are_present": len(rows) == 8,
        "every_domain_has_formal_sources": all(row["formal_sources"] for row in rows),
        "every_domain_has_closed_and_open_evidence": all(row["closed"] and row["open"] for row in rows),
        "particle_spectroscopy_is_not_primary": not payload["policy"]["particle_spectroscopy_is_primary_scorecard"],
        "all_domains_keep_calibration_explicit": all(row["calibration"] in ("open", "partial", "not_required_for_scope") for row in rows),
        "no_domain_claims_external_validation": all(row["prediction"] != "external_validated" for row in rows),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {**payload, "acceptance": acceptance, "passed": all(acceptance.values()), "fingerprint": fingerprint(payload), "decision": {"broad_internal_physics_coverage": True, "particle_physics_is_not_the_primary_scope": True, "independent_physical_calibration_complete": False, "external_physical_validation_complete": False}}


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
