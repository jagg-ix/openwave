# OpenWave M9 CAT/EPT current comparison profile

M9 is integrated through **M9.117**. Stable callers should use the unversioned current entry points:

```text
conformance   openwave/xperiments/m9_cat_ept/model_conformance_current.py
registration  openwave/xperiments/m9_cat_ept/model_registration_current.py
launcher      openwave/xperiments/m9_cat_ept/_launcher.py
```

Current schemas:

```text
openwave.m9.models-conformance.v22
openwave.model-registration.v21
openwave.m9.platform-integration-contract.v1
```

The conformance schema remains v22 because M9.110--M9.117 add implementation and scale-flow evidence without promoting the evidence-derived 21-criterion headlines last changed at M9.109. The registration advances through schema v21 and records those later layers explicitly.

## Authorities

```text
Physlib repository  jagg-ix/entropic-physlib-private
Physlib branch      entropic-physlib-linear-full
Physlib head        bca7617e1294c4645a13bc9eae9aa6d97de78430
zil-lean head       e09723a44185a1e70031ad2661c8009dc98bef74
```

The M9.117 formal contract pins exact Hamiltonian-renormalisation and dimensional-scaling source blobs. Lean remains proof authority. OpenWave provides numerical adapters, finite-grid evidence, and falsification gates.

## Evidence-derived maturity policy

M9 is not summarized by a single validated/partial count. Each of the 21 shared criteria carries separate axes for:

- formal status;
- numerical state construction;
- stability or dynamical closure;
- calibration;
- physical identity;
- prediction and external validation.

A reduced carrier can be constructed while calibration, identity, or prediction readiness remains open. Later numerical evidence cannot promote those axes unless its own authority gate closes them.

The canonical 21-row maturity payload is produced by `criterion_maturity_m109.py` and composed with M9.117 evidence by `model_conformance_current.py`.

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

## Current decisions

```text
universal holographic G                         preserved
one screen G shared across gravity carriers     constructed
source-coupled reduced BSSN layer                constructed
finite three-grid refinement                     completed
dynamic count and block flow                     constructed
Gaussian covariance scale adapter                constructed
one-G multi-resolution gravity                   constructed
particle mass endpoint derivation                open
interacting CAT/EPT fixed point                  open
continuum BSSN/Einstein convergence              open
external physical screen calibration             open
out-of-sample physical prediction                not promoted
```

## Reproduction

Stable reports:

```bash
python -m openwave.xperiments.m9_cat_ept._launcher --current-conformance
python -m openwave.xperiments.m9_cat_ept._launcher --current-registration
python -m openwave.xperiments.m9_cat_ept._launcher --platform-contract
```

Direct scripts:

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_current_conformance.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_current_registration.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_current_platform_contract.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_117a_screen_scale_flow.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_117b_gaussian_covariance_flow.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_117c_coarse_grained_gravity.py
```

## Boundaries

- a theorem-guided adapter is not a new Lean proof;
- a finite-grid campaign is not a continuum theorem;
- a synthetic screen anchor is not physical measurement;
- the Compton-cell count does not replace the microscopic holographic count in Newton's coupling;
- a constructed reduced carrier does not establish observed-particle identity;
- no external experimental validation is claimed by the current registration.
