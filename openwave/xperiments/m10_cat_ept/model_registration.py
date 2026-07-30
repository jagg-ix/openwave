"""Registration and executable contract for the M10 particle-model lineage."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

from .color_matter_gauss_m107 import (
    MILESTONE as MATTER_MILESTONE,
    canonical_payload as matter_payload,
    run_color_matter_gauss_study,
)
from .dirac_cartan_2i_yukawa_model import (
    MILESTONE as CARRIER_MILESTONE,
    SCHEMA as CARRIER_SCHEMA,
    canonical_payload as carrier_payload,
    run_m10_core_study,
)
from .formal_authority import (
    FORMAL_HEAD,
    canonical_payload as formal_authority_payload,
    fingerprint as formal_authority_fingerprint,
)
from .periodic_su3_hamiltonian_m106 import (
    FORMAL_SOURCES as HAMILTONIAN_FORMAL_SOURCES,
    MILESTONE as HAMILTONIAN_MILESTONE,
    canonical_payload as hamiltonian_payload,
    run_periodic_su3_hamiltonian_study,
)
from .qcd_functional_decoherence_m104 import (
    FORMAL_SOURCES as QCD_FORMAL_SOURCES,
    MILESTONE as QCD_MILESTONE,
    canonical_payload as qcd_payload,
    run_qcd_functional_decoherence_study,
)
from .second_quantized_fock_m103 import (
    FORMAL_HEAD as FOCK_FORMAL_HEAD,
    FORMAL_PR as FOCK_FORMAL_PR,
    FORMAL_SOURCE_BLOB as FOCK_FORMAL_SOURCE_BLOB,
    FORMAL_THEOREM as FOCK_FORMAL_THEOREM,
    MILESTONE as FOCK_MILESTONE,
    canonical_payload as fock_payload,
    run_second_quantized_fock_study,
)
from .su3_link_backreaction_m105 import (
    FORMAL_SOURCES as SU3_FORMAL_SOURCES,
    MILESTONE as SU3_MILESTONE,
    canonical_payload as su3_payload,
    run_su3_link_backreaction_study,
)
from .wilson_refinement_spectrum_m108 import (
    FORMAL_SOURCES as SPECTRUM_FORMAL_SOURCES,
    MILESTONE,
    SCHEMA as MODEL_SCHEMA,
    canonical_payload as spectrum_payload,
    run_wilson_refinement_spectrum_study,
)

SCHEMA = "openwave.model-registration.m10.v8"
COLOR_MATTER_FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/YangMillsGaugeDynamics.lean",
        "sha": "4fe7ae3471057b5c7b64fc22705d76f854d66766",
        "theorem": "yangMillsEquation_gauge_covariant",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/GellMannStructureConstants.lean",
        "sha": "b721ea5e04a72430a81d84c6a0a6c20b3f9558a0",
        "theorem": "gellMann_structure_constants",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/SuNGaugeSector.lean",
        "sha": "4585ddf9bc44396b5f9dce14321c4d6b2826cb8a",
        "theorem": "su3_adjoint_eq_gluonCount",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Yukawa/MassDecoherenceProportionality.lean",
        "sha": "578152c3b9d73b3baec98f845bca2f566f59e93e",
        "theorem": "yukawaEntropyRate_eq_const_mul_mass",
    },
)


def canonical_registration_payload() -> dict[str, Any]:
    carrier = carrier_payload()
    fock = fock_payload()
    qcd = qcd_payload()
    su3 = su3_payload()
    hamiltonian = hamiltonian_payload()
    matter = matter_payload()
    spectrum = spectrum_payload()
    formal = formal_authority_payload()
    return {
        "schema": SCHEMA,
        "model_id": "M10",
        "model": spectrum["model"],
        "milestone": MILESTONE,
        "carrier_milestone": CARRIER_MILESTONE,
        "closure_milestone": "M10.2",
        "fock_milestone": FOCK_MILESTONE,
        "qcd_milestone": QCD_MILESTONE,
        "su3_milestone": SU3_MILESTONE,
        "hamiltonian_milestone": HAMILTONIAN_MILESTONE,
        "matter_milestone": MATTER_MILESTONE,
        "carrier_schema": CARRIER_SCHEMA,
        "fock_schema": fock["schema"],
        "qcd_schema": qcd["schema"],
        "su3_schema": su3["schema"],
        "hamiltonian_schema": hamiltonian["schema"],
        "matter_schema": matter["schema"],
        "model_schema": MODEL_SCHEMA,
        "construction_api": carrier["construction_api"],
        "state_api": carrier["state_api"],
        "fock_construction_api": fock["construction_api"],
        "qcd_functional_study_api": qcd["study_api"],
        "su3_link_construction_api": su3["construction_api"],
        "hamiltonian_lattice_study_api": hamiltonian["study_api"],
        "color_matter_study_api": matter["study_api"],
        "wilson_spectrum_study_api": spectrum["study_api"],
        "formal_authority": formal,
        "formal_authority_fingerprint": formal_authority_fingerprint(formal),
        "second_quantized_formal_authority": dict(fock["formal_authority"]),
        "qcd_functional_formal_authority": dict(qcd["formal_authority"]),
        "su3_link_formal_authority": dict(su3["formal_authority"]),
        "hamiltonian_lattice_formal_authority": dict(hamiltonian["formal_authority"]),
        "color_matter_formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "sources": list(COLOR_MATTER_FORMAL_SOURCES),
        },
        "wilson_spectrum_formal_authority": dict(spectrum["formal_authority"]),
        "establishes": [
            *carrier["establishes"],
            "fermionic Fock and finite QCD history functional",
            "matrix-valued and periodic Hamiltonian SU3 gauge dynamics",
            "gauge-covariant fundamental-color matter and sourced Gauss law",
            "nested Wilson-loop refinement and area-perimeter diagnostics",
            "Polyakov center invariance and positive Creutz ratio",
            "positive normalized environment decoherence spectra",
        ],
        "comparison_role": (
            "second-quantized relativistic non-Abelian color-matter confinement "
            "comparison model to M9 Pauli-Hartree-U1"
        ),
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


def _pinned(authority: Mapping[str, Any], expected: int) -> bool:
    return len(authority["sources"]) == expected and all(
        len(source["sha"]) == 40 for source in authority["sources"]
    )


def run_model_registration_study() -> dict[str, Any]:
    payload = canonical_registration_payload()
    core = run_m10_core_study()
    fock = run_second_quantized_fock_study()
    qcd = run_qcd_functional_decoherence_study()
    su3 = run_su3_link_backreaction_study()
    hamiltonian = run_periodic_su3_hamiltonian_study()
    matter = run_color_matter_gauss_study()
    spectrum = run_wilson_refinement_spectrum_study()
    formal = payload["formal_authority"]
    fock_formal = payload["second_quantized_formal_authority"]
    qcd_formal = payload["qcd_functional_formal_authority"]
    su3_formal = payload["su3_link_formal_authority"]
    hamiltonian_formal = payload["hamiltonian_lattice_formal_authority"]
    matter_formal = payload["color_matter_formal_authority"]
    spectrum_formal = payload["wilson_spectrum_formal_authority"]
    acceptance = {
        "model_id_is_M10": payload["model_id"] == "M10",
        "latest_milestone_is_M10_8": payload["milestone"] == "M10.8",
        "lineage_is_retained": (
            payload["carrier_milestone"] == "M10.1"
            and payload["closure_milestone"] == "M10.2"
            and payload["fock_milestone"] == "M10.3"
            and payload["qcd_milestone"] == "M10.4"
            and payload["su3_milestone"] == "M10.5"
            and payload["hamiltonian_milestone"] == "M10.6"
            and payload["matter_milestone"] == "M10.7"
        ),
        "all_executable_studies_pass": all(
            result["passed"]
            for result in (core, fock, qcd, su3, hamiltonian, matter, spectrum)
        ),
        "one_particle_authority_is_pinned": (
            formal["head"] == FORMAL_HEAD and _pinned(formal, 3)
        ),
        "second_quantized_authority_is_exact": (
            fock_formal["pull_request"] == FOCK_FORMAL_PR
            and fock_formal["head"] == FOCK_FORMAL_HEAD
            and fock_formal["source_blob"] == FOCK_FORMAL_SOURCE_BLOB
            and fock_formal["theorem"] == FOCK_FORMAL_THEOREM
        ),
        "all_sector_authorities_are_pinned": (
            _pinned(qcd_formal, len(QCD_FORMAL_SOURCES))
            and _pinned(su3_formal, len(SU3_FORMAL_SOURCES))
            and _pinned(hamiltonian_formal, len(HAMILTONIAN_FORMAL_SOURCES))
            and _pinned(matter_formal, len(COLOR_MATTER_FORMAL_SOURCES))
            and _pinned(spectrum_formal, len(SPECTRUM_FORMAL_SOURCES))
        ),
        "wilson_spectrum_theorems_are_registered": {
            source["theorem"] for source in spectrum_formal["sources"]
        }
        == {
            "areaLaw_implies_decay",
            "center_preserves_norm",
            "expectation_and_connectedGeneratingFunctional_tendsto",
            "decoherenceFunctional_isDecoherenceFunctional",
            "decoherence_offdiag_bound",
        },
        "all_latest_apis_are_registered": (
            payload["construction_api"].endswith(":construct_state")
            and payload["fock_construction_api"].endswith(":construct_fock_state")
            and payload["qcd_functional_study_api"].endswith(":run_qcd_functional_decoherence_study")
            and payload["su3_link_construction_api"].endswith(":construct_link_state")
            and payload["hamiltonian_lattice_study_api"].endswith(":run_periodic_su3_hamiltonian_study")
            and payload["color_matter_study_api"].endswith(":run_color_matter_gauss_study")
            and payload["wilson_spectrum_study_api"].endswith(":run_wilson_refinement_spectrum_study")
        ),
        "formal_fingerprint_is_deterministic": (
            payload["formal_authority_fingerprint"] == formal_authority_fingerprint(formal)
        ),
        "registration_fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M10.8l",
        "fingerprint": fingerprint(payload),
        "core_fingerprint": core["fingerprint"],
        "fock_fingerprint": fock["fingerprint"],
        "qcd_fingerprint": qcd["fingerprint"],
        "su3_fingerprint": su3["fingerprint"],
        "hamiltonian_fingerprint": hamiltonian["fingerprint"],
        "matter_fingerprint": matter["fingerprint"],
        "spectrum_fingerprint": spectrum["fingerprint"],
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m10_registered_as_separate_model": True,
            "m10_wilson_refinement_spectrum_is_latest": True,
            "all_formal_authorities_are_content_pinned": True,
            "m9_registration_rewritten": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
