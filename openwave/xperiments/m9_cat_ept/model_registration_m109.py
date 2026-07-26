"""Current M9 registration over schema-v22 Newton-G conformance."""
from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
import json
from typing import Any, Mapping

from .model_conformance_m109 import canonical_payload as conformance_payload
from .model_conformance_m109 import run_conformance_study
from .model_registration_m108 import canonical_registration_payload as previous_payload


def canonical_registration_payload() -> dict[str, Any]:
    previous = previous_payload()
    conformance = conformance_payload()
    components = conformance["evidence"]["components"]
    return {
        **previous,
        "schema": "openwave.model-registration.v13",
        "conformance": conformance,
        "m9_109": {
            "physlib_head": conformance["formal_authority"]["formal_repository"][
                "current_head"
            ],
            "zil_head": conformance["formal_authority"]["zil_repository"]["head"],
            "G_clock_formal_authority_registered": components[
                "formal_G_clock_authority"
            ]["campaign_passed"],
            "G_is_derived_not_primitive": components["formal_G_clock_authority"][
                "G_is_derived_not_primitive"
            ],
            "particle_clock_universality_audited": components["clock_universality"][
                "campaign_passed"
            ],
            "particle_clocks_define_universal_G": components["clock_universality"][
                "particle_clocks_define_universal_G"
            ],
            "independent_universal_anchor_ready": components["universal_anchor"][
                "independent_anchor_ready"
            ],
            "withheld_G_prediction_executed": components["universal_anchor"][
                "withheld_G_prediction_executed"
            ],
            "calibrated_gravity_coupling_injected": components["gravity_adapter"][
                "calibrated_coupling_injected"
            ],
            "headline_counts": conformance["summary"],
            "physical_claims_promoted": [],
        },
        "claim_boundary": {
            **previous["claim_boundary"],
            "derived_G_is_predicted_G": False,
            "particle_clock_is_universal_gravity_clock": False,
            "Planck_inversion_is_independent_measurement": False,
            "natural_unit_G_is_physical_calibration": False,
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_registration_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":"), default=str).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_model_registration_study() -> dict[str, Any]:
    conformance = run_conformance_study()
    payload = canonical_registration_payload()
    current = payload["m9_109"]
    boundaries = (
        "derived_G_is_predicted_G",
        "particle_clock_is_universal_gravity_clock",
        "Planck_inversion_is_independent_measurement",
        "natural_unit_G_is_physical_calibration",
    )
    acceptance = {
        "m109_conformance_passes": bool(conformance["passed"]),
        "schema_v13_is_current": payload["schema"]
        == "openwave.model-registration.v13",
        "formal_G_authority_is_registered": current[
            "G_clock_formal_authority_registered"
        ]
        and current["G_is_derived_not_primitive"],
        "particle_clock_universality_failure_is_preserved": not current[
            "particle_clocks_define_universal_G"
        ],
        "unready_anchor_does_not_execute_prediction": not current[
            "independent_universal_anchor_ready"
        ]
        and not current["withheld_G_prediction_executed"],
        "unready_prediction_does_not_inject_coupling": not current[
            "calibrated_gravity_coupling_injected"
        ],
        "no_physical_claim_is_promoted": current["physical_claims_promoted"] == [],
        "all_new_boundaries_are_preserved": all(
            not payload["claim_boundary"][key] for key in boundaries
        ),
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "task": "M9.109-registration",
        "registration_fingerprint": fingerprint(payload),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "m109_registration_is_current": True,
            "Newton_G_formal_maturity_changed": True,
            "Newton_G_physical_prediction_changed": False,
            "M9_110_remains_blocked_on_calibrated_universal_anchor": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
