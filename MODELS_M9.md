# OpenWave M9 CAT/EPT current comparison profile

M9 is integrated through **M9.119**. Stable callers should use the unversioned current entry points:

```text
conformance   openwave/xperiments/m9_cat_ept/model_conformance_current.py
registration  openwave/xperiments/m9_cat_ept/model_registration_current.py
launcher      openwave/xperiments/m9_cat_ept/_launcher.py
```

Current schemas:

```text
openwave.m9.models-conformance.v22
openwave.model-registration.v22
openwave.m9.platform-integration-contract.v2
```

The conformance schema remains v22 because M9.110--M9.119 add implementation evidence without promoting the evidence-derived 21-criterion headlines last changed at M9.109. Registration advances to schema v22 and records the gauge-covariant strong and electroweak carriers explicitly.

## Authorities

```text
Physlib repository  jagg-ix/entropic-physlib-private
Physlib branch      entropic-physlib-linear-full
Physlib head        bca7617e1294c4645a13bc9eae9aa6d97de78430
Physlib root blob   38e3e4d5b1fcdebf5a4335fb4741a57774a6c0d1
zil-lean head       e09723a44185a1e70031ad2661c8009dc98bef74
```

M9.119 pins exact source blobs for the finite Wilson model, Wilson-loop area-law observables, `GaugeGroupI = SU(3) × SU(2) × U(1)`, the unitary Higgs gauge action, and the quartic Higgs potential. Lean remains proof authority. OpenWave provides finite numerical carriers, local gauge-covariance tests, and falsification gates.

## Evidence-derived maturity policy

M9 is not summarized by a single validated/partial count. Each of the 21 shared criteria carries separate axes for formal status, numerical construction, stability, calibration, physical identity, prediction, and external validation.

A reduced carrier can be constructed while calibration, identity, or prediction readiness remains open. Later numerical evidence cannot promote those axes unless its own authority gate closes them.

The canonical 21-row maturity payload is produced by `criterion_maturity_m109.py` and composed with M9.119 evidence by `model_conformance_current.py`.

## Integrated milestone lineage

| Milestone | Constructed evidence | Retained boundary |
| --- | --- | --- |
| M9.109 | Newton-G clock theorem/evidence audit and evidence-derived maturity | algebraic equivalence is not an external G prediction |
| M9.110--M9.113 | holographic `N_H/N_C` hierarchy, one screen G, shared initial data and synchronized weak/nonlinear histories | physical screen calibration remains open |
| M9.114 | TT metric modes, trace-free extrinsic curvature and shift dynamics | reduced generalized ADM, not general GR |
| M9.115 | conformal connection, unit determinant, trace-free variables, 1+log and Gamma-driver gauges | BSSN-style carrier, not production BSSN |
| M9.116 | metric-built conformal Ricci, reduced screen-tidal source, tensor/Gamma damping and manufactured refinement | finite-grid consistency is not continuum constraint propagation |
| M9.117a | continuous Planck-bit/Compton-cell count flow and finite heat/block semigroup | endpoint particle mass is not derived |
| M9.117b | Gaussian covariance pullback, fixed-point adapter and principal/image limits | free-field fixed point is not interacting CAT/EPT RG closure |
| M9.117c | one-G multi-resolution Poisson/tidal gravity campaign | synthetic scale fixture is not physical calibration or Einstein equivalence |
| M9.119a | local SU(3) links, covariant color-matter evolution, plaquettes and 1×1/2×1 Wilson loops | finite carrier is not lattice QCD and finite loops do not establish confinement |
| M9.119b | local SU(2) and U(1) links, U(1)^3 Higgs doublet action, covariant matter/link flow and quartic vacuum relaxation | bosonic carrier is not full chiral electroweak theory and predicts no physical masses |
| M9.119c | exact Physlib source contract, composed gauge-sector authority and schema-v22 registration | theorem-guided numerical covariance is not a new Lean proof or experimental validation |

## M9.119 numerical gates

### Strong sector

```text
local SU(3) matter/link covariance       closed to numerical precision
Wilson plaquette action invariance       closed
1x1 and 2x1 Wilson-loop invariance       closed
special-unitary link constraints         preserved
non-Abelian commutator                    nonzero
QCD confinement                           not established
```

### Electroweak Higgs sector

```text
local SU(2)xU(1) matter/link covariance  closed to numerical precision
Higgs norm/potential invariance           closed
SU(2) and U(1) Wilson actions             invariant
quartic vacuum norm flow                  constructed
residual U(1) stabilizer                   constructed
full chiral fermion content               open
Weinberg angle and physical masses        not derived
```

## Current decisions

```text
universal holographic G                         preserved
source-coupled reduced BSSN layer                constructed
dynamic count and Gaussian scale flow            constructed
one-G multi-resolution gravity                   constructed
local SU(3) gauge carrier                        constructed
local SU(2)xU(1) Higgs carrier                   constructed
QCD confinement                                  open
complete electroweak theory                      open
particle mass endpoint derivation                open
continuum BSSN/Einstein convergence              open
external physical calibration                    open
out-of-sample physical prediction                not promoted
```

## Reproduction

Stable reports:

```bash
python -m openwave.xperiments.m9_cat_ept._launcher --current-conformance
python -m openwave.xperiments.m9_cat_ept._launcher --current-registration
python -m openwave.xperiments.m9_cat_ept._launcher --platform-contract
```

Direct M9.119 scripts:

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_119a_non_abelian_gauge.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_119b_electroweak_higgs.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_119_current_registration.py
```

## Boundaries

- a theorem-guided adapter is not a new Lean proof;
- a finite lattice carrier is not continuum QCD or the Standard Model;
- Wilson loops must display a controlled area law before confinement can be considered;
- a bosonic Higgs carrier does not supply the missing chiral fermion content;
- uncalibrated couplings and vacuum relaxation do not predict observed masses;
- a constructed reduced carrier does not establish observed-particle identity;
- no external experimental validation is claimed by the current registration.
