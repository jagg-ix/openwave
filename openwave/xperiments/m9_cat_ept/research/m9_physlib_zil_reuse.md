# PhysLib/ZIL reuse map through M9.56

Source repository: `jagg-ix/entropic-physlib-private`  
Source branch: `entropic-physlib-linear-full`  
Pinned ZIL workflow: `jagg-ix/zil-lean@167cf603aba21bb1160cbe68ad1c4ba9056f92e9`

## Exact source identities

| Path | Git blob SHA | Role |
| --- | --- | --- |
| `formalization/zil/lindblad-driven-leads.zc` | `8f98a97bb12f0b5ab21fbcc62f878e0650894353` | finite generator/evolution graph |
| `formalization/zil/liouville-second-quantization.zc` | `8141e353dc5960ef28c01883ccbb10411f62ac05` | continuum carrier and open-target graph |
| `Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/Basic.lean` | `634087560adaffaaa5a683c47f3dee123501fb28` | bounded generator and exponential definitions |
| `Physlib/QuantumMechanics/OpenSystems/LiouvilleSecondQuantization.lean` | `9d2c905c940480f1ed570cf0be965d5a9b6c4831` | continuum `L²` carrier, regular pointwise actions, and dense-domain declaration |
| `Physlib/QuantumMechanics/DDimensions/Operators/Multiplication.lean` | `9e43c4a6b6eee5f22efdaa9ef4ce3c2b84cef7b5` | maximal-domain and closable multiplication operator |

## Reused boundaries

- `HilbertSchmidtOperatorSpace.HSOp`
- `HilbertSchmidtOperatorSpace.leftMulHS_rightMulHS`
- `NormedSpace.exp`
- `QuantumMechanics.LiouvilleSecondQuantization.ContinuumKernelSpace`
- `QuantumMechanics.LiouvilleSecondQuantization.spacePointwiseKernelOperator_hasDenseDomain`
- `QuantumMechanics.SpaceDHilbertSpace.mulOperator`
- `QuantumMechanics.SpaceDHilbertSpace.mulOperator_isClosable`
- `OpenSystemLindblad.lindblad_trace_preserving`
- `DampedHeatSemigroup.RealC0ContractionSemigroup`

## Finite target closure

- M9.53 closes `phase_space_fokker_planck_bridge` for the implemented finite Markov/Strang solver.
- M9.54 closes finite smooth-domain projection, generator-graph convergence, and sampled shifted-dissipativity controls.
- M9.55 closes the source/declaration refresh mechanism but promotes zero formal proofs.
- M9.56 closes one nested-grid convergence campaign for the implemented unified nonlinear PDE.

These are computational closures, not continuum theorems.

## Open targets retained

- full nonlinear CAT/EPT generator closability
- maximal dissipativity and nonlinear semigroup generation
- `continuum_lindblad_generator`
- `continuum_semigroup_wellposed`
- `continuum_hypoelliptic_wellposed`
- Lorentz-sum and current continuum convergence
- genuinely infinite-particle representation

## Computational source pins

- M9.49: `unified_self_binding_3d.py`, blob `e22bbb02ed93a856be438cbbcc5fbc2198be9524`.
- M9.50: `semigroup_bridge.py`, blob `6767a73827142c9a93278b5b705c42e563ab9ac9`.
- M9.53: `fokker_planck_bridge.py`, blob `914bd157a860b53def562ef7fb30ac50fa42fe74`.
- M9.54: `nonlinear_generator_bridge.py`, blob `66deb60ec3f9b2c2b4ba5529de3dc63f890e4850`.
- M9.55: `kernel_evidence_refresh.py`, blob `7c570e77f366a9dc37b371886a0137a355bb9814`.
- M9.56: `unified_convergence.py`, blob `d547841da80031f72ad324d378b6748ab6c5156b`.

All OpenWave computational records are pinned to the post-merge `main` location.

## Promotion policy

ZIL `pending_ci` means implementation declared, not proved. ZIL `open` means boundary only. Formal promotion requires a matching source hash, a declared witness, explicit `kernel_checked` state, and no open assumptions. M9.55 therefore promotes zero formal proofs.
