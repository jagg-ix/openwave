from openwave.xperiments.m9_cat_ept.independent_calibration_protocol import CalibrationAnchor,calibration_audit,validate_external_anchor_bundle


def external_bundle():
    anchors=[]
    for name in ("sigma0","clock_frequency","mass","charge_unit","force_unit"):
        anchors.append({"name":name,"value":1.0,"unit":"registered","evidence_class":"external","source":"independent measurement"})
    anchors += [
        {"name":"hbar","value":1.0,"unit":"action","evidence_class":"definition","source":"unit convention"},
        {"name":"c","value":1.0,"unit":"speed","evidence_class":"definition","source":"unit convention"},
    ]
    return {"anchors":anchors}


def test_external_anchor_bundle_can_close_independent_gate():
    result=validate_external_anchor_bundle(external_bundle())
    assert result["passed"]
    assert result["audit"]["independent_calibration_ready"]


def test_target_fitted_anchor_is_not_independent():
    anchors=[CalibrationAnchor("sigma0",1.0,"x","external","measurement",target_dependencies=("gravity",))]
    audit=calibration_audit(anchors)
    assert not audit["required_independent"]["sigma0"]["independent"]
    assert "gravity" in audit["self_fitted_targets"]


def test_dependency_cycle_is_rejected():
    anchors=(CalibrationAnchor("a",1.0,"x","derived","a",depends_on=("b",)),CalibrationAnchor("b",1.0,"x","derived","b",depends_on=("a",)))
    assert calibration_audit(anchors)["dependency_cycles"]
