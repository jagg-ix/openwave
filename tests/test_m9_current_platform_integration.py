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
from openwave.xperiments.m9_cat_ept.platform_integration_contract import (
    run_platform_integration_contract,
)


def test_stable_current_aliases_reach_m9_122() -> None:
    registration = canonical_registration_payload()
    conformance = current_conformance_payload()
    current = registration["m9_122"]

    assert CURRENT_MILESTONE == "M9.122"
    assert CURRENT_REGISTRATION_SCHEMA == "openwave.model-registration.v25"
    assert registration["schema"] == CURRENT_REGISTRATION_SCHEMA
    assert registration["registration"]["conformance_runner"] == CURRENT_CONFORMANCE_RUNNER
    assert current["external_evidence_package_schema"]
    assert current["blinded_external_evaluator"]
    assert current["independent_identity_bridge_contract"]
    assert current["physical_claims_promoted"] == []

    assert conformance["schema"] == CURRENT_CONFORMANCE_SCHEMA
    assert conformance["current_milestone"] == "M9.122"
    assert len(conformance["maturity"]["criteria"]) == 21
    assert conformance["latest_evidence"]["passed"]
    assert conformance["latest_registration"]["schema"] == CURRENT_REGISTRATION_SCHEMA


def test_current_authority_studies_pass_without_external_promotion() -> None:
    registration = run_model_registration_study()
    conformance = run_conformance_study()
    current = registration["m9_122"]

    assert registration["passed"]
    assert conformance["passed"]
    assert not current["real_external_evidence_ingested"]
    assert not current["live_heldout_evaluation_executed"]
    assert not current["physical_transition_identity_established"]
    assert not current["external_validation_complete"]
    assert not current["external_physical_promotion_allowed"]
    assert current["physical_claims_promoted"] == []


def test_platform_integration_contract_passes() -> None:
    result = run_platform_integration_contract()

    assert result["schema"] == "openwave.m9.platform-integration-contract.v5"
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["current_conformance_runner"] == CURRENT_CONFORMANCE_RUNNER
    assert result["merged_formal_head"] == "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef"
    assert result["merged_formal_branch"] == "master"
    assert result["zil_public_head"] == "c671f02d8b6dcf7ba689afc86477ff7e35465c35"
    assert result["decision"]["M9_is_exposed_as_first_class_OpenWave_model"]
    assert result["decision"]["physical_claims_promoted"] == []


def test_public_profiles_and_stable_runners_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    required = (
        root / "MODELS.md",
        root / "MODELS_LEGACY.md",
        root / "MODELS_M9.md",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_current_registration.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_current_conformance.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_current_platform_contract.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_122a_external_evidence_package.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_122b_blinded_evaluator.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_122c_identity_bridge.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_122_current_registration.py",
    )
    assert all(path.is_file() for path in required)

    registry = (root / "MODELS.md").read_text(encoding="utf-8")
    profile = (root / "MODELS_M9.md").read_text(encoding="utf-8")
    roadmap = (
        root / "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md"
    ).read_text(encoding="utf-8")
    assert "M9.122" in registry
    assert "external-evidence package" in registry
    assert "M9.122" in profile
    assert "openwave.model-registration.v25" in profile
    assert "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef" in profile
    assert "synthetic fixture" in profile
    assert "M9.122a" in roadmap
    assert "M9.122b" in roadmap
    assert "M9.122c" in roadmap
    assert "M9.123" in roadmap
