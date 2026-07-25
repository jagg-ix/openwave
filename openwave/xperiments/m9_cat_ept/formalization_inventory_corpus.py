"""Merged formalization-family ZIL graphs on the CAT/EPT PhysLib branch."""
from __future__ import annotations


def _names(value: str) -> tuple[str, ...]:
    return tuple(value.split())


CORPUS_ZIL_GRAPHS = (
    {
        "id": "rivers-scalar-green-functions",
        "module": "physlib.qft.scalar_green_functions.rivers1987",
        "source_path": "formalization/zil/rivers-scalar-green-functions.zc",
        "source_blob": "b5f566ba2e261e5eb8c3371b043a9136ea6c7a54",
        "entities": {
            "component": _names("""
                measure_path_integral_model measure_expectation source_coupled_partition
                dominated_convergence wick_contractions wick_theorem complex_action_weight
                entropic_complex_weight entropic_proper_time local_admissible_variation
                schwinger_dyson_kernel finite_determinant
            """),
            "source": _names("""
                rivers1987_eq1_11_eq1_13 rivers1987_eq1_14_eq1_20
                rivers1987_eq1_28_eq1_36 rivers1987_eq1_38_eq1_50
                rivers1987_eq1_51_eq1_59 rivers1987_eq1_60_eq1_79
                rivers1987_eq1_80_eq1_88 rivers1987_eq1_89_eq1_93
                rivers1987_eq1_94_eq1_100
            """),
            "claim": _names("""
                finite_functional_derivative quartic_potential_derivative
                scalar_green_generating_functional bose_symmetric_green_functions
                source_jet_extraction quartic_dyson_schwinger_hierarchy
                dyson_schwinger_contact_terms even_odd_sector_decoupling
                unique_formal_perturbative_recursion zero_dimensional_ds_recurrence
                free_real_gaussian_functional free_odd_moments_vanish
                external_field_dyson_resolvent external_field_resolvent_difference
                finite_neumann_remainder vacuum_factor_cancels
                complex_scalar_source_functional complex_scalar_loop_doubling
                shifted_gaussian_vacuum vacuum_center_unique vacuum_entropic_selection
                global_imaginary_action_cancels global_entropic_gap_damps_but_cancels
                entropic_weighted_dyson_wick continuum_coincident_field_products
                interacting_continuum_measure
            """),
            "proof": _names("""
                Physlib.QFT.ScalarGreenFunctions.finiteFunctionalDerivative_evaluation
                Physlib.QFT.ScalarGreenFunctions.quarticPotential_hasDerivAt
                Physlib.QFT.ScalarGreenFunctions.scalarGreenFunction_pair_comm
                Physlib.QFT.ScalarGreenFunctions.recoverGreenFromSourceJet
                Physlib.QFT.ScalarGreenFunctions.QuarticDysonSchwingerData.hierarchy
                Physlib.QFT.ScalarGreenFunctions.contactTerm_pair
                Physlib.QFT.ScalarGreenFunctions.QuarticDysonSchwingerData.hierarchyOrders_sameParity
                Physlib.QFT.ScalarGreenFunctions.exists_unique_perturbativeCoefficient
                Physlib.QFT.ScalarGreenFunctions.ZeroDimensionalQuarticDS.recurrence_one
                Physlib.QFT.ScalarGreenFunctions.freeRealGeneratingFunctional_neg_source
                Physlib.QFT.ScalarGreenFunctions.ExternalFieldResolventData.dysonEquation
                Physlib.QFT.ScalarGreenFunctions.ExternalFieldResolventFamily.resolventDifference
                Physlib.QFT.ScalarGreenFunctions.one_sub_mul_neumannPartial
                Physlib.QFT.ScalarGreenFunctions.externalNormalizedGenerating_eq_exp
                Physlib.QFT.ScalarGreenFunctions.complexScalarLoopAction_eq_two_real
                Physlib.QFT.ScalarGreenFunctions.gaussianVacuumAction_completeSquare
                Physlib.QFT.ScalarGreenFunctions.vacuumRelativeAction_eq_zero_iff
                Physlib.QFT.ScalarGreenFunctions.norm_vacuumComplexWeight_eq_one_iff
                Physlib.QFT.ScalarGreenFunctions.shiftImaginaryAction_normalizedExpectation
                Physlib.QFT.ScalarGreenFunctions.globalEntropicOffset_damps_but_cancels
                Physlib.QFT.ScalarGreenFunctions.complexActionWeightedDysonWick
            """),
        },
        "rules": _names("verified_claim pending_claim boundary_claim"),
        "queries": _names("""
            claim_statuses proof_registry dependency_edges reused_components
            source_traceability open_boundaries
        """),
        "open_targets": _names(
            "continuum_coincident_field_products interacting_continuum_measure"
        ),
        "witness_prefixes": ("Physlib.QFT.ScalarGreenFunctions",),
    },
    {
        "id": "rivers-scalar-green-functions-continuum",
        "module": "physlib.qft.scalar_green_functions.rivers1987.continuum",
        "source_path": "formalization/zil/rivers-scalar-green-functions-continuum.zc",
        "source_blob": "2f97d66b3ed282c8aa59e0316adb1a767ea2b4d4",
        "entities": {
            "component": _names("""
                l2_scalar_hilbert_space l2_product_kernel_space
                maximal_pointwise_operator pointwise_kernel_actions dirac_distribution
                schwartz_test_space complete_wick_theorem matrix_determinant
                complex_exponential_sum complex_logarithm bochner_integral
                complex_action_weight
            """),
            "source": _names("""
                rivers1987_eq1_32_eq1_36 rivers1987_eq1_51_eq1_59
                rivers1987_eq1_53_eq1_58 rivers1987_eq1_69_eq1_78
                rivers1987_eq1_94_eq1_100
            """),
            "claim": _names("""
                continuum_scalar_l2_carrier continuum_two_point_l2_kernel
                continuum_pointwise_source_operator continuum_pointwise_source_dense_domain
                left_right_continuum_multipliers_commute continuum_dirac_contact
                continuum_contact_removal_pair continuum_distributional_ds_hierarchy
                continuum_two_leg_ds_equation continuum_external_field_dyson
                continuum_resolvent_difference_quotient quartic_source_interaction_operator
                dyson_wick_finite_exponential dyson_wick_normalization
                dyson_wick_termwise_contractions finite_propagator_ds_hierarchy
                continuum_propagator_ds_hierarchy diagonal_trace_log_determinant
                determinant_ratio_trace_log loop_action_spectral_derivative
                continuum_gaussian_vacuum continuum_vacuum_entropic_contraction
                continuum_vacuum_kernel_operator
            """),
            "proof": _names("""
                Physlib.QFT.ScalarGreenFunctions.continuumScalarMulOperator_apply_ae
                Physlib.QFT.ScalarGreenFunctions.continuumScalarMulOperator_hasDenseDomain
                Physlib.QFT.ScalarGreenFunctions.left_right_continuumScalarKernelAction_commute
                Physlib.QFT.ScalarGreenFunctions.scalarContactDistribution_apply
                Physlib.QFT.ScalarGreenFunctions.continuumContactTerm_pair_apply
                Physlib.QFT.ScalarGreenFunctions.ContinuumQuarticDysonSchwingerData.equation_apply
                Physlib.QFT.ScalarGreenFunctions.ContinuumQuarticDysonSchwingerData.twoLegEquation_apply
                Physlib.QFT.ScalarGreenFunctions.ContinuumExternalFieldDysonData.dysonEquation
                Physlib.QFT.ScalarGreenFunctions.ContinuumResolventFlowData.differenceQuotient
                Physlib.QFT.ScalarGreenFunctions.dysonWickTruncation_succ
                Physlib.QFT.ScalarGreenFunctions.normalizedQuarticDysonWickTruncation_empty
                Physlib.QFT.ScalarGreenFunctions.dysonOrder_smul_wicks_theorem
                Physlib.QFT.ScalarGreenFunctions.PropagatorDysonSchwingerData.twoLegEquation
                Physlib.QFT.ScalarGreenFunctions.ContinuumPropagatorDysonSchwingerData.threeLegEquation
                Physlib.QFT.ScalarGreenFunctions.exp_diagonalTraceLog_eq_det
                Physlib.QFT.ScalarGreenFunctions.diagonalDeterminantRatio_eq_exp_traceLog_sub
                Physlib.QFT.ScalarGreenFunctions.realDiagonalLoopAction_hasDerivAt
                Physlib.QFT.ScalarGreenFunctions.continuumGaussianVacuumDensity_completeSquare
                Physlib.QFT.ScalarGreenFunctions.norm_continuumVacuumComplexWeight_le_one
                Physlib.QFT.ScalarGreenFunctions.continuumVacuumKernelOperator_apply_ae
            """),
        },
        "rules": _names("verified_claim pending_claim"),
        "queries": _names("""
            claim_statuses proof_registry dependency_edges reused_components
            source_traceability
        """),
        "open_targets": (),
        "witness_prefixes": ("Physlib.QFT.ScalarGreenFunctions",),
    },
    {
        "id": "lovelock-rund-continuum-variational",
        "module": "physlib.mathematics.lovelock_rund.continuum_variational",
        "source_path": "formalization/zil/lovelock-rund-continuum-variational.zc",
        "source_blob": "109d8cfab6850325463f19d6c6bc5c49e70bf6eb",
        "entities": {
            "component": _names("""
                mathlib_continuous_alternating_map mathlib_exterior_derivative
                mathlib_d_squared_zero mathlib_pullback_naturality
                mathlib_vector_field_formula physlib_admissible_variation
                physlib_fundamental_variational_lemma physlib_variational_gradient
                physlib_divergence physlib_riemannian_metric physlib_second_bianchi
                physlib_complex_action_weight mathlib_tsum physlib_pi_tensor_product
            """),
            "source": _names("""
                lovelock_rund_ch2_ch4_tensor_calculus lovelock_rund_ch5_differential_forms
                lovelock_rund_ch6_variational_principles lovelock_rund_ch7_riemannian_geometry
                lovelock_rund_ch8_field_variational_theories
            """),
            "claim": _names("""
                infinite_tensor_contraction infinite_covariant_derivative
                differential_form_infinite_model d_squared_zero exact_implies_closed
                pullback_commutes_with_d vector_field_exterior_derivative
                weak_extremal_pointwise_zero variational_gradient_weak_equation
                noether_on_shell_conservation higher_order_euler_lagrange
                infinite_geodesic_residual riemannian_energy_positive curvature_form_bianchi
                second_bianchi_conservation complex_variational_stationarity
                entropic_time_gradient
            """),
        },
        "rules": (),
        "queries": _names("proof_registry reused_components source_traceability dependency_edges"),
        "open_targets": (),
        "witness_prefixes": ("Physlib.Mathematics.LovelockRund",),
    },
    {
        "id": "lovelock-rund-pointwise-operators",
        "module": "physlib.mathematics.lovelock_rund.pointwise_operators",
        "source_path": "formalization/zil/lovelock-rund-pointwise-operators.zc",
        "source_blob": "ab6a36c58bfad58661d69ab6836e7b45f9a3bb20",
        "entities": {
            "component": _names("""
                mathlib_l2 mathlib_memlp physlib_space_hilbert physlib_mul_operator
            """),
            "source": _names("lovelock_rund_ch6_continuum_variation lovelock_rund_ch8_field_theories"),
            "claim": _names("""
                vector_valued_continuum_field maximal_pointwise_field_operator
                pointwise_operator_dense_domain pointwise_operator_ae_action
                pointwise_euler_lagrange_operator
            """),
        },
        "rules": (),
        "queries": _names("reused_components proof_registry source_traceability"),
        "open_targets": (),
        "witness_prefixes": ("Physlib.Mathematics.LovelockRund",),
    },
    {
        "id": "lovelock-rund-invariant-geometry",
        "module": "physlib.mathematics.lovelock_rund.invariant_geometry",
        "source_path": "formalization/zil/lovelock-rund-invariant-geometry.zc",
        "source_blob": "c7a9288f68e93914ac0176f0f43da85f12e3d89b",
        "entities": {
            "component": _names("""
                mathlib_lie_bracket mathlib_alternating_curry mathlib_poincare_one_form
                mathlib_curve_integral mathlib_divergence_theorem
                mathlib_fundamental_calculus mathlib_tsum physlib_hamilton_equations
                physlib_complex_action_weight physlib_divergence physlib_second_bianchi
            """),
            "source": _names("""
                lovelock_rund_section_4_3_normal_coordinates
                lovelock_rund_section_4_4_lie_derivative
                lovelock_rund_section_5_3_poincare lovelock_rund_section_5_5_stokes
                lovelock_rund_section_6_2_hamilton_jacobi
                lovelock_rund_section_6_6_multi_noether
                lovelock_rund_section_7_3_curvature
                lovelock_rund_section_7_4_subspaces
                lovelock_rund_section_7_5_hypersurfaces
                lovelock_rund_section_7_6_divergence
            """),
            "claim": _names("""
                cartan_lie_derivative closed_form_lie_derivative_exact
                poincare_closed_one_form_exact closed_one_form_segment_path_independence
                interval_stokes box_divergence_theorem multi_parameter_noether
                infinite_dimensional_hamilton_jacobi complex_hamilton_jacobi_stationarity
                hamilton_jacobi_entropic_rate normal_coordinate_connection_reduction
                infinite_ricci_contraction infinite_scalar_curvature
                einstein_tensor_components gauss_equation codazzi_equation
            """),
        },
        "rules": (),
        "queries": _names("proof_registry reused_components source_traceability dependency_edges"),
        "open_targets": (),
        "witness_prefixes": ("Physlib.Mathematics.LovelockRund",),
    },
    {
        "id": "veliev-periodic-schrodinger",
        "module": "physlib.quantum.periodic_schrodinger.veliev",
        "source_path": "formalization/zil/veliev-periodic-schrodinger.zc",
        "source_blob": "a43cf9fc526ccd427d3dcd32a855725c54ca65b9",
        "entities": {
            "source": ("veliev_periodic_schrodinger",),
            "component": _names("""
                physlib_space_hilbert physlib_mul_operator mathlib_matrix
                mathlib_hermitian mathlib_tsum mathlib_intermediate_value
                physlib_complex_action_weight
            """),
            "claim": _names("""
                free_bloch_energy diffraction_hyperplane resonance_nonresonance_disjoint
                fourier_binding_formula finite_binding_iteration finite_resonance_matrix
                resonance_matrix_hermitian simple_label_uniqueness two_family_simplicity
                directional_potential_split directional_binding_formula
                finite_bloch_localization infinite_bloch_localization
                periodic_potential_preserves_bloch continuum_periodic_potential_operator
                arbitrary_order_known_parts arbitrary_order_error_estimates
                isoenergetic_crossing high_energy_spectral_tail
                bethe_sommerfeld_high_energy_conclusion entropic_spectral_selection
                diffraction_entropic_selection
            """),
        },
        "rules": (),
        "queries": _names("proof_registry reused_components source_traceability external_requirements"),
        "open_targets": ("arbitrary_order_error_estimates",),
        "witness_prefixes": ("Physlib.QuantumMechanics.PeriodicSchrodinger",),
    },
)

