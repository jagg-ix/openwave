# PhysLib/ZIL reuse map through M9.52

Source repository: `jagg-ix/entropic-physlib-private`  
Source branch: `entropic-physlib-linear-full`  
Pinned ZIL workflow: `jagg-ix/zil-lean@167cf603aba21bb1160cbe68ad1c4ba9056f92e9`

## Exact source identities

| Path | Git blob SHA | Role |
| --- | --- | --- |
| `formalization/zil/lindblad-driven-leads.zc` | `8f98a97bb12f0b5ab21fbcc62f878e0650894353` | finite generator/evolution graph |
| `formalization/zil/liouville-second-quantization.zc` | `8141e353dc5960ef28c01883ccbb10411f62ac05` | continuum carrier/open-target graph |
| `Physlib/QuantumMechanics/OpenSystems/LindbladDrivenLeads/Basic.lean` | `634087560adaffaaa5a683c47f3dee123501fb28` | bounded generator and exponential definitions |
| `Physlib/QuantumMechanics/DDimensions/Operators/Multiplication.lean` | `9e43c4a6b6eee5f22efdaa9ef4ce3c2b84cef7b5` | dense-domain and closable multiplication carrier |

## Reused boundaries

- `HilbertSchmidtOperatorSpace.HSOp`
- `HilbertSchmidtOperatorSpace.leftMulHS_rightMulHS`
- `NormedSpace.exp`
- `QuantumMechanics.SpaceDHilbertSpace.mulOperator`
- `QuantumMechanics.SpaceDHilbertSpace.mulOperator_isClosable`
- continuum `L²` kernel carrier
- dominated-convergence observable bridge

## Open targets retained

- `continuum_lindblad_generator`
- `continuum_semigroup_wellposed`
- `phase_space_fokker_planck_bridge`
- Lorentz-sum and current continuum convergence
- genuinely infinite-particle representation

## Computational source pins

- M9.49 merged source: `jagg-ix/openwave@main:openwave/xperiments/m9_cat_ept/unified_self_binding_3d.py`, Git blob `e22bbb02ed93a856be438cbbcc5fbc2198be9524`.
- M9.50 is a finite-grid computational bridge and does not change formal proof state.
- M9.52 depends on merged M9.49 and broadens its profile families; it does not alter any formal theorem state.

## Promotion policy

ZIL `pending_ci` means implementation declared, not proved. ZIL `open` means boundary only. Formal promotion requires a matching source hash and explicit `kernel_checked` state. M9.51 therefore promotes zero formal proofs.
