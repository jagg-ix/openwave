import openwave.xperiments.m9_cat_ept.criterion_maturity_m101 as maturity


def fake_authority():
    return {
        "formal_head": "acdbe8ce6456e66837bd18604cf3107d3181c4de",
        "fingerprint": "f" * 64,
        "passed": True,
        "components": {
            "coupled_action": {
                "passed": True,
                "symmetry_reduced_branch": True,
                "unrestricted_branch": False,
            },
            "packet_tbmt": {
                "passed": True,
                "adapter_constructed": True,
                "reduction_closed": False,
                "improves_on_rest_frame": True,
            },
            "clock": {
                "passed": True,
                "internal_calibration": True,
                "external_calibration": False,
            },
            "gravity": {
                "passed": True,
                "weak_field_evolution": True,
                "full_einstein_evolution": False,
            },
        },
    }


def test_m101_updates_axes_without_physical_overpromotion(monkeypatch):
    monkeypatch.setattr(maturity, "run_m101_evidence_authority", fake_authority)
    rows = {row.key: row for row in maturity.current_rows()}
    assert rows["de_broglie_clock"].calibration == "partial"
    assert rows["magnetic_moment_spin"].state == "reduced_constructed"
    assert rows["electric_force"].state == "reduced_constructed"
    assert rows["magnetic_force"].state == "reduced_constructed"
    assert rows["gravity"].state == "reduced_constructed"
    assert rows["de_broglie_clock"].identity == "open"
    assert rows["gravity"].calibration == "open"


def test_five_target_rows_remain_conditional(monkeypatch):
    monkeypatch.setattr(maturity, "run_m101_evidence_authority", fake_authority)
    payload = maturity.canonical_payload()
    by_key = {row["key"]: row for row in payload["criteria"]}
    for key in (
        "de_broglie_clock",
        "magnetic_moment_spin",
        "electric_force",
        "magnetic_force",
        "gravity",
    ):
        assert by_key[key]["headline"] == "conditional_validated"
    assert payload["policy"]["physical_identity_is_not_inferred"]
    assert payload["policy"]["external_validation_is_not_inferred"]
