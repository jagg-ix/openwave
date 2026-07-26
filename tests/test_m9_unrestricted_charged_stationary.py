import numpy as np
import openwave.xperiments.m9_cat_ept.unrestricted_charged_stationary as target


def _row(residual: float = 0.1):
    return {"projection_calls_after_initialization":0,"full":{"relative_stationary_residual":residual,"norm":1.0},"winding":{"integer_winding":3,"quantization_error":0.0},"down_component_fraction":0.1,"action_nonincrease":True,"action":{"total":1.0},"radius":1.0,"maxwell":{"gauss_relative_residual":0.0,"ampere_relative_residual":0.0,"magnetic_divergence_max":0.0}}


def test_unrestricted_gate_is_outcome_driven(monkeypatch):
    row=_row()
    monkeypatch.setattr(target,"solve_unrestricted_candidates",lambda:{"rows":[row,row,row],"best_index":0,"maximum_seed_distance":0.01})
    monkeypatch.setattr(target,"best_unrestricted_state",lambda:(np.zeros((2,17,17,17),dtype=np.complex128),row))
    monkeypatch.setattr(target,"_tube",lambda state,kind,cfg:{"perturbation":kind,"passed":True})
    target.run_unrestricted_charged_stationary.cache_clear()
    result=target.run_unrestricted_charged_stationary()
    assert result["passed"]
    assert result["unrestricted_stationary_state_constructed"]
    assert result["unrestricted_orbital_stability_qualified"]
    assert not result["decision"]["projection_used_after_initialization"]


def test_failed_residual_does_not_fail_campaign_or_create_state(monkeypatch):
    row=_row(0.4)
    monkeypatch.setattr(target,"solve_unrestricted_candidates",lambda:{"rows":[row,row,row],"best_index":0,"maximum_seed_distance":0.01})
    monkeypatch.setattr(target,"best_unrestricted_state",lambda:(np.zeros((2,17,17,17),dtype=np.complex128),row))
    monkeypatch.setattr(target,"_tube",lambda state,kind,cfg:{"perturbation":kind,"passed":True})
    target.run_unrestricted_charged_stationary.cache_clear()
    result=target.run_unrestricted_charged_stationary()
    assert result["passed"]
    assert not result["unrestricted_stationary_state_constructed"]
    assert not result["unrestricted_orbital_stability_qualified"]
