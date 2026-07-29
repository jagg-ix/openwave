# M9.137 — global inference, statistics, and vacuum-wave authority

This milestone was selected after comparing the previously pinned Physlib head
`bca7617e1294c4645a13bc9eae9aa6d97de78430` with the current
`entropic-physlib-linear-full` tip
`8bafa9ab93cbb39e85909fc3837bb4b6e0dec748`, then inspecting the complete root
import surface and existing OpenWave authorities. The upstream delta contains 46
commits; the selection is not based only on the final commit.

The QCD, gravity, Page--Wootters, linewidth/KL, and anomaly families are already
represented on current OpenWave `main`. Three imported theorem families remained
unrepresented and independently executable.

## M9.137a — Cramér--Rao inference precision

Pinned source:

`Physlib/QuantumMechanics/ComplexAction/EntropicTime/CramerRaoInferenceMass.lean`

The executable bridge integrates a Gaussian location model and checks that the
score is centered, its variance is `1/v`, the regularity covariance is one, and
the sample-mean estimator saturates `Var[T] I = 1`.

Boundary: the theorem establishes Fisher information as an attainable inference
precision limit. It does not derive the physical identification `mass = Fisher
information`.

## M9.137b — Pauli exchange and exclusion

Pinned source:

`Physlib/QFT/PerturbationTheory/FieldStatistics/PauliExchange.lean`

The bridge checks sign reversal of a two-state antisymmetrized amplitude,
vanishing for coincident labels, and the two-exchange involution.

Boundary: this is the algebraic Pauli identity. It is not the spin-statistics
theorem and does not assign fermionic statistics dynamically to a CAT/EPT
excitation.

## M9.137c — harmonic Maxwell plane-wave certificate

Pinned source:

`Physlib/Electromagnetism/Vacuum/HarmonicWaveCertificate.lean`

The bridge evaluates the exact transverse cosine component and independently
checks its finite-difference vacuum wave equation and analytic time curvature.

Boundary: this is a classical free-field certificate. It does not quantize the
field, derive photons, calibrate units, or derive electromagnetism from CAT/EPT.

## Reproduction

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_137_global_inference_statistics_emwave.py
python -m pytest -vv tests/test_m9_global_inference_statistics_emwave_m137.py
```

No Physlib file or physical criterion status is modified.
