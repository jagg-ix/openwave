# OpenWave M9 CAT/EPT current comparison profile

M9 is integrated through **M9.120**. Stable callers should use the unversioned current entry points:

```text
conformance   openwave/xperiments/m9_cat_ept/model_conformance_current.py
registration  openwave/xperiments/m9_cat_ept/model_registration_current.py
launcher      openwave/xperiments/m9_cat_ept/_launcher.py
```

Current schemas:

```text
openwave.m9.models-conformance.v22
openwave.model-registration.v23
openwave.m9.platform-integration-contract.v3
```

The conformance schema remains v22 because M9.110--M9.120 add implementation evidence without promoting the evidence-derived 21-criterion headlines last changed at M9.109. Registration advances to schema v23 and records finite gauge spectra, response, and refinement explicitly.

## Authorities

```text
Physlib repository  jagg-ix/entropic-physlib-private
Physlib branch      entropic-physlib-linear-full
merged Physlib head 3923d802339c957066fcccd579362f739775797a
Physlib root blob   d225e3cdb0e3239eb6c83f20af25968ddb9ec37b
zil-lean head       e09723a44185a1e70031ad2661c8009dc98bef74
```

M9.120 pins exact merged source blobs for finite Hermitian resonance matrices and residuals, finite/infinite Bloch localization, entropic spectral mismatch weights, formal Green-function source jets, and the quartic Higgs potential.

Two newer Physlib heads are recorded as candidates only:

```text
PR #19  128bebd375cd895af1431444974a7a591c872a31  draft/open/unmerged
PR #20  e192104955fc516f1ba267f8653f0dcf8d18ab51  draft/open/unmerged
```

They are not used as merged proof authority. Lean remains proof authority; OpenWave supplies finite numerical carriers and falsification gates.

## Evidence-derived maturity policy

M9 is not summarized by a single validated/partial count. Each of the 21 shared criteria carries separate axes for formal status, numerical construction, stability, calibration, physical identity, prediction, and external validation.

A reduced carrier can be constructed while calibration, identity, or prediction readiness remains open. Later numerical evidence cannot promote those axes unless its own authority gate closes them.

The canonical 21-row maturity payload is produced by `criterion_maturity_m109.py` and composed with M9.120 evidence by `model_conformance_current.py`.

## Integrated milestone lineage

| Milestone | Constructed evidence | Retained boundary |
| --- | --- | --- |
| M9.109 | Newton-G clock theorem/evidence audit and evidence-derived maturity | algebraic equivalence is not an external G prediction |
| M9.110--M9.113 | holographic `N_H/N_C` hierarchy, one screen G, shared initial data and synchronized weak/nonlinear histories | physical screen calibration remains open |
| M9.114--M9.116 | generalized ADM and source-coupled BSSN-style refinement | finite-grid gravity is not production numerical relativity or a continuum proof |
| M9.117 | count/block flow, Gaussian covariance scale adapter and one-G multi-resolution gravity | particle mass, interacting fixed point and physical screen calibration remain open |
| M9.119 | local SU(3) and SU(2)xU(1) gauge links with covariant matter/link evolution | finite carriers are not QCD or the full electroweak Standard Model |
| M9.120a | Hermitian covariant operators, locally gauge-invariant spectra, eigenpair residuals and Higgs tangent/radial curvature modes | finite eigenvalues are not observed masses |
| M9.120b | gauge-invariant site-source response, spectral completeness sum rules and radial/tangent selection | Lorentzian broadening is not an intrinsic decay width |
| M9.120c | flat and smooth four-grid spectral refinement plus a dimensionless phenomenology ledger | improving finite-grid sequences are not continuum or external-validation results |

## M9.120 numerical gates

### Gauge spectra

```text
SU(3) and SU(2)xU(1) operators       Hermitian and nonnegative
local-gauge spectral invariance      closed to numerical precision
low-mode eigenpair residuals         closed
Higgs tangent modes                  three zero-curvature directions
Higgs radial curvature               4 mu^2 in model units
physical mass interpretation         not promoted
```

### Transition response

```text
site-scalar source                    commutes with local gauge rotations
broadened spectral response           gauge invariant
spectral completeness sum rule        closed
radial/tangent Higgs selection        closed
intrinsic irreversible decay          not constructed
physical transition identification    not promoted
```

### Refinement

```text
fixed physical two-torus              used
link scaling                           U = exp(i h A)
odd grids                              5, 7, 9, 11
flat first-mode error                  monotonically decreasing
smooth strong low-cluster change       monotonically decreasing
smooth electroweak low-cluster change  monotonically decreasing
continuum theorem                      open
physical-unit calibration             open
```

## Current decisions

```text
universal holographic G                         preserved
source-coupled reduced BSSN layer                constructed
local SU(3) gauge carrier                        constructed
local SU(2)xU(1) Higgs carrier                   constructed
gauge-invariant finite spectra                   constructed
gauge-invariant finite response                  constructed
finite spectral refinement                       constructed
dimensionless phenomenology ledger               constructed
QCD confinement                                  open
complete electroweak theory                      open
intrinsic decay dynamics                         open
physical mass and coupling calibration           open
continuum spectrum theorem                       open
observed-particle identity                       open
external physical validation                     open
```

## Reproduction

Stable reports:

```bash
python -m openwave.xperiments.m9_cat_ept._launcher --current-conformance
python -m openwave.xperiments.m9_cat_ept._launcher --current-registration
python -m openwave.xperiments.m9_cat_ept._launcher --platform-contract
```

Direct M9.120 scripts:

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_120a_gauge_spectrum.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_120b_linear_response.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_120c_spectral_refinement.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_120_current_registration.py
```

## Boundaries

- a theorem-guided adapter is not a new Lean proof;
- an unmerged draft Physlib PR is not merged formal authority;
- finite lattice spectra are not calibrated particle masses;
- numerical broadening is not an intrinsic decay width;
- four-grid Cauchy improvement is not a continuum theorem;
- dimensionless response and spectrum ledgers are not external phenomenology;
- no observed-particle identity or external experimental validation is claimed.
