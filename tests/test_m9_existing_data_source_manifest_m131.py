from openwave.xperiments.m9_cat_ept.existing_data_source_manifest_m131 import run_source_manifest_verifier

def test_source_manifest_verifier():
    result = run_source_manifest_verifier()
    assert result["passed"]
    assert result["valid"]
