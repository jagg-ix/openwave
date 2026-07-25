"""Frozen CAT/EPT Lean and ZIL inventory imported from entropic PhysLib.

The inventory records every entity identifier in the three ZIL graphs already
referenced by OpenWave, plus the Lean source modules used by the current M9
criterion bridges. Lean remains proof authority; ZIL remains an orchestration
and status graph.
"""
from __future__ import annotations


def _names(value: str) -> tuple[str, ...]:
    return tuple(value.split())


FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_COMMIT = "e10af9a3b47bf90afc0a88167a5d495b6935f4dc"
MODULE_INDEX_PATH = "Physlib.lean"
MODULE_INDEX_BLOB = "7f5115e083cbe33491b25003cb963c5be7fee9be"

ZIL_GRAPHS = (
    {
        "id": "electrogravitic-action-closure",
        "module": "physlib.electrogravitic.action_closure",
        "source_path": "formalization/zil/electrogravitic-action-closure.zc",
        "source_blob": "cf9110d8b4229c33a1e2cefa34c0719062a3f340",
        "entities": {
            "component": _names("""
                variational_gradient_api frechet_derivative_api
                electromagnetic_lagrangian electromagnetic_variational_gradient
                distributional_maxwell_variation complex_regge_action
                complex_regge_action_derivative coupled_first_variation
                coupled_action_germ coupled_action_germ_derivative
                nonlinear_action_certificate action_stationarity_bridge
                global_lorentzian_measure global_einstein_hilbert_action
                global_action_derivative global_action_stationarity
                metric_built_connection metric_built_riemann metric_built_ricci
                metric_built_scalar metric_built_einstein
                metric_built_action_constructor einstein_hilbert_density_derivative
                palatini_curvature_derivative palatini_einstein_hilbert_derivative
                ghy_boundary_cancellation global_intrinsic_maxwell_equation
                global_intrinsic_maxwell_operator global_maxwell_atlas_independence
                maxwell_well_posed_cauchy_interface maxwell_green_interface
                maxwell_retarded_global_solution maxwell_advanced_global_solution
                nonlinear_einstein_cauchy_interface
                local_nonlinear_einstein_existence
                local_nonlinear_einstein_uniqueness bcj_explicit_channels
                bcj_path_weight_bridge
            """),
            "claim": _names("""
                electromagnetic_action_and_derivative
                complex_regge_action_and_derivative
                coupled_linearized_action_derivative
                arbitrary_certified_action_to_field_equations
                global_einstein_hilbert_action_and_derivative
                metric_to_curvature_capstone_closure
                global_intrinsic_maxwell_pde sourced_distributional_maxwell_pde
                global_maxwell_green_solutions
                local_nonlinear_complex_einstein_evolution
                local_nonlinear_complex_einstein_uniqueness
                concrete_maxwell_cauchy_from_global_hyperbolicity
                concrete_adm_constraint_propagation
                maximal_globally_hyperbolic_coupled_development
                explicit_model_bcj_amplitude_closure
                concrete_global_nonlinear_coupled_action_certificate
            """),
            "inspection": _names(
                "global_curved_spacetime_pde_closure global_action_integration"
            ),
            "policy": ("closure_status_vocabulary",),
        },
        "rules": (),
        "queries": _names("""
            proved_interfaces scoped_proved_interfaces
            conditional_analytic_interfaces open_end_to_end_interfaces
            not_located_interfaces dependency_edges
        """),
        "open_targets": _names("""
            concrete_maxwell_cauchy_from_global_hyperbolicity
            concrete_adm_constraint_propagation
            maximal_globally_hyperbolic_coupled_development
            concrete_global_nonlinear_coupled_action_certificate
        """),
        "witness_prefixes": _names("""
            HasVarGradientAt HasFDerivAt Electromagnetism.
            PseudoRiemannianMetric.
            Physlib.QuantumMechanics.ComplexAction.LeviCivita.ComplexReggeAction
            Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.ElectroGravitationalFieldEquations
            Physlib.QuantumMechanics.ComplexAction.Curvature.GlobalEinsteinHilbertAction
            Physlib.QuantumMechanics.ComplexAction.Curvature.DiffeomorphismMetricVariation
            Physlib.QuantumMechanics.ComplexAction.ComptonClock.ReversibleLimitConvergence
            Physlib.Meta.EntropicDynamicsFullEinsteinSource
        """),
    },
    {
        "id": "lindblad-driven-leads",
        "module": "physlib.quantum.open_systems.lindblad_driven_leads",
        "source_path": "formalization/zil/lindblad-driven-leads.zc",
        "source_blob": "8f98a97bb12f0b5ab21fbcc62f878e0650894353",
        "entities": {
            "component": _names("""
                hilbert_schmidt_operator_space hilbert_schmidt_left_right_mul
                banach_algebra_exponential pointwise_mul_operator
                pointwise_closability dominated_convergence cauchy_distribution
                cauchy_normalization
            """),
            "source": _names("""
                schwarz2016_eq34 schwarz2016_eq36 schwarz2016_eq37
                schwarz2016_eq38 schwarz2016_eq39 schwarz2016_eq40
                schwarz2016_eq42 schwarz2016_eq45 schwarz2016_eq55_eq56
                schwarz2016_eq58_eq60 schwarz2016_eq65 schwarz2016_eq68
                schwarz2016_eq70
            """),
            "claim": _names("""
                loss_gain_rates occupation_relaxation unique_target_occupation
                finite_hs_lddl_generator bounded_lddl_evolution
                one_level_green_broadening lorentzian_unit_spectral_weight
                continuum_resolution_criterion
                continuum_observable_dominated_convergence
                transport_integral_convergence_from_hybridization
                level_doubling_amplitudes level_doubling_hybridization
                local_rate_unitary_invariance continuum_pointwise_closable
                lorentz_sum_converges_to_continuum_hybridization
                lddl_current_converges_to_continuum_current
            """),
            "proof": _names("""
                QuantumMechanics.LindbladDrivenLeads.totalRate_eq_gamma
                QuantumMechanics.LindbladDrivenLeads.imbalanceRate_eq
                QuantumMechanics.LindbladDrivenLeads.occupationVectorField_eq
                QuantumMechanics.LindbladDrivenLeads.occupationVectorField_eq_zero_iff
                QuantumMechanics.LindbladDrivenLeads.gainRate_div_totalRate
                QuantumMechanics.LindbladDrivenLeads.lindbladDissipatorHS_apply
                QuantumMechanics.LindbladDrivenLeads.lddlEvolutionHS_zero
                QuantumMechanics.LindbladDrivenLeads.keldyshLeadGreen_eq
                QuantumMechanics.LindbladDrivenLeads.lorentzian_nonneg
                QuantumMechanics.LindbladDrivenLeads.integral_lorentzian_eq_one
                QuantumMechanics.LindbladDrivenLeads.matchedBroadening_resolved
                QuantumMechanics.LindbladDrivenLeads.continuumObservable_tendsto_of_dominated_convergence
                QuantumMechanics.LindbladDrivenLeads.transportObservable_tendsto_of_hybridization
                QuantumMechanics.LindbladDrivenLeads.couplingWeight_sq
                QuantumMechanics.LindbladDrivenLeads.sum_doubledCoupling_normSq
                QuantumMechanics.LindbladDrivenLeads.sum_localRateMinus_mul_doubledNormSq
                QuantumMechanics.LindbladDrivenLeads.scalarRateMatrix_unitaryInvariant
                QuantumMechanics.LindbladDrivenLeads.doubledSpacePointwiseOperator_isClosable
            """),
        },
        "rules": _names("verified_claim pending_claim open_claim"),
        "queries": _names("""
            claim_statuses proof_registry dependency_edges reused_components
            source_traceability open_targets
        """),
        "open_targets": _names("""
            lorentz_sum_converges_to_continuum_hybridization
            lddl_current_converges_to_continuum_current
        """),
        "witness_prefixes": ("QuantumMechanics.LindbladDrivenLeads",),
    },
    {
        "id": "liouville-second-quantization",
        "module": "physlib.quantum.open_systems.liouville_second_quantization",
        "source_path": "formalization/zil/liouville-second-quantization.zc",
        "source_blob": "8141e353dc5960ef28c01883ccbb10411f62ac05",
        "entities": {
            "component": _names("""
                lean4_mathlib mathlib_matrix_single mathlib_l2_space
                mathlib_memlp physlib_space_d_hilbert_space
                physlib_pointwise_mul_operator physlib_dirac_distribution
            """),
            "source": _names("""
                arxiv_2207_14234_eq4_eq5 arxiv_2207_14234_eq8
                arxiv_2207_14234_eq9 arxiv_2207_14234_eq10
                arxiv_2207_14234_eq13 arxiv_2207_14234_phase_space_outlook
            """),
            "assumption": _names("""
                decidable_discrete_index_equality infinite_level_index
                finite_particle_number_per_sector lindblad_generator_closable
                continuum_semigroup_wellposed
            """),
            "claim": _names("""
                discrete_arbitrary_index_left_action
                discrete_arbitrary_index_right_action
                discrete_arbitrary_index_reservoir_sandwich infinite_mode_set
                fixed_particle_sector_arbitrary_modes continuum_l2_kernel_carrier
                continuum_kernel_constructor regular_pointwise_kernel_actions
                doubled_space_pointwise_operator continuum_dirac_matrix_unit
                genuinely_infinite_particle_representation
                continuum_lindblad_generator phase_space_fokker_planck_bridge
            """),
            "proof": _names("""
                QuantumMechanics.LiouvilleSecondQuantization.leftKernelAction_matrixUnit_same
                QuantumMechanics.LiouvilleSecondQuantization.rightKernelAction_matrixUnit_same
                QuantumMechanics.LiouvilleSecondQuantization.independentReservoirKernel_eq_single
                QuantumMechanics.LiouvilleSecondQuantization.kernelMode_infinite
                QuantumMechanics.LiouvilleSecondQuantization.kernelOccupationBasis_particleNumber
                QuantumMechanics.LiouvilleSecondQuantization.coe_mkContinuumKernel_ae
                QuantumMechanics.LiouvilleSecondQuantization.leftPointwise_rightPointwise_commute
                QuantumMechanics.LiouvilleSecondQuantization.spacePointwiseKernelOperator_hasDenseDomain
                QuantumMechanics.LiouvilleSecondQuantization.continuumMatrixUnit_apply
            """),
        },
        "rules": _names("""
            implementation_declared verified_from_kernel_witness awaiting_ci
            weak_open_target
        """),
        "queries": _names("""
            claim_statuses implementation_registry dependency_edges
            reused_components source_traceability open_targets
        """),
        "open_targets": _names("""
            genuinely_infinite_particle_representation continuum_lindblad_generator
            phase_space_fokker_planck_bridge
        """),
        "witness_prefixes": ("QuantumMechanics.LiouvilleSecondQuantization",),
    },
)

