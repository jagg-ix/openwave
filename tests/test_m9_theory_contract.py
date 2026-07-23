import pytest
from openwave.xperiments.m9_cat_ept.theory_contract import (
    ContractError, EvolutionTermSpec, FieldSpec, ParameterSpec, TheoryManifest,
    TheoryRegistry, cat_ept_manifest, run_theory_contract_study, validate_manifest,
)

def test_reference_manifest_is_valid():
    result = validate_manifest(cat_ept_manifest())
    assert result["valid"]
    assert result["has_reversible_sector"]
    assert result["has_irreversible_sector"]
    assert result["has_constraint_sector"]

def test_fingerprint_is_deterministic():
    manifest = cat_ept_manifest()
    assert manifest.fingerprint() == manifest.fingerprint()
    assert len(manifest.fingerprint()) == 64

def test_registry_rejects_duplicate_version():
    registry = TheoryRegistry(); manifest = cat_ept_manifest(); registry.register(manifest)
    with pytest.raises(ContractError): registry.register(manifest)

def test_unknown_field_reference_is_rejected():
    m = TheoryManifest("x","1",(FieldSpec("x","dynamic"),),(),
        (EvolutionTermSpec("bad","reversible",("missing",),("x",)),),
        cat_ept_manifest().observables[:1],(),{})
    with pytest.raises(ContractError): validate_manifest(m)

def test_parameter_bounds_are_enforced():
    base = cat_ept_manifest()
    m = TheoryManifest(base.name,base.version,base.fields,
        (ParameterSpec("bad",2.0,(0.0,1.0)),),base.evolution_terms,base.observables,base.laws,{})
    with pytest.raises(ContractError): validate_manifest(m)

def test_manifest_declares_core_cat_ept_ledgers():
    names = {f.name for f in cat_ept_manifest().fields}
    assert {"entropy","reservoir","constraint"} <= names

def test_contract_has_no_acquisition_requirement():
    assert cat_ept_manifest().metadata["requires_data_acquisition"] is False

def test_full_study_passes():
    result = run_theory_contract_study()
    assert result["passed"] and all(result["acceptance"].values())
