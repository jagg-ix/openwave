# M9.136 — QCD order-parameter chain

This milestone follows a global inspection of `Physlib.lean` at
`entropic-physlib-linear-full@8bafa9ab93cbb39e85909fc3837bb4b6e0dec748`, not merely the latest commit diff.

The previous M9.135 authority covered one-loop running, theta-vacuum algebra,
complex-action confinement factorization, color counting, and trace-anomaly sign structure.
The next three branch-wide gaps were the connected nonperturbative order-parameter chain:

1. **Polyakov-loop deconfinement** — exact Z(3) fixed-point algebra, positive Boltzmann magnitude,
   monotonicity with temperature and static-quark free energy.
2. **Chiral symmetry breaking and GMOR** — O(2) chiral-circle invariance, symmetry-breaking
   order parameter, massless chiral limit, positive and quark-mass-linear pion mass squared.
3. **Axial anomaly and eta-prime topology** — anomalous theta shift, conditional massless-quark
   cancellation, Witten–Veneziano positivity, and the vanishing-susceptibility limit.

## Verified Physlib sources

| Source | Blob |
|---|---|
| `Physlib.lean` | `bf9028667305c70e77142e5fd24ec06fadb0d66f` |
| `PolyakovLoopDeconfinement.lean` | `3f5eb8945e367c49a4156cd7db598ec7818dad24` |
| `ChiralSymmetryBreakingCondensate.lean` | `f29e760dfc6f2b98149a9dd316f167482520920e` |
| `AxialAnomalyEtaPrimeMass.lean` | `bfbaf7766c5b6d8e9929b59166ffa15241465fdf` |

All three files carry satisfied ZIL physical-theorem contracts with explicit forbidden promotions.

## Executable identities

OpenWave checks:

- `L = zL` for nontrivial `z` only at `L = 0` in the finite complex carrier;
- `exp(-F_q/T)` grows with `T` and decreases with `F_q`;
- chiral rotations preserve `sigma^2 + pion^2`;
- `m_pi^2 = -2 m_q <qbar q>/f_pi^2` is positive for physical signs, linear in `m_q`, and zero at `m_q = 0`;
- `theta + 2 N_f alpha = 0` for `alpha = -theta/(2N_f)`;
- the shifted theta-vacuum phase is unity;
- `m_eta'^2 = 2 N_f chi_top/f_pi^2` is positive for positive susceptibility and zero when susceptibility vanishes.

## Boundaries

This milestone does not determine a numerical deconfinement temperature, construct a lattice measure,
calculate the condensate or topological susceptibility, derive the anomaly equation from a path integral,
or claim that the observed quark spectrum contains a massless quark. It also does not uniquely validate CAT/EPT.
