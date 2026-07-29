from __future__ import annotations

from openwave.xperiments.m9_cat_ept.model_conformance_latest import (
    run_conformance_study,
)
from openwave.xperiments.m9_cat_ept.model_registration_latest import (
    run_model_registration_study,
)
from openwave.xperiments.m9_cat_ept.platform_integration_latest_m141 import (
    run_platform_integration_contract,
)


def test_latest_registration_distinguishes_stable_and_latest() -> None:
    result = run_model_registration_study()
    assert result["passed"]
    assert result["latest_milestone"] == "M9.141"
    assert result["stable_compatibility"]["milestone"] == "M9.126"
    assert result["decision"]["stable_current_alias_is_not_rewritten"]
    assert result["decision"]["three_dimensional_charged_carrier_registered"]
    assert result["decision"]["physical_claims_promoted"] == []


def test_latest_conformance_keeps_all_statuses_unchanged() -> None:
    result = run_conformance_study()
    assert result["passed"]
    assert result["latest_milestone"] == "M9.141"
    assert result["maturity"]["status_counts"] == {
        "validated": 7,
        "partial": 13,
        "negative": 1,
        "not_yet": 0,
    }
    assert result["decision"]["three_dimensional_charged_carrier_is_available"]
    assert result["decision"]["criterion_rows_promoted"] == []


def test_latest_public_platform_contract_passes() -> None:
    result = run_platform_integration_contract()
    assert result["passed"]
    assert result["latest_milestone"] == "M9.141"
    assert result["stable_compatibility"]["milestone"] == "M9.126"
    assert result["decision"]["three_dimensional_charged_carrier_is_public"]
    assert result["decision"]["physical_claims_promoted"] == []
