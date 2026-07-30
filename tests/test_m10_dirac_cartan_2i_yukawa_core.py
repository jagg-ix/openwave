from __future__ import annotations

from openwave.xperiments.m10_cat_ept.dirac_cartan_2i_yukawa_model import (
    binary_icosahedral_diagnostics,
    construct_state,
    run_m10_core_study,
)
from openwave.xperiments.m10_cat_ept.formal_authority import FORMAL_HEAD
from openwave.xperiments.m10_cat_ept.model_registration import (
    run_model_registration_study,
)


def test_complete_binary_icosahedral_group_executes() -> None:
    diagnostics = binary_icosahedral_diagnostics()
    assert diagnostics["cardinality"] == 120
    assert diagnostics["multiplication_closure_failures"] == 0
    assert diagnostics["maximum_norm_error"] <= 2.0e-12
    assert diagnostics["maximum_unitarity_error"] <= 2.0e-12
    assert diagnostics["central_sign_closed"]


def test_m10_constructs_one_four_spinor_state() -> None:
    state = construct_state()
    assert state.spinor.shape == (4, 17, 17, 17)
    assert state.measured_winding == 3
    assert state.winding_quantization_error <= 2.0e-12
    assert state.minimum_contour_amplitude > 1.0e-3


def test_m10_core_study_establishes_all_registered_relations() -> None:
    result = run_m10_core_study()
    assert result["passed"]
    assert result["decision"]["dirac_cartan_2i_yukawa_carrier_constructed"]
    assert result["decision"]["complete_binary_icosahedral_action_executed"]
    assert result["decision"]["yukawa_compton_complex_mass_assembled"]
    assert result["decision"]["cartan_axial_contact_assembled"]
    assert result["measured_winding"] == 3
    assert result["dirac_mass_shell_error"] <= 2.0e-14


def test_m10_registration_is_separate_and_formally_pinned() -> None:
    result = run_model_registration_study()
    assert result["passed"]
    assert result["model_id"] == "M10"
    assert result["milestone"] == "M10.3"
    assert result["carrier_milestone"] == "M10.1"
    assert result["closure_milestone"] == "M10.2"
    assert result["formal_authority"]["head"] == FORMAL_HEAD
    assert result["formal_authority"]["pull_request"] == 41
    assert all(
        len(source["sha"]) == 40 for source in result["formal_authority"]["sources"]
    )
    assert result["second_quantized_formal_authority"]["pull_request"] == 42
    assert result["decision"]["m10_registered_as_separate_model"]
    assert result["decision"]["one_particle_and_second_quantized_authorities_are_content_pinned"]
    assert result["decision"]["m10_second_quantized_fock_carrier_is_latest"]
    assert not result["decision"]["m9_registration_rewritten"]
