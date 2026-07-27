from pathlib import Path

from openwave.xperiments.m9_cat_ept.model_conformance_current import (
    CURRENT_CONFORMANCE_SCHEMA,
    CURRENT_MILESTONE,
    canonical_payload as current_conformance_payload,
    run_conformance_study,
)
from openwave.xperiments.m9_cat_ept.model_registration_current import (
    CURRENT_CONFORMANCE_RUNNER,
    CURRENT_SCHEMA as CURRENT_REGISTRATION_SCHEMA,
    canonical_registration_payload,
    run_model_registration_study,
)
from openwave.xperiments.m9_cat_ept.platform_integration_contract import run_platform_integration_contract


def test_stable_current_aliases_reach_m9_125() -> None:
    registration = canonical_registration_payload()
    conformance = current_conformance_payload()
    current = registration["m9_125"]
    assert CURRENT_MILESTONE == "M9.125"
    assert CURRENT_REGISTRATION_SCHEMA == "openwave.model-registration.v28"
    assert registration["schema"] == CURRENT_REGISTRATION_SCHEMA
    assert registration["registration"]["conformance_runner"] == CURRENT_CONFORMANCE_RUNNER
    assert current["shared_finite_three_clock_carrier"]
    assert current["conditioned_modular_identification_reduced"]
    assert current["internal_clock_parameter_maps"]
    assert not current["single_universal_physical_clock_established"]
    assert current["physical_claims_promoted"] == []
    assert conformance["schema"] == CURRENT_CONFORMANCE_SCHEMA
    assert conformance["current_milestone"] == "M9.125"
    assert len(conformance["maturity"]["criteria"]) == 21
    assert conformance["latest_evidence"]["passed"]


def test_current_authority_studies_pass_without_physical_clock_promotion() -> None:
    registration = run_model_registration_study()
    conformance = run_conformance_study()
    current = registration["m9_125"]
    assert registration["passed"]
    assert conformance["passed"]
    assert current["reduced_common_carrier_gate"]
    assert not current["real_three_clock_data_ingested"]
    assert not current["external_validation_complete"]
    assert not current["external_physical_promotion_allowed"]


def test_platform_integration_contract_passes() -> None:
    result = run_platform_integration_contract()
    assert result["schema"] == "openwave.m9.platform-integration-contract.v8"
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["current_conformance_runner"] == CURRENT_CONFORMANCE_RUNNER
    assert result["merged_formal_head"] == "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef"
    assert result["development_formal_head"] == "af78ea63ee0b39456d8dab023761482196b8c172"
    assert result["decision"]["physical_claims_promoted"] == []


def test_public_profiles_and_current_runners_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    required = (
        root / "MODELS.md",
        root / "MODELS_M9.md",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_125a_shared_carrier.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_125b_calibration_contract.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_125c_holdout_protocol.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_125_current_registration.py",
    )
    assert all(path.is_file() for path in required)
    registry = (root / "MODELS.md").read_text(encoding="utf-8")
    profile = (root / "MODELS_M9.md").read_text(encoding="utf-8")
    roadmap = (root / "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md").read_text(encoding="utf-8")
    assert "M9.125" in registry and "shared finite carrier" in registry
    assert "openwave.model-registration.v28" in profile
    assert "real three-clock data" in profile
    assert all(token in roadmap for token in ("M9.125a", "M9.125b", "M9.125c", "M9.126", "NEXT"))
