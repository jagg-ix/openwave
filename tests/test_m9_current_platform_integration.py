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


def test_stable_current_aliases_reach_m9_119() -> None:
    registration = canonical_registration_payload()
    conformance = current_conformance_payload()

    assert CURRENT_MILESTONE == "M9.119"
    assert CURRENT_REGISTRATION_SCHEMA == "openwave.model-registration.v22"
    assert registration["schema"] == CURRENT_REGISTRATION_SCHEMA
    assert registration["registration"]["conformance_runner"] == CURRENT_CONFORMANCE_RUNNER
    assert registration["m9_119"]["local_SU3_link_carrier"]
    assert registration["m9_119"]["local_SU2xU1_link_carrier"]
    assert registration["m9_119"]["physical_claims_promoted"] == []

    assert conformance["schema"] == CURRENT_CONFORMANCE_SCHEMA
    assert conformance["current_milestone"] == "M9.119"
    assert len(conformance["maturity"]["criteria"]) == 21
    assert conformance["latest_evidence"]["passed"]
    assert conformance["latest_registration"]["schema"] == CURRENT_REGISTRATION_SCHEMA
    assert (
        conformance["latest_registration"]["registration"]["conformance_runner"]
        == CURRENT_CONFORMANCE_RUNNER
    )


def test_current_authority_studies_pass_without_promoting_physics() -> None:
    registration = run_model_registration_study()
    conformance = run_conformance_study()

    assert registration["passed"]
    assert conformance["passed"]
    assert not registration["m9_119"]["QCD_confinement_established"]
    assert not registration["m9_119"]["complete_electroweak_theory"]
    assert registration["m9_119"]["physical_claims_promoted"] == []
    assert not conformance["decision"]["external_physical_validation_complete"]


def test_platform_integration_contract_passes() -> None:
    result = run_platform_integration_contract()

    assert result["schema"] == "openwave.m9.platform-integration-contract.v2"
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["current_conformance_runner"] == CURRENT_CONFORMANCE_RUNNER
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
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_119a_non_abelian_gauge.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_119b_electroweak_higgs.py",
        root / "openwave/xperiments/m9_cat_ept/research/scripts/m9_119_current_registration.py",
    )
    assert all(path.is_file() for path in required)

    registry = (root / "MODELS.md").read_text(encoding="utf-8")
    profile = (root / "MODELS_M9.md").read_text(encoding="utf-8")
    roadmap = (
        root / "openwave/xperiments/m9_cat_ept/research/m9_roadmap_maturity.md"
    ).read_text(encoding="utf-8")
    assert "M9 - CAT/EPT" in registry
    assert "MODELS_LEGACY.md" in registry
    assert "evidence-derived maturity" in registry
    assert "M9.119" in registry
    assert "M9.119" in profile
    assert "openwave.model-registration.v22" in profile
    assert "model_registration_current.py" in profile
    assert "model_conformance_current.py" in profile
    assert "M9.119a" in roadmap
    assert "M9.119b" in roadmap
    assert "M9.119c" in roadmap
    assert "M9.120" in roadmap
