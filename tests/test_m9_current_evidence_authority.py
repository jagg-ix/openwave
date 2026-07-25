from types import SimpleNamespace

from openwave.xperiments.m9_cat_ept.current_evidence_authority import (
    authority_fingerprint,
    evaluate_current_identity,
    run_current_evidence_authority,
)
from openwave.xperiments.m9_cat_ept.physical_calibration_ledger_v2 import (
    run_physical_calibration_ledger_v2,
)


def test_current_evidence_authority_composes_m9_96_without_promotion():
    result = run_current_evidence_authority()
    assert result["passed"] and all(result["acceptance"].values())
    assert result["charged_branch"]["passing_candidate_count"] == 0
    assert not result["charged_branch"]["charged_stationary_branch_constructed"]
    assert result["maxwell_source"]["passed"]
    assert result["force_triangle"]["passed"]
    assert not result["force_triangle"]["center_acceleration_measured"]
    assert result["status"] == {
        "magnetic_moment_spin": "partial",
        "electric_force": "partial",
        "magnetic_force": "partial",
    }
    assert result["decision"]["criterion_rows_promoted"] == []
    assert not result["decision"]["physical_identity_established"]


def test_authority_fingerprint_is_deterministic():
    result = run_current_evidence_authority()
    payload = {
        key: value
        for key, value in result.items()
        if key not in {"fingerprint", "acceptance", "passed", "decision"}
    }
    assert len(result["fingerprint"]) == 64
    assert authority_fingerprint(payload) == authority_fingerprint(payload)


def test_current_three_row_calibration_ledger_preserves_shared_blocker():
    result = run_physical_calibration_ledger_v2()
    assert result["passed"] and all(result["acceptance"].values())
    assert len(result["rows"]) == 3
    assert result["status_counts"]["blocked_by_model"] == 3
    assert result["decision"]["shared_blocker"] == "stable charged spinorial stationary branch"
    assert not result["decision"]["magnetic_moment_spin_promoted"]
    assert not result["decision"]["electric_force_promoted"]
    assert not result["decision"]["magnetic_force_promoted"]


def test_current_identity_fails_even_when_external_flags_are_asserted():
    model = SimpleNamespace(
        spec=SimpleNamespace(
            particle_id="candidate",
            winding_sector=3,
            physical_assignment="electron",
            calibration_id="test-calibration",
        ),
        measure=lambda state: {
            "normalization_error": 0.0,
            "boundary_fraction": 0.0,
        },
    )
    state = SimpleNamespace(declared_winding_sector=3, winding_embedded=True)
    evidence = {
        "charge_unit_calibrated": True,
        "rest_energy_calibrated": True,
        "clock_identified": True,
        "spin_and_exchange_closed_on_same_branch": True,
        "physical_magnetic_moment_calibrated": True,
        "physical_force_calibrated": True,
        "out_of_sample_prediction": True,
    }
    certificate = evaluate_current_identity(model, state, evidence)
    assert not certificate["passed"]
    assert certificate["gates"]["current_evidence_authority_passes"]
    assert not certificate["gates"]["charged_stationary_branch_is_closed"]
    assert certificate["decision"]["current_charged_stationary_failure_blocks_identity"]
