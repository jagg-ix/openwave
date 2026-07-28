from openwave.xperiments.m9_cat_ept.m127_planckian_discrimination_authority import run_m127_planckian_discrimination_authority


def test_m127_authority_preserves_honest_non_discrimination():
    result = run_m127_planckian_discrimination_authority()
    assert result["passed"]
    assert result["decision"]["retrospective_discriminator_complete"]
    assert not result["decision"]["existing_evidence_uniquely_supports_entropic_time"]
    assert result["decision"]["prospective_raw_data_test_required"]
