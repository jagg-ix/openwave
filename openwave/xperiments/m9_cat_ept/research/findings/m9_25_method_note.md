# M9.25 finding: constrained 1D localization is partial

The normalized complex-time focusing field admits a finite-norm sech family.
The static residual converges at orders `1.979635`
and `1.994862`.

For the scored `kappa=0.8` member:

```text
long-horizon RMS/reference   = 1.001945636324
long-horizon peak/reference  = 1.008165253526
long-horizon core fraction   = 0.999364077651
long-horizon tail fraction   = 7.074806e-05
norm error                   = 0.000e+00
```

The family is continuous in `kappa`; its scale is fixed by the conserved norm,
not selected dynamically. A one-dimensional localized family is accepted, but
`accepted_three_dimensional_particle=false`.

Focused validation: `8 passed`. No CI workflow was run or inspected.
