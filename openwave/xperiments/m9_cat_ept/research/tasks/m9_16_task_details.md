# M9.16 task: Lindblad information-loss qualification

## Question

Can a trace-preserving information-loss channel be qualified independently of
M9.15's trace-decreasing amplitude weight?

## Selected channel

```text
d rho/dt = -i[H,rho] + gamma(sigma_z rho sigma_z-rho)
H = omega sigma_z/2
omega=1.1, gamma=0.23.
```

## Gates

- fourth-order convergence;
- trace, Hermiticity, positivity, and populations preserved;
- purity and relative coherence monotone;
- zero-dephasing unitary reduction;
- explicit distinction from amplitude loss.

## Boundary

The channel is a selected dephasing model. It is not identified with the CAT/EPT
imaginary action and does not identify a unique information clock.
