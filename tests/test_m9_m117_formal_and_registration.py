from openwave.xperiments.m9_cat_ept.formalization_m117_extension import (
    CURRENT_FORMAL_HEAD,
    FORMAL_SOURCES,
    expected_source_blobs,
    run_formalization_m117_extension,
    validate_formalization_m117,
)
from openwave.xperiments.m9_cat_ept.m117_coarse_graining_evidence_authority import (
    run_m117_coarse_graining_evidence_authority,
)
from openwave.xperiments.m9_cat_ept.model_registration_m117 import (
    run_model_registration_study,
)


def test_m117_formal_sources_are_exact_and_fail_closed():
    result = run_formalization_m117_extension()
    assert result["passed"]
    assert len(FORMAL_SOURCES) == 4
    assert len(CURRENT_FORMAL_HEAD) == 40
    drift = expected_source_blobs()
    first = next(iter(drift))
    drift[first] = "0" * 40
    validation = validate_formalization_m117(observed_source_blobs=drift)
    assert not validation["passed"]
    assert any(first in error for error in validation["errors"])


def test_m117_evidence_and_registration_preserve_boundaries():
    evidence = run_m117_coarse_graining_evidence_authority()
    assert evidence["passed"]
    assert evidence["decision"]["M9_117a_dynamic_count_flow_complete"]
    assert evidence["decision"]["M9_117b_Gaussian_fixed_point_adapter_complete"]
    assert evidence["decision"]["M9_117c_multi_resolution_gravity_complete"]
    assert not evidence["decision"]["M9_118_external_calibration_unblocked"]

    registration = run_model_registration_study()
    assert registration["passed"]
    assert registration["schema"] == "openwave.model-registration.v21"
    current = registration["m9_117"]
    assert current["formal_source_count"] == 4
    assert current["universal_holographic_G_preserved"]
    assert current["low_mode_gravity_scale_consistency"]
    assert not current["particle_mass_endpoint_derived"]
    assert not current["interacting_CAT_EPT_fixed_point_constructed"]
    assert not current["physical_calibration_complete"]
    assert current["physical_claims_promoted"] == []
