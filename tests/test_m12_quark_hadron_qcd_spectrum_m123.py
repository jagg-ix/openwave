from openwave.xperiments.m12_particle_zoo.quark_hadron_qcd_spectrum_m123 import run_particle_zoo_model_study

def test_m12_quark_hadron_qcd_spectrum():
    result = run_particle_zoo_model_study()
    assert result["passed"], result
    assert result["coverage"]["fundamental_particle_types"] == 17
    assert result["diagnostics"]["m10_qcd_passed"]
