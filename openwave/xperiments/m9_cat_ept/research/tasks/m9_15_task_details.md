# M9.15 task: imaginary-action amplitude-loss qualification

## Question

Can the CAT/EPT relation `|W|=exp(-tau_ent)` be represented by one explicit,
positive, non-Hermitian control without treating that control as established
physics?

## Selected control

```text
d psi/dt = (-i H_R-Gamma) psi.
```

The scored identity gate uses `Gamma=gamma I`, `gamma=0.17`, and

```text
tau_ent = -1/2 log ||psi||^2.
```

A second positive diagonal `Gamma=diag(0.08,0.22)` checks contractivity and
normalized-observable distortion.

## Gates

- positive loss generator;
- fourth-order RK4 convergence;
- monotone norm and `tau_ent`;
- exact imaginary-action and weight-modulus identities;
- zero-loss unitary reduction;
- positive nonuniform contraction.

## Boundary

This is a selected two-level non-Hermitian control. It does not derive `gamma`,
identify physical time, or define a trace-preserving open system.
