from __future__ import annotations

import numpy as np

from openwave.xperiments.m10_cat_ept.qcd_functional_decoherence_m104 import (
    QCDFunctionalDecoherenceConfig,
    center_configurations,
    center_features,
    history_decoherence_matrix,
    history_weights,
    run_qcd_functional_decoherence_study,
    topological_indices,
    wilson_actions,
)
from openwave.xperiments.m10_cat_ept.dirac_cartan_2i_yukawa_model import (
    DiracCartan2IYukawaConfig,
)


def test_complete_finite_center_history_space_is_enumerated() -> None:
    cfg = QCDFunctionalDecoherenceConfig()
    configurations = center_configurations(cfg.plaquettes)
    assert len(configurations) == 81
    assert len(set(configurations)) == 81
    assert np.min(wilson_actions(configurations)) >= 0.0


def test_history_decoherence_is_hermitian_normalized_and_positive() -> None:
    cfg = QCDFunctionalDecoherenceConfig()
    particle = DiracCartan2IYukawaConfig()
    configurations = center_configurations(cfg.plaquettes)
    features = center_features(configurations)
    weights = history_weights(
        cfg,
        particle,
        wilson_actions(configurations),
        topological_indices(features),
    )
    decoherence = history_decoherence_matrix(weights, features, cfg)
    assert np.max(np.abs(decoherence - decoherence.conj().T)) <= 1.0e-13
    assert abs(np.trace(decoherence).real - 1.0) <= 1.0e-12
    assert np.min(np.linalg.eigvalsh(decoherence)) >= -1.0e-11


def test_complete_m10_4_study_passes() -> None:
    result = run_qcd_functional_decoherence_study()
    assert result["passed"]
    assert result["history_count"] == 81
    assert result["factorization_error"] <= 1.0e-13
    assert result["born_error"] <= 1.0e-13
    assert result["charge_conjugation_error"] <= 1.0e-13
    assert result["partition_derivative_error"] <= 1.0e-7
    assert result["first_source_error"] <= 1.0e-8
    assert result["connected_source_error"] <= 1.0e-6
    assert result["minimum_decoherence_eigenvalue"] >= -1.0e-11
    assert result["maximum_decohered_offdiag"] < result["maximum_pure_offdiag"]
    assert result["maximum_stronger_offdiag"] < result["maximum_decohered_offdiag"]
    assert result["decision"]["finite_qcd_path_integral_is_constructed"]
    assert result["decision"]["source_functional_and_connected_correlator_are_executed"]
    assert result["decision"]["history_decoherence_matrix_is_positive_and_environment_suppressed"]


def test_one_loop_qcd_functionals_converge() -> None:
    one_loop = run_qcd_functional_decoherence_study()["one_loop"]
    assert one_loop["feynman_parameter_error"] <= 1.0e-12
    assert one_loop["bubble_finite_part_error"] <= 1.0e-5
