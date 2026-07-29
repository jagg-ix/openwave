from __future__ import annotations

from openwave.xperiments.m9_cat_ept.canonical_particle_model_m140 import (
    ACTION_TERM_MAP,
    COMPONENTS,
    MILESTONE,
    canonical_payload,
    fingerprint,
    resolve_symbol,
    run_canonical_model_contract,
)


def test_m140_canonical_contract_passes_without_promotion() -> None:
    result = run_canonical_model_contract()
    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["milestone"] == "M9.140"
    assert result["decision"]["existing_m9_surfaces_are_unified_behind_one_api"]
    assert result["decision"]["physical_claims_promoted"] == []


def test_m140_all_component_symbols_resolve() -> None:
    assert len(COMPONENTS) == 6
    assert all(resolve_symbol(component.symbol) is not None for component in COMPONENTS)
    assert all(not component.physical_promotion for component in COMPONENTS)


def test_m140_action_map_keeps_imaginary_action_gap_explicit() -> None:
    row = next(item for item in ACTION_TERM_MAP if item["id"] == "imaginary-action-relaxation")
    assert row["sector"] == "imaginary"
    assert row["status"] == "effective-law-not-yet-derived-from-one-discrete-S_I"
    assert "variational derivative" in row["required_gate"]


def test_m140_payload_and_fingerprint_are_stable() -> None:
    payload = canonical_payload()
    assert MILESTONE == "M9.140"
    assert payload["lineage"]["stable_compatibility_alias"] == "M9.126"
    assert not payload["claim_boundary"]["physical_particle_identity"]
    assert len(fingerprint(payload)) == 64
    assert fingerprint(payload) == fingerprint(payload)
