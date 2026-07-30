from openwave.xperiments.m12_particle_zoo.standard_model_zoo_m121 import run_standard_model_zoo_study

def test_m12_standard_model_zoo():
    result = run_standard_model_zoo_study()
    assert result["passed"], result
    assert result["diagnostics"]["particle_type_count"] == 17
    assert result["diagnostics"]["gauge_state_count"] == 12
