from copy import deepcopy
from openwave.xperiments.m9_cat_ept.three_clock_holdout_protocol import build_live_template, build_synthetic_fixture, evaluate_package, run_three_clock_holdout_protocol, validate_package

def test_holdout_protocol_blocks_live_and_separates_synthetic():
    result = run_three_clock_holdout_protocol()
    assert result['passed']
    assert result['live_evaluation']['status'] == 'blocked'
    assert result['synthetic_evaluation']['status'] == 'evaluated'
    assert not result['synthetic_evaluation']['external_validation_complete']

def test_commitment_tampering_is_rejected():
    fixture = build_synthetic_fixture()
    fixture['prediction']['rows'][0]['coherence_magnitude'] += 0.2
    assert not validate_package(fixture, allow_synthetic=True)['accepted_for_execution']
    assert evaluate_package(build_live_template())['status'] == 'blocked'
