# PhysLib/ZIL reuse map through M9.59

Source repository: `jagg-ix/entropic-physlib-private`  
Source branch: `entropic-physlib-linear-full`  
Pinned branch head: `14ecf025ec58d2ec9e4731081c4ed1853f4468f0`  
Pinned ZIL workflow: `jagg-ix/zil-lean@167cf603aba21bb1160cbe68ad1c4ba9056f92e9`

## Current formal source identities

| Path | Git blob SHA | Role |
| --- | --- | --- |
| `formalization/zil/electrogravitic-action-closure.zc` | `cf9110d8b4229c33a1e2cefa34c0719062a3f340` | scoped action/PDE closure graph |
| `GlobalEinsteinHilbertAction.lean` | `6862565fb915b5c6f1cc561b769e190b70f3156a` | global gravitational action and dominated derivative |
| `GlobalElectrograviticAction.lean` | `39e807f424cf8384135299e84fdffc97fb506ee5` | integrated coupled-action derivative seam |
| `ADMConstraintPropagation.lean` | `600b872eb73611de817df0d00dd6711570c567e2` | continuum carrier, constraint propagation, global flow under hypotheses |
| `MaximalCauchyDevelopment.lean` | `2504c579fd8f8afe0a1670911142fb0e7ecdb2c0` | conditional chain gluing and maximal development |
| `docs/EntropicDynamicsClosure.md` | `e9d542ea516492b6e308a5610f952f831f4ed1c5` | corrected scientific status ledger |

Earlier LDDL, Liouville, multiplication-operator, trace-preservation, and Cauchy-limit sources remain reusable. Evidence state must be read from the corresponding ZIL graph rather than inferred solely from the presence of a Lean declaration.

## M9.57--M9.59 closure

- M9.57 reconciles the live formal branch and checks a finite action derivative and reversible/dissipative generator split.
- M9.58 closes nested finite kinetic convergence, mass/positivity, and algebraic Hörmander rank.
- M9.59 introduces a bounded cubic--quintic action density and selects a finite-grid localization candidate against the original-action baseline.

## Open boundaries

- uniqueness or first-principles derivation of the selected binding action;
- full nonlinear CAT/EPT continuum generator closability and maximal dissipativity;
- continuum kinetic existence, uniqueness, subelliptic estimates, and hypoellipticity;
- continuum compactness and orbital stability for the selected 3D candidate;
- concrete calibrated coupled Einstein--Maxwell--entropic physical evolution;
- physical mass, charge, clock, coupling, lifetime, and experimental agreement.

## Status policy

Use the vocabulary `directly proved`, `proved with explicit scope`, `conditional on explicit analytic data`, and `not closed end-to-end`. OpenWave platform validation remains separate. ZIL records identities, dependencies, scope, and evidence states; Lean remains proof authority.
