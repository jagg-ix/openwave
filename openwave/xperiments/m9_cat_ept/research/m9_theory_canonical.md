# M9 CAT/EPT canonical specification

## Back-reaction interfaces

M9.15 selects `d psi/dt=(-i H_R-Gamma)psi`; for `Gamma=gamma I` it establishes
`tau_ent=-1/2 log ||psi||^2` and `|W|=exp(-tau_ent)`.

M9.16 selects the trace-preserving channel
`d rho/dt=-i[H,rho]+gamma(sigma_z rho sigma_z-rho)`.

M9.17 selects spatial matter-to-reservoir transfer
`d psi_s/dt=-sigma_x d_x psi_s-i m sigma_z psi_s-(kappa g/2)psi_s`,
`d r_s/dt=kappa g |psi_s|^2`.

## Canonical decision

The interfaces predict different accessible trace, normalized purity, and
reservoir-transfer signatures. Their operational monotones are not a unique clock.

```text
unique_backreaction_selected=false
physical_time_identified=false.
```
