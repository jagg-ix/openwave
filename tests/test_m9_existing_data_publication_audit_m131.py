from openwave.xperiments.m9_cat_ept.existing_data_publication_audit_m131 import run_leakage_publication_audit

def test_leakage_publication_audit():
    result = run_leakage_publication_audit()
    assert result["passed"]
    assert not result["audit"]["leakage_ids"]