LATEST_FORMAL_TREE = "239a663a3192a3144fb998e7bb200e09689a3bb9"
LATEST_MODULE_INDEX_BLOB = "182a06e0f50314ec54436da602b4ac86eba4ee08"

CORPUS_LEAN_SOURCES = (
    (
        "scalar-green-functions",
        "Physlib/QFT/ScalarGreenFunctions.lean",
        "1e9e06027545af89507deb84f969f5a73870a5cf",
        ("Physlib.QFT.ScalarGreenFunctions",),
        "mixed_kernel_and_pending_statuses",
    ),
    (
        "lovelock-rund",
        "Physlib/Mathematics/LovelockRund.lean",
        "a6a6d3ebd9c39be9ea02267b90c6b86947a393c2",
        ("Physlib.Mathematics.LovelockRund",),
        "kernel_source_registry",
    ),
    (
        "periodic-schrodinger",
        "Physlib/QuantumMechanics/PeriodicSchrodinger.lean",
        "54228fbacd689ccb2769fa01e92806052b7d0bf2",
        ("Physlib.QuantumMechanics.PeriodicSchrodinger",),
        "kernel_source_with_external_analytic_boundary",
    ),
    (
        "eddington-affine-first-integral",
        "Physlib/QuantumMechanics/ComplexAction/EddingtonAffineFirstIntegral.lean",
        "5bd4704dbe22f2be35d871996a953d2ee009e4ef",
        ("Physlib.QuantumMechanics.ComplexAction.EddingtonAffineFirstIntegral",),
        "kernel_checked_scoped",
    ),
)