LEAN_SOURCES = (
    ("physlib-module-index", "Physlib.lean", MODULE_INDEX_BLOB,
     ("Physlib.QuantumMechanics.ComplexAction", "Physlib.QuantumMechanics.OpenSystems"),
     "kernel_index"),
    ("electrogravitic-field-equations",
     "Physlib/QuantumMechanics/ComplexAction/ComplexEinstein/ElectroGravitationalFieldEquations.lean",
     "7ecfc0ce288e84d575af60718b74fb1148bf0c5f",
     ("Physlib.QuantumMechanics.ComplexAction.ComplexEinstein.ElectroGravitationalFieldEquations",),
     "kernel_checked"),
    ("global-einstein-hilbert-action",
     "Physlib/QuantumMechanics/ComplexAction/Curvature/GlobalEinsteinHilbertAction.lean",
     "6862565fb915b5c6f1cc561b769e190b70f3156a",
     ("Physlib.QuantumMechanics.ComplexAction.Curvature.GlobalEinsteinHilbertAction",),
     "kernel_checked_scoped"),
    ("diffeomorphism-metric-variation",
     "Physlib/QuantumMechanics/ComplexAction/Curvature/DiffeomorphismMetricVariation.lean",
     "a589fc1188645bdb126e522862a861e38392cfea",
     ("Physlib.QuantumMechanics.ComplexAction.Curvature.DiffeomorphismMetricVariation",),
     "kernel_checked_scoped"),
    ("complex-regge-action",
     "Physlib/QuantumMechanics/ComplexAction/LeviCivita/ComplexReggeAction.lean",
     "485e778a7de16b0f30fa37bf03ad906987d40b4a",
     ("Physlib.QuantumMechanics.ComplexAction.LeviCivita.ComplexReggeAction",),
     "kernel_checked"),
    ("reversible-limit-convergence",
     "Physlib/QuantumMechanics/ComplexAction/ComptonClock/ReversibleLimitConvergence.lean",
     "81fdd6183edb5fcd40c91d9e4fe49bcd5b3672af",
     ("Physlib.QuantumMechanics.ComplexAction.ComptonClock.ReversibleLimitConvergence",),
     "conditional_analytic_interfaces"),
    ("entropic-dynamics-capstone", "Physlib/Meta/EntropicDynamicsFullEinsteinSource.lean",
     "f1dc5fb21b42b5be676485a672c6923615b6380e",
     ("Physlib.Meta.EntropicDynamicsFullEinsteinSource",), "kernel_checked_scoped"),
    ("liouville-second-quantization",
     "Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean",
     "9d2c905c940480f1ed570cf0be965d5a9b6c4831",
     ("QuantumMechanics.LiouvilleSecondQuantization",), "implementation_declared"),
    ("lindblad-driven-leads",
     "Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/Basic.lean",
     "634087560adaffaaa5a683c47f3dee123501fb28",
     ("QuantumMechanics.LindbladDrivenLeads",), "implementation_declared"),
    ("pointwise-multiplication-operator",
     "Physlib/QuantumMechanics/DDimensions/Operators/Multiplication.lean",
     "9e43c4a6b6eee5f22efdaa9ef4ce3c2b84cef7b5",
     ("QuantumMechanics.SpaceDHilbertSpace",), "provided_interface"),
    ("pauli-spin-orbit",
     "Physlib/QuantumMechanics/ComplexAction/Dirac/PauliEquationSpinOrbit.lean",
     "9752e6c317b1e3bd714c2e36bc4dd5152a6289df",
     ("Physlib.QuantumMechanics.ComplexAction.Dirac.PauliEquationSpinOrbit",),
     "kernel_checked"),
    ("anomalous-magnetic-moment",
     "Physlib/QuantumMechanics/ComplexAction/FirstQuantizedQED/AnomalousMagneticMoment.lean",
     "e89ec4075f41b502e9997d365e2dd50af35c70c5",
     ("Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMagneticMoment",),
     "kernel_checked_structural"),
    ("em-lorentz-superoperator",
     "Physlib/QuantumMechanics/ComplexAction/Electromagnetic/EMLorentzCombinedSuperoperator.lean",
     "d20871ca6d8c40e0d61e647f14dfdbc70bfe5925",
     ("Physlib.QuantumMechanics.ComplexAction.Electromagnetic.EMLorentzCombinedSuperoperator",),
     "kernel_checked"),
    ("screened-potential",
     "Physlib/QuantumMechanics/ComplexAction/Yukawa/ScreenedPotential.lean",
     "d9c78c21515020dd6ddd9c8877cf21c5665c0dde",
     ("Physlib.QuantumMechanics.ComplexAction.Yukawa.ScreenedPotential",),
     "kernel_checked"),
    ("coulomb-gegenbauer",
     "Physlib/QuantumMechanics/ComplexAction/Yukawa/CoulombGegenbauer.lean",
     "9875d3a77f5573e82ed2b521686360a9e1e1a2a5",
     ("Physlib.QuantumMechanics.ComplexAction.Yukawa.CoulombGegenbauer",),
     "kernel_checked"),
    ("elementary-quantization",
     "Physlib/QuantumMechanics/ComplexAction/ElementaryQuantization.lean",
     "b68b5c1588e6f299e826cf41117e1bc97cb5bedf",
     ("Physlib.QuantumMechanics.ComplexAction.ElementaryQuantization",),
     "kernel_checked"),
    ("euclidean-free-schrodinger",
     "Physlib/QuantumMechanics/Schrodinger/EuclideanL2FreeEvolution.lean",
     "161641f1261421b55014d078744c2c89a932668b",
     ("Physlib.QuantumMechanics.Schrodinger.EuclideanL2FreeEvolution",),
     "kernel_checked"),
    ("cat-ept-cubic-flow",
     "Physlib/QuantumMechanics/ComplexAction/EntropicTime/IpekCatichaSuperpositionViolation.lean",
     "ff050e86cb9812bcb0ecb612e498d7dc05e8c639",
     ("Physlib.QuantumMechanics.ComplexAction.EntropicTime.IpekCatichaSuperpositionViolation",),
     "kernel_checked_scoped"),
    ("winding-charge",
     "Physlib/QuantumMechanics/ComplexAction/Winding/QuarkChargeWinding.lean",
     "a8317538d445453a0e9345c499c11ad3742f7980",
     ("Physlib.QuantumMechanics.ComplexAction.Winding.QuarkChargeWinding",),
     "kernel_checked"),
    ("zero-point-length",
     "Physlib/QuantumMechanics/ComplexAction/ComptonClock/ZeroPointLength.lean",
     "7232eefe2d0b85ddf6df0d7ed206f7acfb2d005d",
     ("Physlib.QuantumMechanics.ComplexAction.ComptonClock.ZeroPointLength",),
     "optional"),
)

