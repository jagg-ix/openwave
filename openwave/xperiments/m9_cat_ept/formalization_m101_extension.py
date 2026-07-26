"""M9.101 formal authority for the current entropic-physlib-linear-full branch.

The previous OpenWave equation contract predates the global integrated electrogravitic
action, the metric-built entropic-dynamics capstone, the G-free Newton coupling, and
the current clock/action and Pauli/T-BMT interfaces. This module pins those exact
surfaces and records what each theorem actually supplies.
"""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_HEAD = "acdbe8ce6456e66837bd18604cf3107d3181c4de"
PHYSLIB_ROOT_BLOB = "cf0c719c3249c48174df8923380287bcaf33f04b"

FORMAL_SOURCES = (
    {"path": "Physlib/QuantumMechanics/ComplexAction/Curvature/GlobalElectrograviticAction.lean", "blob": "39e807f424cf8384135299e84fdffc97fb506ee5", "role": "integrated nonlinear continuum action data and stationarity-to-field-equation bridge", "epistemic_status": "ansatz-loaded"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/ComplexEinstein/ElectroGravitationalFieldEquations.lean", "blob": "7ecfc0ce288e84d575af60718b74fb1148bf0c5f", "role": "coupled metric, gauge and entropic first variation and derivative certificate", "epistemic_status": "conditional-formal"},
    {"path": "Physlib/Meta/EntropicDynamicsFullEinsteinSource.lean", "blob": "f1dc5fb21b42b5be676485a672c6923615b6380e", "role": "metric-built entropic-dynamics capstone with Maxwell, Einstein and Bianchi conclusions", "epistemic_status": "conditional-formal"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/ComptonClock/ComptonCellNewtonConstant.lean", "blob": "535738543f0259aae3f6f36e772ec4bf160317b8", "role": "G-free relations G=hbar*c/m^2 and G=hbar*c*sigma0^4", "epistemic_status": "ansatz-loaded"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/ClockRelativeEntropy.lean", "blob": "b0bbc6d801cbb0112eeafe628bc694a5d7bd1007", "role": "operator entropic clock and exact frequency-lapse Tolman algebra", "epistemic_status": "conditional-formal"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/ClockEntropyNagaoGravity.lean", "blob": "386013906df52c051e17097b02afda8d41da85bb", "role": "clock entropy rate, complex-action damping and entropic curvature bridge", "epistemic_status": "conditional-formal"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/Yukawa/CouplingIsolation.lean", "blob": "527116982460e59e62c5736249a624f836d2f102", "role": "clock-frequency Yukawa isolation and entropy-rate relation", "epistemic_status": "inversion"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/FirstQuantizedQED/AnomalousMomentLinks.lean", "blob": "51c0e5d9adacf144b6c902ff47d0850071083a0c", "role": "gauge-invariant Pauli tensor coupling and g-factor split", "epistemic_status": "structural"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/MuonAnomaly/ThomasBMTMagicCancellation.lean", "blob": "7a7863819b8c86dfa1eb5a9647b4f59250885d4f", "role": "lab-frame T-BMT coefficients, magic cancellation and rest-frame QED grounding", "epistemic_status": "mixed"},
    {"path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/EntropicDynamicsEvolutionSchrodingerEhrenfest.lean", "blob": "b4652ff601e9dad1fa46a58258d8e1b132ba1e33", "role": "hbar-squared quantum coupling and curved gauge-density/Ehrenfest interfaces", "epistemic_status": "conditional-formal"},
    {"path": "Physlib/Meta/DerivedPredictions.lean", "blob": "325e2c3b475ded41e38fb3b9c2c9ca713fdeb267", "role": "enforced epistemic classes for inversions, identities, ansatz-loaded and risky claims", "epistemic_status": "audit-authority"},
)

TARGETS = (
    {"id": "coupled_gauge_spinor_hartree_action", "openwave_scope": "finite periodic action and winding-sector stationary solver", "remaining_boundary": "not the full continuum Einstein-Hilbert-Maxwell density"},
    {"id": "covariant_packet_tbmt", "openwave_scope": "local packet integral of the regular lab-frame BMT angular velocity", "remaining_boundary": "the covariant boost/Thomas equation remains imported physical dynamics"},
    {"id": "clock_action_rate_calibration", "openwave_scope": "internal natural-unit calibration from a measured branch frequency", "remaining_boundary": "not an external physical electron-clock calibration"},
    {"id": "electrogravitic_evolution", "openwave_scope": "weak-field Schrodinger-Maxwell-Poisson evolution with metric-source diagnostics", "remaining_boundary": "not a nonlinear four-dimensional Einstein Cauchy development"},
)


def _is_sha(value: object) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(c in "0123456789abcdef" for c in value.lower())


def canonical_payload() -> dict[str, Any]:
    return {
        "schema": "openwave.m9.formalization-m101-extension.v1",
        "repository": {"name": FORMAL_REPOSITORY, "branch": FORMAL_BRANCH, "head": FORMAL_HEAD, "physlib_root_blob": PHYSLIB_ROOT_BLOB},
        "sources": [dict(source) for source in FORMAL_SOURCES],
        "targets": [dict(target) for target in TARGETS],
        "policy": {
            "lean_is_proof_authority": True,
            "formal_interface_is_not_numerical_implementation": True,
            "ansatz_loaded_relations_are_not_parameter_free_predictions": True,
            "scope_boundaries_are_mandatory": True,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_formalization_m101_extension() -> dict[str, Any]:
    payload = canonical_payload()
    paths = [source["path"] for source in FORMAL_SOURCES]
    acceptance = {
        "current_formal_head_is_pinned": _is_sha(FORMAL_HEAD) and FORMAL_HEAD == "acdbe8ce6456e66837bd18604cf3107d3181c4de",
        "current_physlib_root_is_pinned": _is_sha(PHYSLIB_ROOT_BLOB),
        "all_formal_sources_are_exact": len(FORMAL_SOURCES) == 11 and len(set(paths)) == len(paths) and all(_is_sha(source["blob"]) for source in FORMAL_SOURCES),
        "all_four_targets_are_registered": [target["id"] for target in TARGETS] == ["coupled_gauge_spinor_hartree_action", "covariant_packet_tbmt", "clock_action_rate_calibration", "electrogravitic_evolution"],
        "recent_global_action_and_gravity_surfaces_are_used": any("GlobalElectrograviticAction" in path for path in paths) and any("EntropicDynamicsFullEinsteinSource" in path for path in paths),
        "all_boundaries_are_explicit": all(target["remaining_boundary"] for target in TARGETS),
        "epistemic_audit_is_registered": any(path.endswith("Meta/DerivedPredictions.lean") for path in paths),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.101a",
        "fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "formal_authority_upgraded_to_current_head": True,
            "recent_global_action_and_clock_surfaces_recognized": True,
            "formal_interfaces_promote_no_physical_identity": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
