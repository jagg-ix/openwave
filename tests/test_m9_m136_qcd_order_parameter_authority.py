from openwave.xperiments.m9_cat_ept.m136_qcd_order_parameter_authority import (
    run_m136_qcd_order_parameter_authority,
)


def test_m136_qcd_order_parameter_authority_passes() -> None:
    result = run_m136_qcd_order_parameter_authority()
    assert result["schema"] == "openwave.m9.m136-qcd-order-parameter-authority.v1"
    assert result["milestone"] == "M9.136"
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert not any(result["claim_boundaries"].values())
    assert len(result["study_fingerprint"]) == 64
