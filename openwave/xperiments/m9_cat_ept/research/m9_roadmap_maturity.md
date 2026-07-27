# M9 maturity-based roadmap

M9.100--M9.108 established evidence-derived maturity, coupled particle/field campaigns, nonlinear reduced gravity, and dynamical candidate states. M9.109 audited the Compton-clock specialization. M9.110--M9.117 restore the holographic area-per-bit hierarchy, advance its gravity carrier through source-coupled BSSN-style refinement, and construct an explicit theorem-guided coarse-graining flow.

| Task | Target | State |
| --- | --- | --- |
| M9.100--M9.108 | Evidence authority, coupled dynamics, reduced nonlinear gravity, interaction sectors, candidate states | DONE; PHYSICAL IDENTITY SEPARATE |
| M9.109 | Formal clock identities, anchor protocol, theorem/paper scope, and numerical Compton-cell interpretation | DONE; NO LEAN THEOREM FALSIFIED |
| M9.110a--d | Separate `N_H`/`N_C`, preserve universal `A/N_H`, and inject one screen `G` into both gravity carriers | DONE; PHYSICAL CALIBRATION SEPARATE |
| M9.110e | Execute both carriers from one screen anchor and compare shared source, potential, metric seed, and initial constraints | DONE; INITIAL-STATE CONSISTENCY ONLY |
| M9.110f--M9.113 | Compare synchronized weak/nonlinear histories and retain nonlinear-only curvature and constraints | DONE; REDUCED CONFORMAL-ADM SCOPE |
| M9.114a--c | Add TT metric modes, trace-free extrinsic curvature, and shift dynamics | DONE; REDUCED GENERALIZED ADM |
| M9.115a | Add conformal connection functions and their differential constraint | DONE; REDUCED BSSN-STYLE |
| M9.115b | Enforce unit determinant and trace-free conformal variables | DONE; ALGEBRAIC CONTROL |
| M9.115c | Add 1+log lapse and Gamma-driver shift evolution | DONE; GAUGE REFINEMENT |
| M9.116a | Build the conformal Ricci tensor from the evolved metric and couple the screen-density tidal source | DONE; REDUCED SCALAR-SOURCE CARRIER |
| M9.116b | Add exact-Fourier STF tensor-momentum correction and damp the conformal-connection constraint | DONE; DIFFERENTIAL CONSTRAINT DAMPING |
| M9.116c | Execute analytic manufactured-source checks and three-grid Cauchy refinement | DONE; FINITE-GRID CONSISTENCY, NOT CONTINUUM PROOF |
| M9.117a | Construct continuous count flow and finite heat/block-spin screen flow while preserving `A/N_H` | DONE; ENDPOINT MASS SELECTION OPEN |
| M9.117b | Bind Gaussian covariance pullback, composable injections, semigroup flow, and principal/image limits to Physlib | DONE; FREE-FIELD FIXED POINT ONLY |
| M9.117c | Inject one screen `G` across three gravity resolutions and compare low-mode Poisson/tidal observables | DONE; SCALE CONSISTENCY, NOT CALIBRATION |
| M9.118 | Execute an independently calibrated physical screen-density campaign | BLOCKED ON EXTERNAL ANCHOR |
| M9.119 | Replace reduced color/chiral carriers with gauge-covariant non-Abelian/electroweak systems | NEXT |
| M9.120 | Connect stable candidate carriers to spectra, decays, and phenomenology | PLANNED |

## Corrected holographic implication

The primary gravitational equation is

```text
G = (A/N_H) c^3/hbar,
A/N_H = l_P^2.
```

For an entanglement screen based on a particle Compton scale, both `A` and `N_H` vary as `m^-2`; their ratio remains universal. The mass-dependent expression `hbar*c/m^2` is obtained only after replacing the Planck-area bit count with the coarser Compton-cell count. The M9.117 coarse-graining flow does not make that replacement in the definition of `G`; it preserves microscopic area per bit while grouping Planck bits into coarser cells.

## Current decision

```text
universal holographic G                  preserved
N_H/N_C exact count ratio                closed
one screen G shared across carriers      constructed
shared matter/source histories           constructed
conformal connection functions           constructed
unit determinant control                 constructed
trace-free conformal curvature           constructed
1+log lapse evolution                    constructed
Gamma-driver shift evolution             constructed
metric-built conformal Ricci tensor      constructed
screen-source tidal curvature            constructed
STF tensor-momentum damping               constructed
Gamma-constraint damping                 constructed
three-grid manufactured refinement       completed
finite-grid Cauchy consistency            established
dynamic N_H/N_C count flow               constructed
finite heat/block-spin screen flow       constructed
Gaussian covariance pullback             constructed
free-field covariance fixed point        reproduced
principal/image continuum limits         reproduced
one-G multi-resolution gravity           constructed
particle mass endpoint derivation        open
interacting CAT/EPT fixed point           open
continuum BSSN convergence proof          open
production BSSN                          open
full general Einstein evolution          open
external physical calibration            open
```

## Current upstream authorities

```text
OpenWave integration head  agent/m9-generalized-adm-screen-114
Physlib                    bca7617e1294c4645a13bc9eae9aa6d97de78430
zil-lean                   e09723a44185a1e70031ad2661c8009dc98bef74
```

The M9.117 flow gives the exact count ratio a composable finite and continuous scale mechanism while keeping the microscopic area per bit fixed. The Gaussian adapter reproduces the formal free-field fixed-point structure, and low Fourier-mode gravity observables agree across three odd grids. These results do not derive a particle mass, establish the interacting CAT/EPT renormalisation fixed point, supply an external screen calibration, or constitute production numerical relativity.