EXTERNAL_WITNESS_PREFIXES = (
    "HasVarGradientAt", "HasFDerivAt", "Electromagnetism.",
    "PseudoRiemannianMetric.", "HilbertSchmidtOperatorSpace.",
    "NormedSpace.", "MeasureTheory.", "ProbabilityTheory.",
    "QuantumMechanics.SpaceDHilbertSpace.", "Physlib.Distribution.", "Mathlib."
)

CRITERION_IMPORTS = (
    {
        "criterion": "magnetic_moment_spin",
        "task": "M9.94",
        "declarations": _names("""
            Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMagneticMoment.spinTensor_12_involution
            Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMagneticMoment.spinMoment_comm_diracBeta
            Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMagneticMoment.gFactor_dirac
            Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMagneticMoment.gFactor_schwinger
            Physlib.QuantumMechanics.ComplexAction.FirstQuantizedQED.AnomalousMagneticMoment.gFactor_eq_two_mul_ratio
            Physlib.QuantumMechanics.ComplexAction.Dirac.PauliEquationSpinOrbit.pauli_vector_identity
            Physlib.QuantumMechanics.ComplexAction.Dirac.PauliEquationSpinOrbit.heisenberg_spin_precession
            Physlib.QuantumMechanics.ComplexAction.Dirac.PauliEquationSpinOrbit.pauliHamiltonianFW_isSelfAdjoint
        """),
        "numerical_adapters": (
            "openwave.xperiments.m9_cat_ept.spin_magnetic_observables:run_spin_magnetic_study",
        ),
        "boundary": (
            "Schwinger anomaly is a structural formal value, not derived from the localized branch",
            "physical g-factor calibration and electron identity remain separate",
        ),
    },
    {
        "criterion": "electric_force",
        "task": "M9.95",
        "declarations": _names("""
            Physlib.QuantumMechanics.ComplexAction.Yukawa.ScreenedPotential.yukawaPotential_le_coulomb
            Physlib.QuantumMechanics.ComplexAction.Yukawa.CoulombGegenbauer.yukawaPotential_zero_eq_coulomb
            Physlib.QuantumMechanics.ComplexAction.Yukawa.CoulombGegenbauer.entropicMass_coulomb
        """),
        "numerical_adapters": (
            "openwave.xperiments.m9_cat_ept.two_body_forces:run_two_body_force_study",
        ),
        "boundary": (
            "formal source supplies the potential and unscreened limit; OpenWave differentiates the regularized kernel",
            "charge and force units remain uncalibrated",
        ),
    },
    {
        "criterion": "magnetic_force",
        "task": "M9.95",
        "declarations": _names("""
            Physlib.QuantumMechanics.ComplexAction.Electromagnetic.EMLorentzCombinedSuperoperator.emLorentzGenerator_decompose
            Physlib.QuantumMechanics.ComplexAction.Electromagnetic.EMLorentzCombinedSuperoperator.spacetime_transforms_em
            Physlib.QuantumMechanics.ComplexAction.Electromagnetic.EMLorentzCombinedSuperoperator.covariantLiouvillian_decompose
        """),
        "numerical_adapters": (
            "openwave.xperiments.m9_cat_ept.two_body_forces:run_two_body_force_study",
            "openwave.xperiments.m9_cat_ept.spin_magnetic_observables:run_spin_magnetic_study",
        ),
        "boundary": (
            "formal superoperator supplies covariance and decomposition, not a calibrated dipole force law",
            "force between stable charged CAT/EPT particles remains open",
        ),
    },
)
