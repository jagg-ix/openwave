# M9 CAT/EPT roadmap

Research mode remains headless. No `_launcher.py` is added until a validated
three-dimensional dynamics exists.

| Task | Deliverable | Status / gate |
| --- | --- | --- |
| M9.1 | Version-pinned formal contract and conformance suite | DONE |
| M9.2 | Free complex-field solver and exact Gaussian benchmark | DONE |
| M9.3 | Fixed field-to-probability map and coarse-graining clocks | DONE |
| M9.4 | Bounded nonlinear family and localization decision gate | DONE; focusing candidate passed |
| M9.5 | Exact energy, radius, phase-frequency, and scaling family ledger | DONE; nine-case executable ledger |
| M9.6 | Scalar charge/spin/topology audit and replacement-carrier contract | DONE; current-carrier limits closed |
| M9.7 | Replacement-carrier localization in 3D, then Taichi port and launcher | Gated on a validated non-scalar carrier |

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

Nine products `g in {1,2,4}`, `N in {0.5,1,2}` verify the formulas. The
implemented enclosed-probability check uses the fraction of total norm, not
absolute enclosed norm, so all `N` values share the same `tanh(eta R)` law.

The norm exponents are

```text
eta ~ N^1,
omega_phase ~ N^2,
|E| ~ N^3,
R_rms ~ N^-1.
```

Two scale-invariant identities close:

```text
omega_phase R_rms^2 = pi^2/24,
E/(mu N) = 1/3.
```

The optional Compton and Zitterbewegung bridges remain conditional unit-map
identifications and do not supply a mass prediction.

### M9.6 scalar-carrier boundary

The executable audit proves the following for the current carrier and profile:

1. global phase preserves density, norm, phase current, and scalar energy;
2. conjugation preserves norm/energy and reverses phase current, but does not
   create an opposite electric-charge sector;
3. a local phase changes ordinary-gradient energy because no gauge connection
   exists;
4. `s psi`, `s in [0,1]`, contracts the profile continuously to zero vacuum;
5. scalar intrinsic rotations return `+1` at `2pi`, unlike a spinor double cover;
6. no Maxwell source, Gauss flux, charge unit, spinor representation, or
   topological boundary class is present.

The staged spinor embedding `Psi=(psi,0)` preserves
`Psi-dagger Psi=|psi|^2`, so the normalized-density entropic-clock interface can
survive a carrier replacement. This does not establish that the replacement
localizes.

See [`findings/m9_6_method_note.md`](findings/m9_6_method_note.md).

## Next gate: replacement-carrier localization

The next scientific program must choose one bounded route before running:

- locally gauge-coupled scalar for charged spin-0 matter;
- Dirac/Weyl spinor plus local gauge field for spin-1/2 charge;
- multi-component topological order parameter for winding/defect sectors.

For any route, the acceptance gate must re-establish localization, conservation,
window independence, perturbation stability, and the entropic-clock density map.
No interactive renderer is justified before that gate passes.