CORPUS_CRITERION_IMPORTS = (
    {
        "criterion": "gravity",
        "task": "M9.94a",
        "declarations": _names("""
            Physlib.QuantumMechanics.ComplexAction.EddingtonAffineFirstIntegral.connectionResidual_contract
            Physlib.QuantumMechanics.ComplexAction.EddingtonAffineFirstIntegral.connectionResidual_iff_density_parallel
            Physlib.QuantumMechanics.ComplexAction.EddingtonAffineFirstIntegral.firstIntegral_ricci_eq
            Physlib.QuantumMechanics.ComplexAction.EddingtonAffineFirstIntegral.firstIntegral_scalarCurvature
            Physlib.QuantumMechanics.ComplexAction.EddingtonAffineFirstIntegral.firstIntegral_derives_einsteinLambda
            Physlib.QuantumMechanics.ComplexAction.EddingtonAffineFirstIntegral.nonsingular_firstIntegral_lambda_ne_zero
            Physlib.QuantumMechanics.ComplexAction.EddingtonAffineFirstIntegral.nonsingular_firstIntegral_eddingtonLambda_ne_zero
            Physlib.QuantumMechanics.ComplexAction.EddingtonAffineFirstIntegral.torsionVacuumEom_forces_contorsion_zero
            Physlib.QuantumMechanics.ComplexAction.EddingtonAffineFirstIntegral.lovelockFirstIntegral_derives_fieldEquation
        """),
        "numerical_adapters": (
            "openwave.xperiments.m9_cat_ept.formal_action_generator_bridge:run_action_generator_study",
            "openwave.xperiments.m9_cat_ept.geometry_backreaction:run_geometry_backreaction_study",
        ),
        "boundary": (
            "the affine first integral is algebraic over a finite index type and assumes the variational field equation",
            "no calibrated global nonlinear CAT/EPT gravity evolution is inherited",
        ),
    },
)
