# M9 CAT/EPT roadmap

Research mode remains headless. No `_launcher.py` is added until a validated
three-dimensional dynamics exists.

| Task | Deliverable | Status / gate |
| --- | --- | --- |
| M9.1 | Version-pinned formal contract and conformance suite | DONE |
| M9.2 | Free complex-field solver and exact Gaussian benchmark | DONE |
| M9.3 | Fixed field-to-probability map and coarse-graining clocks | DONE |
| M9.4 | Bounded nonlinear family and localization decision gate | DONE; focusing candidate passed |
| M9.5 | Exact energy, radius, phase-frequency, and scaling family ledger | DONE; all nine family checks passed |
| M9.6 | Scalar charge/spin no-go and replacement-carrier contract | NEXT |
| M9.7 | Three-dimensional dynamics, then Taichi port and launcher | Gated on a validated 3D carrier |

## Completed results

### M9.1--M9.4

- formal theorem-to-code contract is source-pinned;
- free Gaussian control converges at approximately second order;
- one explicit Markov channel produces a closed coarse-graining information ledger;
- the selected focusing cubic member supports a convergent neutral 1+1D soliton;
- identical free and defocusing controls disperse.

### M9.5 exact scaling family

For

```text
i psi_t = -1/2 psi_xx - g |psi|^2 psi,
```

the norm-`N` family is

```text
eta = gN/2,
psi = eta/sqrt(g) sech(eta x) exp(i eta^2 t/2).
```

The exact observables are

```text
mu = -eta^2/2,
omega_phase = eta^2/2,
E = -eta^3/(3g) = -g^2 N^3/24,
R_rms = pi/(2 sqrt(3) eta).
```

Nine products `g in {1,2,4}`, `N in {0.5,1,2}` verify the formulas. Maximum
relative quadrature errors are `2.56e-14` for norm, `7.57e-14` for energy, and
`4.19e-12` for RMS radius. The stationary residual is below `2.8e-16` relative.

The fitted norm exponents are

```text
eta ~ N^1,
omega_phase ~ N^2,
|E| ~ N^3,
R_rms ~ N^-1.
```

Two scale-invariant identities close exactly:

```text
omega_phase R_rms^2 = pi^2/24,
E/(mu N) = 1/3.
```

The optional Compton and Zitterbewegung bridges are conditional unit-map
identifications. Neither supplies a mass prediction.

See [`findings/m9_5_method_note.md`](findings/m9_5_method_note.md).

## Next gate: M9.6

M9.6 must make the present carrier limitations executable:

1. global phase leaves scalar density and energy unchanged;
2. conjugation leaves norm and energy unchanged and only reverses current;
3. the localized profile contracts continuously to the zero vacuum;
4. intrinsic scalar rotations return with `+1` after `2pi`, unlike spin-1/2;
5. no local gauge connection, Gauss-law flux, or opposite-charge sector exists.

It must then specify a staged replacement carrier that preserves `psi-dagger psi`
and the entropic-clock interface without claiming that the replacement already
localizes.
