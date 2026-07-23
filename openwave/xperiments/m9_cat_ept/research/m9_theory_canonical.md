# M9 CAT/EPT canonical specification

## M9.12 controls

The four-component Dirac representation and free/vacuum controls pass.

## M9.13 coupled 3D reduction

```text
i psi_s,t = [alpha.(-i grad-s q A)+beta m]psi_s
A_t=-E
E_t=curl B-J-sigma E
B=curl A
rho_abs,t=-div(sigma E).
```

The bounded run passes refinement, norm, corrected energy, final absolute/relative Gauss, charge, transport, magnetic, radiation, and domain gates. The relative Gauss defect `0.190060` is retained as a coarse-grid limitation.
