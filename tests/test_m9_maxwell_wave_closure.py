from openwave.xperiments.m9_cat_ept.maxwell_wave_closure import (
    run_maxwell_wave_closure,
)


def test_maxwell_wave_closure_passes():
    result = run_maxwell_wave_closure()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["decision"]["em_wave_sector_validated_in_platform"]
    assert result["decision"]["source_free_maxwell_plane_wave_established"]


def test_maxwell_promotion_keeps_stronger_boundaries():
    decision = run_maxwell_wave_closure()["decision"]
    assert not decision["electromagnetism_derived_from_full_cat_ept"]
    assert not decision["photon_quantization_established"]
    assert not decision["physical_units_calibrated"]
