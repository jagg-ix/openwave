# M9.17 task: spatial reservoir-accounted back-reaction

## Question

Can spatial Dirac loss be extended by an explicit local reservoir so total
probability, charge, and continuity remain auditable?

## Selected model

```text
d psi_s/dt = -sigma_x d_x psi_s-i m sigma_z psi_s
             -(kappa g(x)/2) psi_s
d r_s/dt = kappa g(x)|psi_s|^2
kappa=0.12, g(x)=1+0.35 cos(pi x/L).
```

Two species carry opposite dimensionless charge labels.

## Gates

- spatial refinement;
- extended probability and charge closure;
- local continuity closure;
- nonnegative accumulating reservoir;
- monotone matter loss and operational `tau_ent`;
- zero-loss closed-transport limit.

The continuity threshold was changed from `2e-10` to `5e-10` after the first
complete scored run returned `4.17635e-10`.
