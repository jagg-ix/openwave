# PhysLib/ZIL reuse map for M9.46--M9.48

Source repository: `jagg-ix/entropic-physlib-private`  
Source branch: `entropic-physlib-linear-full`

## ZIL `reused_components`

- `HilbertSchmidtOperatorSpace.HSOp`
- `HilbertSchmidtOperatorSpace.leftMulHS_rightMulHS`
- `NormedSpace.exp`
- `QuantumMechanics.SpaceDHilbertSpace.mulOperator`
- `QuantumMechanics.SpaceDHilbertSpace.mulOperator_isClosable`
- `MeasureTheory.tendsto_integral_of_dominated_convergence`
- `MeasureTheory.TendstoInDistribution`
- `MeasureTheory.tendstoInDistribution_of_ae_tendsto`
- `ProbabilityMeasure`

## Direct Lean carriers

- `StandardModel.GaugeGroupI`
- `StandardModel.GaugeGroupI.toSU3`
- `CKMMatrix`
- `PhaseShiftRelation`

## ZIL `open_targets` preserved as boundaries

- `continuum_lindblad_generator`
- `continuum_semigroup_wellposed`
- `phase_space_fokker_planck_bridge`
- `lorentz_sum_converges_to_continuum_hybridization`
- `lddl_current_converges_to_continuum_current`
- `genuinely_infinite_particle_representation`

OpenWave therefore uses finite-dimensional or finite-grid controls only. No continuum theorem, kernel-checked proof, or full-QCD claim is inferred from the reuse map.
