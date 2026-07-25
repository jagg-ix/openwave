from openwave.xperiments.m9_cat_ept.klein_gordon_closure import (
    run_klein_gordon_closure,
)


def test_klein_gordon_closure_passes():
    result = run_klein_gordon_closure()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["modes"]["maximum_group_error"] < 2e-14
    assert result["modes"]["maximum_reverse_error"] < 2e-14
    assert result["modes"]["maximum_energy_error"] < 1e-12
    assert result["spatial"]["energy_drift"] < 2e-12
    assert result["decision"]["klein_gordon_validated_in_platform"]
    assert not result["decision"]["interacting_scalar_field_derived"]
