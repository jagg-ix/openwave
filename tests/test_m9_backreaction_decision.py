from openwave.xperiments.m9_cat_ept.backreaction_decision import run_backreaction_decision


def result():
    return run_backreaction_decision()


def test_components_pass():
    assert result()["acceptance"]["all_component_studies_pass"]


def test_trace_signature_distinguishes_amplitude_loss():
    assert result()["discrimination"]["amplitude_vs_lindblad_trace_margin"] >= 0.5


def test_purity_signature_distinguishes_dephasing():
    assert result()["discrimination"]["amplitude_vs_lindblad_purity_margin"] >= 0.3


def test_reservoir_transfer_and_extended_trace_close():
    signature = result()["signatures"]["explicit_reservoir"]
    assert signature["reservoir_transfer"] >= 0.5
    assert signature["extended_trace_error"] <= 5e-8


def test_operational_clocks_are_not_identical():
    values = result()["discrimination"]
    assert max(value for key, value in values.items() if key.endswith("tau_difference")) >= 0.1


def test_falsification_table_is_complete():
    assert len(result()["falsification_table"]) == 4


def test_negative_uniqueness_and_time_decisions_are_explicit():
    assert result()["unique_backreaction_selected"] is False
    assert result()["physical_time_identified"] is False


def test_full_decision_passes_with_claim_boundaries():
    study = result()
    assert study["passed"]
    assert all(study["acceptance"].values())
    assert study["classification"]["establishes"]
    assert study["classification"]["does_not_establish"]
