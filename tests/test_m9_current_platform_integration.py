from pathlib import Path

from openwave.xperiments.m9_cat_ept.model_conformance_current import CURRENT_CONFORMANCE_SCHEMA, CURRENT_MILESTONE, canonical_payload as current_conformance_payload, run_conformance_study
from openwave.xperiments.m9_cat_ept.model_registration_current import CURRENT_CONFORMANCE_RUNNER, CURRENT_SCHEMA as CURRENT_REGISTRATION_SCHEMA, canonical_registration_payload, run_model_registration_study
from openwave.xperiments.m9_cat_ept.platform_integration_contract import run_platform_integration_contract


def test_stable_current_aliases_reach_m9_123() -> None:
    registration, conformance = canonical_registration_payload(), current_conformance_payload()
    current = registration["m9_123"]
    assert CURRENT_MILESTONE == "M9.123"
    assert CURRENT_REGISTRATION_SCHEMA == "openwave.model-registration.v26"
    assert registration["schema"] == CURRENT_REGISTRATION_SCHEMA
    assert registration["registration"]["conformance_runner"] == CURRENT_CONFORMANCE_RUNNER
    assert current["nonparticle_domain_count"] == 8 and current["nonparticle_control_count"] == 6
    assert current["broad_internal_physics_modeling"] and not current["particle_spectroscopy_primary"]
    assert current["physical_claims_promoted"] == []
    assert conformance["schema"] == CURRENT_CONFORMANCE_SCHEMA
    assert conformance["current_milestone"] == "M9.123"
    assert len(conformance["maturity"]["criteria"]) == 21
    assert conformance["latest_evidence"]["passed"]
    assert conformance["latest_registration"]["schema"] == CURRENT_REGISTRATION_SCHEMA


def test_current_authority_passes_without_unification_or_external_promotion() -> None:
    registration, conformance = run_model_registration_study(), run_conformance_study()
    current = registration["m9_123"]
    assert registration["passed"] and conformance["passed"]
    assert current["broad_internal_physics_modeling"]
    assert not current["predictive_fundamental_theory_ready"]
    assert not current["independent_calibration_complete"]
    assert not current["external_validation_complete"]
    assert not current["external_physical_promotion_allowed"]
    assert current["physical_claims_promoted"] == []


def test_platform_integration_contract_passes() -> None:
    result = run_platform_integration_contract()
    assert result["schema"] == "openwave.m9.platform-integration-contract.v6"
    assert result["passed"] and all(result["acceptance"].values())
    assert result["current_conformance_runner"] == CURRENT_CONFORMANCE_RUNNER
    assert result["merged_formal_head"] == "80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef"
    assert result["merged_formal_branch"] == "master"
    assert result["zil_public_head"] == "c671f02d8b6dcf7ba689afc86477ff7e35465c35"
    assert result["decision"]["particle_spectroscopy_is_primary_scorecard"] is False
    assert result["decision"]["predictive_fundamental_theory_ready"] is False
    assert result["decision"]["physical_claims_promoted"] == []


def test_public_profiles_and_stable_runners_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    required = (root / "MODELS.md", root / "MODELS_LEGACY.md", root / "MODELS_M9.md", root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_current_registration.py", root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_current_conformance.py", root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_current_platform_contract.py", root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_123a_physics_scope.py", root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_123b_nonparticle_benchmark.py", root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_123c_explanatory_scope.py", root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_123_current_registration.py")
    assert all(path.is_file() for path in required)
    registry = (root / "MODELS.md").read_text(encoding="utf-8")
    profile = (root / "MODELS_M9.md").read_text(encoding="utf-8")
    roadmap = (root / "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md").read_text(encoding="utf-8")
    assert "M9.123" in registry and "non-particle physics" in registry
    assert "M9.123" in profile and "openwave.model-registration.v26" in profile
    assert "particle spectroscopy is not the primary scorecard" in profile
    assert "predictive fundamental theory" in profile
    assert all(token in roadmap for token in ("M9.123a", "M9.123b", "M9.123c", "M9.124"))
