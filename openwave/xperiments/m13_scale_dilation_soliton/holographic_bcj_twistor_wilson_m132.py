"""M13.2 finite holographic, twistor, BCJ-QCD, and Wilson-loop closure.

The executable layer mirrors exact finite/algebraic theorem surfaces from
``entropic-physlib-linear-full``.  It deliberately does not claim an evaluated
interacting Witten diagram, a BCFW derivation from QCD Feynman rules, a full
SU(2,2) twistor action, or a continuum gauge/string duality.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Any, Mapping

from .ads_cft_m132 import (
    ads_cft_diagnostics,
    extended_ads_diagnostics,
    rt_diagnostics,
    source_response_diagnostics,
)
from .twistor_bcj_wilson_m132 import (
    abjm_diagnostics,
    bcj_diagnostics,
    dependency_diagnostics,
    twistor_diagnostics,
)


MILESTONE = "M13.2"
SCHEMA = "openwave.m13.holographic-bcj-twistor-wilson.v1"
FORMAL_HEAD = "8bafa9ab93cbb39e85909fc3837bb4b6e0dec748"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/AdSCFT/GKPWittenAdSCFTDictionary.lean",
        "sha": "d9f9bf5e00fd1a4880520cab6c4e5458ee4aa1d3",
        "theorems": [
            "massDimension_relation",
            "bulkToBoundaryKernel_scaling",
            "bulkToBoundaryKernel_boundary_limit",
            "cubicWittenDensity_jacobian_covariance",
            "gkpWitten_affine_source_hessian",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/AdSCFT/GKPWittenCasimir.lean",
        "sha": "61d5bf1a710c835ca957b5586cc1570dad9c41c8",
        "theorems": [
            "conformalDimension_gegenbauer",
            "conformalDimension_reggeCasimir",
            "conformalDimension_cutkosky",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/AdSCFT/GKPWittenOperatorSpectrum.lean",
        "sha": "f968c21eeb7ad34cd03a4372d490d9def7e208ed",
        "theorems": [
            "hydrogenOperator_twoPoint",
            "hydrogen_shadow_dimension",
            "regge_dimension_succ",
            "gegenbauerOperator_twoPoint",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/AdSCFT/FiniteBaryonDensityPhaseTransition.lean",
        "sha": "979bd61e9badb423aa04c303074db23f2bd1d606",
        "theorems": [
            "sRen_hasDerivAt",
            "grandPotential_hasDerivAt_transition",
            "density_slope_transition",
            "grandPotential_shift",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/AdSCFT/LovelockEntanglementAdSCoefficients.lean",
        "sha": "bc2a7a6ba42c561c4f423aae95ccf2ea7b543627",
        "theorems": [
            "adsOnShellLovelockCoeff_pos_iff_le_M",
            "waldEntropyAreaCoeff_einstein",
            "waldEntropyAreaCoeff_pos_iff",
            "symplecticFlowCoeff_eq_mul_area",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/AdSCFT/RyuTakayanagiFormulaAlgebra.lean",
        "sha": "c14aede2c8654bdbdb4aedfca543c36872c65e55",
        "theorems": [
            "rt_log_square_prefactor_identity",
            "rtPoincareLineDensity_regulated_integral_eq_neg_two_log",
            "cftEntropyVacuumLine_strongSubadditivity",
            "cftEntropyFiniteT_strongSubadditivity",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/PenroseTwistorSpace.lean",
        "sha": "dbb5cd4a0e264b491c1dd255469564fce0d7711a",
        "theorems": [
            "twistorDirection_smul",
            "isNullTwistor_smul",
            "incident_isNull",
            "sl2c_twistorDirection",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/BCJDoubleCopy/ColorKinematicsDoubleCopy.lean",
        "sha": "110a42b466c7fcf8be68be4326cb1d0c9197043c",
        "theorems": [
            "bcjDoubleCopy_diagonal_nonneg",
            "faradayBCJDuality",
            "cubicDoubleCopy_eq_cubicAmplitude_colorReplacement",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Particles/QCDFundamentalBCJRelations.lean",
        "sha": "5756653f5dbd58ac14fef7307d03223e7bf81304",
        "theorems": [
            "forwardBCJRelation_iff_backwardBCJRelation",
            "threePoint_fundamentalBCJ",
            "fundamentalBCJ_inductionStep_closes",
            "qcdPrimitiveBCJ_KLT_pole_cancellations_tetrad_invariant",
        ],
    },
    {
        "path": "Physlib/QFT/PathIntegral/FiniteWilsonGaugeModel.lean",
        "sha": "870efa65de9037ea7c8e617628b15c19fb3de521",
        "theorems": [
            "boltzmannFactor_pos",
            "sourceCoupledPartition_linearSource_hasDerivAt_zero",
        ],
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/ABJMWilsonLoopsFermiGas/AnchorsBPSWilsonLoops.lean",
        "sha": "257e17018234a3cf7da7dbefb5bdadfa12291c05",
        "theorems": [
            "abjm_effectivePlanck_eq_two_pi_level",
            "abjmFermiGasKernel_eq_chi_momentumKernel",
            "abjm_convergentLevel_iff",
            "abjmOneSixthWilson_eq_wittenNormalizedExpectation",
        ],
    },
)


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class HolographicAmplitudeConfig:
    boundary_dimension: float = 4.0
    mass_radius_sq: float = 5.0
    ads_radius: float = 2.0
    newton_constant: float = 0.25
    radial_coordinate: float = 0.7
    boundary_coordinate: float = 1.3
    boundary_source: float = -0.4
    dilation: float = 1.8
    cubic_dimensions: tuple[float, float, float] = (3.0, 4.0, 5.0)
    rt_interval: float = 2.4
    rt_cutoff: float = 0.08
    inverse_temperature: float = 7.0
    ssa_segments: tuple[float, float, float] = (0.7, 1.1, 0.9)
    source_step: float = 1.0e-6
    abjm_rank: int = 3
    abjm_level: int = 8
    abjm_winding: int = 2

    def validate(self) -> None:
        positive = (
            self.boundary_dimension,
            self.ads_radius,
            self.newton_constant,
            self.radial_coordinate,
            self.dilation,
            self.rt_interval,
            self.rt_cutoff,
            self.inverse_temperature,
            self.source_step,
        )
        if min(positive) <= 0.0:
            raise ValueError("positive holographic controls required")
        if self.rt_cutoff >= math.pi / 2.0:
            raise ValueError("RT angular cutoff must lie below pi/2")
        if min(self.ssa_segments) <= 0.0:
            raise ValueError("positive adjacent intervals required")
        if self.abjm_rank <= 0 or self.abjm_level <= 0 or self.abjm_winding < 0:
            raise ValueError("valid ABJM parameters required")
        if (self.boundary_dimension / 2.0) ** 2 + self.mass_radius_sq < 0.0:
            raise ValueError("bulk scalar violates the BF bound")


def canonical_payload(
    config: HolographicAmplitudeConfig | None = None,
) -> dict[str, Any]:
    cfg = HolographicAmplitudeConfig() if config is None else config
    return {
        "schema": SCHEMA,
        "model_id": "M13",
        "milestone": MILESTONE,
        "model": "CAT/EPT finite AdS/CFT--twistor--BCJ/QCD--Wilson closure",
        "configuration": asdict(cfg),
        "lineage_dependencies": ["M10.8", "M13.1"],
        "study_api": (
            "openwave.xperiments.m13_scale_dilation_soliton."
            "holographic_bcj_twistor_wilson_m132:run_holographic_amplitude_study"
        ),
        "formal_authority": {
            "repository": "jagg-ix/entropic-physlib-private",
            "branch": "entropic-physlib-linear-full",
            "head": FORMAL_HEAD,
            "sources": list(FORMAL_SOURCES),
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


def run_holographic_amplitude_study(
    config: HolographicAmplitudeConfig | None = None,
) -> dict[str, Any]:
    cfg = HolographicAmplitudeConfig() if config is None else config
    cfg.validate()
    diagnostics: dict[str, Any] = {}
    diagnostics.update(ads_cft_diagnostics(cfg))
    diagnostics.update(source_response_diagnostics(cfg))
    diagnostics.update(rt_diagnostics(cfg))
    diagnostics.update(extended_ads_diagnostics(cfg))
    diagnostics.update(twistor_diagnostics())
    diagnostics.update(bcj_diagnostics())
    diagnostics.update(abjm_diagnostics(cfg))
    diagnostics.update(dependency_diagnostics())

    acceptance = {
        "gkp_dictionary_and_boundary_limit": (
            diagnostics["mass_dimension_error"] < 5.0e-13
            and diagnostics["bf_margin"] >= 0.0
            and diagnostics["kernel_scaling_error"] < 5.0e-13
            and bool(diagnostics["boundary_limit_monotone"])
            and diagnostics["boundary_limit_last_error"] < 2.0e-3
            and diagnostics["cubic_jacobian_covariance_error"] < 5.0e-13
        ),
        "finite_gkp_source_response": (
            diagnostics["propagator_symmetry_error"] < 5.0e-14
            and diagnostics["source_first_derivative_error"] < 5.0e-9
            and diagnostics["source_hessian_error"] < 2.0e-4
        ),
        "ryu_takayanagi_and_entropy_inequalities": (
            diagnostics["rt_integral_error"] < 2.0e-6
            and diagnostics["rt_cft_prefactor_error"] < 5.0e-13
            and diagnostics["vacuum_ssa_margin"] >= -5.0e-13
            and diagnostics["thermal_ssa_margin"] >= -5.0e-13
            and diagnostics["thermal_minus_vacuum"] >= -5.0e-13
        ),
        "extended_ads_cft_spectrum_thermodynamics_and_lovelock": (
            diagnostics["regge_dimension_error"] < 5.0e-13
            and diagnostics["regge_tower_step_error"] < 5.0e-13
            and diagnostics["regge_shadow_error"] < 5.0e-13
            and diagnostics["gegenbauer_dimension_error"] < 5.0e-13
            and diagnostics["finite_density_derivative_error"] < 5.0e-9
            and diagnostics["finite_density_transition_zero_error"] < 5.0e-14
            and diagnostics["finite_density_grand_shift_error"] < 5.0e-13
            and diagnostics["finite_density_second_order_slope"] > 0.0
            and diagnostics["lovelock_survival_pattern"]
            and diagnostics["lovelock_einstein_normalization"]
            and diagnostics["lovelock_symplectic_area_relation"]
        ),
        "projective_twistor_and_lorentz_boundary_action": (
            diagnostics["projective_direction_error"] < 5.0e-14
            and diagnostics["incident_null_error"] < 5.0e-13
            and diagnostics["projective_null_scaling_error"] < 5.0e-13
            and diagnostics["sl2c_mobius_error"] < 5.0e-14
            and diagnostics["sl2c_determinant_error"] < 5.0e-14
        ),
        "bcj_color_kinematics_and_double_copy": (
            diagnostics["color_jacobi_error"] < 5.0e-14
            and diagnostics["kinematic_jacobi_error"] < 5.0e-14
            and diagnostics["second_copy_jacobi_error"] < 5.0e-14
            and diagnostics["color_replacement_error"] < 5.0e-14
            and diagnostics["minimum_diagonal_channel"] >= 0.0
        ),
        "primitive_qcd_bcj_obligations": (
            diagnostics["qcd_total_legs"] == 8
            and diagnostics["qcd_moved_leg_is_gluon"]
            and diagnostics["qcd_forward_sum_error"] < 5.0e-14
            and diagnostics["qcd_backward_sum_error"] < 5.0e-14
            and diagnostics["qcd_forward_backward_error"] < 5.0e-14
            and diagnostics["qcd_three_point_coefficient_error"] < 5.0e-14
            and diagnostics["qcd_contour_closure_error"] < 5.0e-14
            and diagnostics["analytic_bcfw_obligations_supplied"]
        ),
        "finite_wilson_loop_campaign": (
            diagnostics["m10_wilson_passed"]
            and diagnostics["wilson_area_coefficient"] > 0.0
            and diagnostics["wilson_creutz_11"] > 0.0
            and diagnostics["wilson_gauge_error"] < 2.0e-12
            and diagnostics["wilson_polyakov_max_norm"] <= 1.0 + 1.0e-12
        ),
        "abjm_wilson_algebra": (
            diagnostics["kernel_positive"]
            and diagnostics["kernel_factorization_error"] < 5.0e-14
            and diagnostics["convergence_condition"]
            and diagnostics["partition_reconstruction_error"] < 5.0e-14
            and diagnostics["opposite_level_sum"] == 0
        ),
        "scale_and_model_dependencies": (
            diagnostics["m13_1_passed"]
            and diagnostics["scale_radial_metric_available"]
        ),
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": MILESTONE,
        "diagnostics": diagnostics,
        "acceptance": acceptance,
        "fingerprint": fingerprint(payload),
        "passed": all(acceptance.values()),
        "decision": {
            "finite_ads_cft_dictionary_is_executable": True,
            "twistor_projective_and_incidence_checks_are_executable": True,
            "finite_bcj_and_primitive_qcd_relations_are_executable": True,
            "m10_supplies_wilson_loop_data": True,
            "abjm_wilson_algebra_is_checked": True,
            "interacting_witten_diagram_is_not_evaluated": True,
            "bcfw_qcd_derivation_is_not_claimed": True,
            "full_su22_twistor_action_is_not_claimed": True,
            "continuum_gauge_string_duality_is_not_claimed": True,
        },
    }
