# M9.138 — complex-action, entropic-time, and gauge authority

This milestone is based on a global inspection of the complete
`entropic-physlib-linear-full` branch, not only its latest commit. The branch tip
is pinned to `8bafa9ab93cbb39e85909fc3837bb4b6e0dec748`.

Current OpenWave `main` already represents the QCD, anomaly, gravity, clock,
Page–Wootters, calibrated linewidth/KL, inference-statistics, Pauli-exchange,
and harmonic-vacuum-wave theorem families. The following three directly useful
families remained absent as one executable authority.

## Target 1 — complex variational stationarity

Pinned source:

`Physlib/Mathematics/LovelockRund/ComplexActionVariational.lean`

The bridge checks that the pointwise residual `E_R + i E_I` vanishes exactly
when both real and imaginary components vanish. This represents the formal
split used by a complex action without claiming that OpenWave has derived the
complete CAT/EPT field equations.

## Target 2 — entropic-time gradient and action weight

The same pinned Lean module defines the local entropic-time gradient `E_I/ℏ`
and proves that the modulus of the complex-action weight is `exp(-E_I/ℏ)`.
The executable authority checks both identities and rejects `ℏ = 0`.

Boundary: positivity or monotonicity of entropic time is not automatic. It
requires a sign condition and a dynamical law for the imaginary action.

## Target 3 — covariant electromagnetic gauge invariance

Pinned source:

`Physlib/Electromagnetism/Kinematics/GaugeTransformation.lean`

The executable bridge constructs a smooth polynomial gauge scalar, verifies
that its pure-gradient potential has zero antisymmetric field strength, and
checks that adding that gradient to a nontrivial potential leaves `F_{μν}`
unchanged.

Boundary: this establishes the numerical counterpart of gauge redundancy. It
does not derive electromagnetism, photons, charge calibration, or a physical
particle identity from CAT/EPT.

## Reproduction

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_138_complex_action_gauge_authority.py
python -m pytest -vv tests/test_m9_complex_action_gauge_authority_m138.py
```

No Physlib file and no physical criterion status is modified.
