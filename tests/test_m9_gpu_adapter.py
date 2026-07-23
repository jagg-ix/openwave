import numpy as np
import pytest
from openwave.xperiments.m9_cat_ept.gpu_adapter import (
    AdapterError, FlatDeviceBuffer, compile_manifest, execute_flat_device,
    execute_numpy, reference_manifest, reference_parameters, reference_state,
    run_gpu_adapter_study
)

def test_manifest_compiles_aligned_layout():
    p=compile_manifest(reference_manifest())
    assert all(s.offset_bytes%64==0 for s in p.slices)

def test_buffer_roundtrip():
    m=reference_manifest(); p=compile_manifest(m); s=reference_state(m)
    b=FlatDeviceBuffer(p); b.load(s); out=b.export()
    assert all(np.array_equal(s[k],out[k]) for k in s)

def test_numpy_flat_parity():
    m=reference_manifest(); p=compile_manifest(m); s=reference_state(m); q=reference_parameters()
    a=execute_numpy(p,s,q); b=execute_flat_device(p,s,q)
    assert max(np.max(np.abs(a[k]-b[k])) for k in a)<=2e-15

def test_balance_observable_closes():
    m=reference_manifest(); p=compile_manifest(m)
    out=execute_flat_device(p,reference_state(m),reference_parameters())
    assert abs(out["observable"][0]+out["observable"][1]-1)<=2e-14

def test_malformed_shape_rejected():
    m=reference_manifest(); p=compile_manifest(m); s=reference_state(m); s["psi"]=np.zeros(3,dtype=np.complex128)
    with pytest.raises(AdapterError): execute_flat_device(p,s,reference_parameters())

def test_parameter_set_rejected():
    m=reference_manifest(); p=compile_manifest(m)
    with pytest.raises(AdapterError): execute_flat_device(p,reference_state(m),{"dt":.1})

def test_fingerprint_is_deterministic():
    m=reference_manifest()
    assert compile_manifest(m).fingerprint==compile_manifest(m).fingerprint

def test_full_study_passes():
    r=run_gpu_adapter_study()
    assert r["passed"] and all(r["acceptance"].values())
