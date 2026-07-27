# M9.120 spectral phenomenology findings

## Question

After M9.119 established finite local gauge covariance, can the same carriers support basis-independent spectra, transition-response observables, and controlled refinement without promoting finite model units to physical masses or decay rates?

## Formal baseline

Merged authority:

```text
Physlib branch  entropic-physlib-linear-full
head            3923d802339c957066fcccd579362f739775797a
root blob       d225e3cdb0e3239eb6c83f20af25968ddb9ec37b
```

Pinned merged surfaces:

- finite Hermitian resonance matrices and residuals;
- finite/infinite Bloch localization;
- spectral mismatch and contractive selection weights;
- formal Green-function source jets;
- quartic Higgs vacuum identities.

Draft Physlib PRs #19 and #20 are recorded as candidate layers only. Their heads are not treated as merged proof authority.

## M9.120a — gauge-invariant finite spectra

The negative covariant lattice Laplacian is assembled as a Hermitian matrix on site-internal vectors. Local gauge transformations act by block-unitary similarity.

Representative results:

```text
SU(3) maximum spectral gauge error       1.3224230738240195e-14
SU(3) similarity relative error          4.3047668310502195e-16
SU(3) maximum low-mode residual          7.379966077828003e-15
SU(2)xU(1) maximum spectral gauge error  1.1407541578023483e-14
SU(2)xU(1) similarity relative error     4.990492365021785e-16
SU(2)xU(1) maximum low-mode residual     5.710545269704189e-15
```

At the homogeneous quartic Higgs vacuum, the real four-coordinate local Hessian has eigenvalues

```text
0, 0, 0, 4.8
```

for the default `mu_squared = 1.2`. The three zero-curvature directions are tangent to the gauge orbit; the radial curvature is exactly `4 mu_squared`. These are model-unit curvature modes, not physical Goldstone or Higgs particle masses.

## M9.120b — gauge-invariant response

A site-scalar source acts identically on internal components, so it commutes with local gauge transformations. The broadened spectral response is therefore basis independent.

```text
SU(3) response gauge relative error      1.0185952067547417e-14
SU(3) completeness sum-rule error        3.370696285722868e-16
SU(2)xU(1) response gauge error          4.7630433479279775e-15
SU(2)xU(1) completeness sum-rule error   3.968604612890190e-16
Higgs radial source strength             1
Higgs tangent source strength            0
```

The Lorentzian broadening is a numerical resolution parameter. The closed Hermitian carriers do not construct intrinsic irreversible decay.

## M9.120c — four-grid refinement

Smooth links are scaled as

```text
U_mu(x) = exp(i h A_mu(x))
```

on a fixed `2 pi` periodic box. This scaling is required for a meaningful grid sequence; directly reusing unscaled M9.119 links would change the physical background as the grid changes.

Flat-link first positive eigenvalue errors decrease across `5, 7, 9, 11`:

```text
0.1248597999
0.0653627562
0.0399615153
0.0268950129
```

Smooth low-cluster relative changes decrease:

```text
SU(3)       0.0637202155, 0.0264428307, 0.0134114031
SU(2)xU(1)  0.0516226424, 0.0215054348, 0.0108094891
```

This is finite-grid Cauchy improvement, not a continuum spectral theorem.

## Decision

```text
gauge-invariant finite spectra           constructed
gauge-invariant finite response           constructed
spectral completeness sum rules           closed
Higgs radial/tangent selection            constructed
four-grid spectral refinement             completed
dimensionless phenomenology ledger        constructed
intrinsic decay dynamics                  not constructed
physical mass/coupling calibration        open
observed particle identity                open
continuum spectrum theorem                open
external validation                       open
```

The next executable target is an explicitly open-system, gauge-covariant response/decay carrier. Any linewidth, lifetime, or particle label must remain separately evidence-gated.
