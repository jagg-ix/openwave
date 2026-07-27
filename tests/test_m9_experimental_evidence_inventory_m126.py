from openwave.xperiments.m9_cat_ept.experimental_evidence_inventory_m126 import run_experimental_evidence_inventory

def test_inventory_recognizes_existing_papers():
    r=run_experimental_evidence_inventory()
    assert r["passed"]
    assert len(r["planckian_records"])==8
    assert len(r["papers"])==3
    assert not r["decision"]["qualified_raw_dataset_complete"]
