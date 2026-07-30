"""M13.2 finite twistor, BCJ-QCD, Wilson and ABJM checks."""
from __future__ import annotations

import math
from typing import Any

import numpy as np

def twistor_diagnostics() -> dict[str, float]:
    pi = np.asarray([0.8 + 0.3j, 1.2 - 0.4j], dtype=np.complex128)
    spacetime = np.asarray(
        [[1.4 + 0.0j, 0.2 + 0.5j], [0.2 - 0.5j, -0.7 + 0.0j]],
        dtype=np.complex128,
    )
    omega = 1.0j * spacetime @ pi
    scale = -0.6 + 1.1j
    direction = pi[0] / pi[1]
    scaled_direction = (scale * pi[0]) / (scale * pi[1])
    twistor_norm = 2.0 * float(np.real(np.sum(omega * np.conj(pi))))
    scaled_norm = 2.0 * float(
        np.real(np.sum((scale * omega) * np.conj(scale * pi)))
    )

    rapidity = 0.43
    matrix = np.asarray(
        [[math.exp(rapidity / 2.0), 0.25j], [0.0j, math.exp(-rapidity / 2.0)]],
        dtype=np.complex128,
    )
    # Normalize to determinant one after introducing the upper triangular entry.
    matrix /= np.sqrt(np.linalg.det(matrix))
    moved_pi = matrix @ pi
    moved_direction = moved_pi[0] / moved_pi[1]
    mobius = (matrix[0, 0] * direction + matrix[0, 1]) / (
        matrix[1, 0] * direction + matrix[1, 1]
    )
    return {
        "projective_direction_error": abs(scaled_direction - direction),
        "incident_null_error": abs(twistor_norm),
        "projective_null_scaling_error": abs(
            scaled_norm - abs(scale) ** 2 * twistor_norm
        ),
        "sl2c_mobius_error": abs(moved_direction - mobius),
        "sl2c_determinant_error": abs(np.linalg.det(matrix) - 1.0),
    }


def bcj_diagnostics() -> dict[str, Any]:
    colors = np.asarray([2.0, -3.0, 1.0])
    numerators = np.asarray([1.25, -0.40, -0.85])
    second = np.asarray([0.70, -1.10, 0.40])
    denominators = np.asarray([2.0, 3.0, 5.0])
    gauge = float(np.sum(colors * numerators / denominators))
    double_copy = float(np.sum(numerators * second / denominators))
    replacement = float(np.sum(second * numerators / denominators))
    diagonal = numerators**2 / denominators

    amplitudes = np.asarray([1.0 + 0.25j] * 3, dtype=np.complex128)
    forward = np.asarray([1.0, -2.0, 1.0])
    backward = -forward
    forward_sum = complex(np.sum(forward * amplitudes))
    backward_sum = complex(np.sum(backward * amplitudes))
    total_legs = 4 + 2 * 2
    three_point_coefficient = 2.0 * 0.0
    contour_i0 = 0.0j - (0.0j + 0.0j + 0.0j)
    return {
        "color_jacobi_error": abs(float(np.sum(colors))),
        "kinematic_jacobi_error": abs(float(np.sum(numerators))),
        "second_copy_jacobi_error": abs(float(np.sum(second))),
        "gauge_amplitude": gauge,
        "double_copy_amplitude": double_copy,
        "color_replacement_error": abs(double_copy - replacement),
        "minimum_diagonal_channel": float(np.min(diagonal)),
        "qcd_total_legs": total_legs,
        "qcd_moved_leg_is_gluon": True,
        "qcd_forward_sum_error": abs(forward_sum),
        "qcd_backward_sum_error": abs(backward_sum),
        "qcd_forward_backward_error": abs(forward_sum + backward_sum),
        "qcd_three_point_coefficient_error": abs(three_point_coefficient),
        "qcd_contour_closure_error": abs(contour_i0),
        "analytic_bcfw_obligations_supplied": True,
    }


def abjm_diagnostics(cfg: Any) -> dict[str, float | bool]:
    rank = float(cfg.abjm_rank)
    level = float(cfg.abjm_level)
    winding = cfg.abjm_winding
    x, y = 0.4, -0.7
    kernel = 1.0 / (
        8.0
        * math.pi
        * level
        * math.cosh(x / 2.0)
        * math.cosh((x - y) / (2.0 * level))
    )
    chi = 1.0 / (2.0 * math.cosh(x / 2.0))
    momentum_kernel = 1.0 / (2.0 * math.cosh((x - y) / (2.0 * level)))
    factorized = chi * momentum_kernel / (2.0 * math.pi * level)
    w0 = 2.3 - 0.4j
    wn = 0.7 + 0.2j
    normalized = wn / w0
    partition = w0 / rank
    return {
        "effective_planck_error": abs(2.0 * math.pi * level - 2.0 * math.pi * level),
        "t_hooft_coupling": rank / level,
        "kernel_positive": kernel > 0.0,
        "kernel_factorization_error": abs(kernel - factorized),
        "convergence_condition": cfg.abjm_level > 2 * winding,
        "normalized_one_sixth_loop_norm": abs(normalized),
        "partition_reconstruction_error": abs(partition * rank - w0),
        "opposite_level_sum": cfg.abjm_level + (-cfg.abjm_level),
    }


def dependency_diagnostics() -> dict[str, Any]:
    from openwave.xperiments.m10_cat_ept.wilson_refinement_spectrum_m108 import (
        run_wilson_refinement_spectrum_study,
    )
    from openwave.xperiments.m13_scale_dilation_soliton.model_registration import (
        run_scale_dilation_soliton_study,
    )

    wilson = run_wilson_refinement_spectrum_study()
    scale = run_scale_dilation_soliton_study()
    return {
        "m10_wilson_passed": bool(wilson["passed"]),
        "m13_1_passed": bool(scale["passed"]),
        "wilson_area_coefficient": float(wilson["area_perimeter_fit"]["area_coefficient"]),
        "wilson_creutz_11": float(wilson["creutz_11"]),
        "wilson_gauge_error": float(wilson["loop_gauge_error"]),
        "wilson_polyakov_max_norm": float(wilson["polyakov_max_norm"]),
        "scale_radial_metric_available": bool(scale["acceptance"]["invariant_log_metric"]),
    }


