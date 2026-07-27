# M9.117 dynamical holographic coarse graining

M9.117 replaces the static interpretation of `N_H/N_C` with three executable, falsifiable scale-flow layers while preserving

```text
G_screen = (A/N_H)c^3/hbar.
```

## M9.117a — count and block flow

The continuous scale coordinate is

```text
s = log(m_P/m).
```

The declared flow is

```text
bits per coarse cell = exp(2s)
coarse cells         = N_H exp(-2s)
area per coarse cell = l_P^2 exp(2s).
```

Consequently the microscopic ratio remains

```text
(area per coarse cell)/(bits per coarse cell) = l_P^2
```

and the reconstructed `G` is invariant. At the species endpoint the multiplicity is `(m_P/m)^2` and the coarse-cell count equals `N_C`.

A finite periodic carrier applies an exact heat semigroup followed by adjacent-cell block sums. Total bit content, total area, local area per bit, and the induced coupling remain invariant. This supplies a coherent coarse-graining mechanism; it does not derive the particle mass selecting the endpoint.

## M9.117b — Gaussian covariance flow

A finite covariance tower realizes the Physlib pattern

```text
C_M = I_M^* C I_M
C_M = I_(M->2M)^* C_(2M) I_(M->2M).
```

Piecewise-constant injections are isometric, direct and nested projections agree, Gaussian Weyl pullbacks agree numerically, and heat transfer composes as a semigroup.

The principal coupling approaches one and the image couplings approach zero. This reproduces the formal free-field limit structure; it is not an interacting CAT/EPT fixed point.

## M9.117c — gravity across resolutions

One synthetic screen anchor is injected into the weak and nonlinear gravity configurations on odd grids `17^3`, `25^3`, and `33^3`. A low Fourier-mode source is transported spectrally. The following remain scale consistent:

- source norm;
- Poisson potential norm;
- field energy;
- trace-free tidal curvature norm.

Independent reconstruction produced:

```text
heat semigroup relative error        8.021613486287196e-17
principal-mode final error           5.208224840225206e-05
maximum final image coupling         1.5957342274844392e-05
maximum gravity Cauchy change        1.0409855411570073e-15
```

## Decision boundary

M9.117 establishes a consistent count flow, a free-Gaussian covariance adapter, and low-mode gravity scale consistency. It does not derive a particle mass, construct the interacting CAT/EPT renormalisation fixed point, calibrate the holographic screen, or prove general Einstein equivalence across scales.
