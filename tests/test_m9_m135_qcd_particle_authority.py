from openwave.xperiments.m9_cat_ept.m135_qcd_particle_authority import (
    run_m135_qcd_particle_authority,
)


def test_m135_qcd_particle_authority_preserves_scope():
    result = run_m135_qcd_particle_authority()
    assert result["passed"] and all(result["acceptance"].values())
    assert len(result["fingerprint"]) == 64
    assert result["decision"]["previous_qcd_underassessment_corrected"]
    assert result["decision"]["physlib_zil_particle_graph_is_authoritative"]
    assert result["decision"]["openwave_qcd_executable_bridge_added"]
    assert not result["decision"]["empirical_qcd_validation_complete"]
    assert not result["decision"]["unique_cat_ept_qcd_prediction_established"]
    assert result["decision"]["physical_claims_promoted"] == []
