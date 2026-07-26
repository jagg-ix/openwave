import openwave.xperiments.m9_cat_ept.model_registration_m105 as target


def fake_previous():
    return {"schema":"openwave.model-registration.v10","claim_boundary":{}}


def fake_conformance():
    return {"schema":"openwave.m9.models-conformance.v20","formal_authority":{"physlib":{"head":"eba0124fcfbc1216d973bb6f504c5a6d324de60c"},"zil":{"current_head":"e09723a44185a1e70031ad2661c8009dc98bef74"}},"evidence":{"components":{"unrestricted_state":{"passed":True,"stationary_gate":False,"orbital_gate":False},"packet_refinement":{"passed":True,"refinement_gate":False},"calibration":{"passed":True,"independent_ready":False,"withheld_predictions_executed":False}}},"summary":{"validated_in_scope":7,"conditional_validated":5,"reduced_model_validated":3,"calibration_pending":1,"candidate":4,"negative":1}}


def test_registration_keeps_failed_subgates_explicit(monkeypatch):
    monkeypatch.setattr(target,"previous_payload",fake_previous)
    monkeypatch.setattr(target,"conformance_payload",fake_conformance)
    payload=target.canonical_registration_payload()
    current=payload["m9_103_105"]
    assert payload["schema"]=="openwave.model-registration.v11"
    assert current["unrestricted_campaign_registered"]
    assert not current["unrestricted_stationary_gate"]
    assert not current["packet_refinement_gate"]
    assert not current["independent_calibration_ready"]
    assert current["physical_claims_promoted"]==[]
