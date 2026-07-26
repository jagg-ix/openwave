import openwave.xperiments.m9_cat_ept.criterion_maturity_m102 as maturity


def fake_authority(*, branch: bool):
    return {
        "formal_head": "acdbe8ce6456e66837bd18604cf3107d3181c4de",
        "fingerprint": "f" * 64,
        "passed": True,
        "components": {
            "coupled_action": {
                "passed": True,
                "symmetry_reduced_branch": branch,
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


def test_implemented_action_does_not_create_a_state_when_gate_fails():
    payload = maturity.canonical_payload(fake_authority(branch=False))
    by_key = {row["key"]: row for row in payload["criteria"]}
    for key in ("magnetic_moment_spin", "electric_force", "magnetic_force"):
        assert by_key[key]["implementation"]["coupled_action"] == "implemented"
        assert not by_key[key]["implementation"]["winding_sector_state_gate"]
        assert by_key[key]["state"] == "not_constructed"
        assert "symmetry-reduced stationary-state gate" in by_key[key]["open"]
    assert payload["policy"]["carrier_implementation_is_not_state_existence"]


def test_state_axis_advances_only_after_state_gate_passes():
    payload = maturity.canonical_payload(fake_authority(branch=True))
    by_key = {row["key"]: row for row in payload["criteria"]}
    for key in ("magnetic_moment_spin", "electric_force", "magnetic_force"):
        assert by_key[key]["state"] == "reduced_constructed"
        assert "symmetry-reduced charged stationary state gate" in by_key[key]["closed"]


def test_clock_and_gravity_updates_retain_physical_boundaries():
    payload = maturity.canonical_payload(fake_authority(branch=False))
    by_key = {row["key"]: row for row in payload["criteria"]}
    assert by_key["de_broglie_clock"]["calibration"] == "partial"
    assert by_key["de_broglie_clock"]["identity"] == "open"
    assert by_key["gravity"]["state"] == "reduced_constructed"
    assert by_key["gravity"]["calibration"] == "open"
    assert by_key["gravity"]["headline"] == "conditional_validated"
