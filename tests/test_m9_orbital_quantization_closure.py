from openwave.xperiments.m9_cat_ept.orbital_quantization_closure import (
    run_orbital_quantization_closure,
)


def test_orbital_quantization_closure_passes():
    result = run_orbital_quantization_closure()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["cross_angular_momentum"]["n2_spread"] < 3e-5
    assert result["cross_angular_momentum"]["n3_spread"] < 1e-5
    assert result["radial"]["node_counts"] == [0, 1, 2, 3]
    assert result["decision"]["orbital_quantization_validated_in_platform"]
    assert not result["decision"]["emergent_electron_and_nucleus_identified"]
