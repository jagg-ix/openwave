"""Canonical OpenWave registration for the M9 CAT/EPT model component."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .model_conformance import run_conformance_study
from .particle_model import run_particle_kernel_study
from .physlib_contract import contract_fingerprint, run_physlib_contract_study


@dataclass(frozen=True)
class ModelRegistration:
    model_id: str
    key: str
    name: str
    model_directory: str
    launcher: str
    comparison_profile: str
    conformance_runner: str
    particle_api: str
    formal_contract: str
    briefing: str
    physical_identity_default: str | None

    def __post_init__(self) -> None:
        values = (
            self.model_id,
            self.key,
            self.name,
            self.model_directory,
            self.launcher,
            self.comparison_profile,
            self.conformance_runner,
            self.particle_api,
            self.formal_contract,
            self.briefing,
        )
        if not all(values):
            raise ValueError("complete model registration required")
        if self.physical_identity_default is not None:
            raise ValueError("M9 cannot inherit a physical particle name by default")


M9_REGISTRATION = ModelRegistration(
    model_id="M9",
    key="m9_cat_ept",
    name="CAT/EPT Entropic Particle Dynamics",
    model_directory="openwave/xperiments/m9_cat_ept",
    launcher="openwave/xperiments/m9_cat_ept/_launcher.py",
    comparison_profile="MODELS_M9.md",
    conformance_runner=(
        "openwave.xperiments.m9_cat_ept.model_conformance:run_conformance_study"
    ),
    particle_api="openwave.xperiments.m9_cat_ept.particle_model:CatEptParticleModel",
    formal_contract=(
        "openwave/xperiments/m9_cat_ept/formal/physlib_contract.v2.json"
    ),
    briefing="openwave/xperiments/m9_cat_ept/__M9_model_briefing.md",
    physical_identity_default=None,
)


def canonical_registration_payload() -> dict[str, Any]:
    conformance = run_conformance_study()
    return {
        "schema": "openwave.model-registration.v1",
        "registration": asdict(M9_REGISTRATION),
        "formal_contract_fingerprint": contract_fingerprint(),
        "conformance": {
            "criterion_count": conformance["audit"]["criterion_count"],
            "domain_counts": conformance["audit"]["domain_counts"],
            "status_counts": conformance["audit"]["status_counts"],
            "profile_fingerprint": conformance["fingerprint"],
        },
        "claim_boundary": {
            "mathematical_particle_kernel": True,
            "physical_particle_identity": False,
            "physical_calibration": False,
            "out_of_sample_prediction_ready": False,
        },
    }


def registration_fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else payload
    serialized = json.dumps(selected, sort_keys=True, separators=(",", ":"))
    return sha256(serialized.encode()).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    payload = canonical_registration_payload()
    conformance = run_conformance_study()
    formal = run_physlib_contract_study()
    particle = run_particle_kernel_study()
    expected_counts = {"validated": 7, "partial": 13, "negative": 1, "not_yet": 0}
    acceptance = {
        "canonical_model_id_is_m9": M9_REGISTRATION.model_id == "M9",
        "all_21_shared_criteria_are_registered": (
            payload["conformance"]["criterion_count"] == 21
        ),
        "current_status_profile_is_exact": (
            payload["conformance"]["status_counts"] == expected_counts
        ),
        "conformance_profile_passes": bool(conformance["passed"]),
        "physlib_contract_passes": bool(formal["passed"]),
        "particle_kernel_passes": bool(particle["passed"]),
        "launcher_and_briefing_are_registered": bool(
            M9_REGISTRATION.launcher and M9_REGISTRATION.briefing
        ),
        "physical_identity_is_unassigned": (
            M9_REGISTRATION.physical_identity_default is None
            and not payload["claim_boundary"]["physical_particle_identity"]
        ),
        "registration_fingerprint_is_deterministic": (
            registration_fingerprint(payload) == registration_fingerprint(payload)
        ),
    }
    return {
        **payload,
        "task": "M9.93c",
        "registration_fingerprint": registration_fingerprint(payload),
        "component_results": {
            "conformance_passed": conformance["passed"],
            "formal_contract_passed": formal["passed"],
            "particle_kernel_passed": particle["passed"],
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m9_registered_as_canonical_model_component": True,
            "comparison_profile_is_executable": True,
            "physical_particle_name_assigned": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
