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


def test_stable_current_aliases_reach_m9_124() -> None:
    registration = canonical_registration_payload()
    conformance = current_conformance_payload()
    current = registration["m9_124"]
    assert CURRENT_MILESTONE == "M9.124"
    assert CURRENT_REGISTRATION_SCHEMA == "openwave.model-registration.v27"
    assert registration["schema"] == CURRENT_REGISTRATION_SCHEMA
    assert registration["registration"]["conformance_runner"] == CURRENT_CONFORMANCE_RUNNER
    assert current["clock_role_count"] == 3
    assert current["pairwise_bridge_count"] == 3
    assert current["three_aspect_time_framework"]
    assert not current["single_unified_physical_clock_established"]
    assert current["physical_claims_promoted"] == []
    assert conformance["schema"] == CURRENT_CONFORMANCE_SCHEMA
    assert conformance["current_milestone"] == "M9.124"
    assert len(conformance["maturity"]["criteria"]) == 21
    assert conformance["latest_evidence"]["passed"]


def test_current_authority_studies_pass_without_clock_identity_promotion() -> None:
    registration = run_model_registration_study()
    conformance = run_conformance_study()
    assert registration["passed"]
    assert conformance["passed"]
    current = registration["m9_124"]
    assert current["three_aspect_time_framework"]
    assert not current["single_unified_physical_clock_established"]
    assert not current["external_validation_complete"]
    assert not current["external_physical_promotion_allowed"]


def test_platform_integration_contract_passes() -> None:
    result = run_platform_integration_contract()
    assert result["schema"] == "openwave.m9.platform-integration-contract.v7"
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["merged_formal_head"] == "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef"
    assert result["development_formal_head"] == "af78ea63ee0b39456d8dab023761482196b8c172"
    assert result["development_formal_branch"] == "entropic-physlib-linear-full"
    assert result["decision"]["physical_claims_promoted"] == []


def test_public_profiles_and_runners_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    required = (
        root / "MODELS.md", root / "MODELS_M9.md",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_124a_three_clock_profile.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_124b_three_clock_benchmark.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_124c_three_clock_synthesis.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_124_current_registration.py",
    )
    assert all(path.is_file() for path in required)
    registry = (root / "MODELS.md").read_text(encoding="utf-8")
    profile = (root / "MODELS_M9.md").read_text(encoding="utf-8")
    roadmap = (root / "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md").read_text(encoding="utf-8")
    assert "M9.124" in registry and "Page-Wootters" in registry
    assert "openwave.model-registration.v27" in profile
    assert "single unified physical clock" in profile
    assert all(token in roadmap for token in ("M9.124a", "M9.124b", "M9.124c", "M9.125"))
