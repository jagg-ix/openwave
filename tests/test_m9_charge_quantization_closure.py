from openwave.xperiments.m9_cat_ept.charge_quantization_closure import (
    run_charge_quantization_closure,
)


def test_charge_quantization_closure_passes():
    result = run_charge_quantization_closure()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["arithmetic"]["table"] == {
        "electron": "-1",
        "neutrino": "0",
        "up": "2/3",
        "down": "-1/3",
    }
    assert result["winding"]["maximum_resolution_error"] < 5e-15
    assert result["decision"]["charge_quantization_validated_in_platform"]
    assert not result["decision"]["elementary_electric_charge_identity_established"]
