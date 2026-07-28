from openwave.xperiments.m9_cat_ept.experimental_evidence_qualification_m126 import run_experimental_evidence_qualification

def test_qualification_gate_is_fail_closed():
    r=run_experimental_evidence_qualification()
    assert r["passed"]
    assert r["qualified_gate"]["passed"]
    assert not r["external_promotion_gate"]["passed"]
    assert "data:raw_values_and_uncertainties" in r["external_promotion_gate"]["missing"]
