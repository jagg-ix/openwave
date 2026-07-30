from openwave.xperiments.m12_particle_zoo.electroweak_lepton_neutrino_m122 import run_electroweak_lepton_neutrino_study

def test_m12_electroweak_lepton_neutrino():
    result = run_electroweak_lepton_neutrino_study()
    assert result["passed"], result
    assert result["diagnostics"]["pmns_unitarity_error"] < 1e-14
