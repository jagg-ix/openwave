# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** M9.1--M9.5 establish a source-pinned CAT/EPT interface,
> certified free control, explicit coarse-graining clock, stable neutral 1+1D
> bright-soliton family, and exact scaling ledger. M9.6 now closes the current
> scalar carrier honestly: it has no signed gauge charge or intrinsic spin-1/2.
> A staged Pauli/Dirac plus local U(1) replacement contract is specified.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Formal source | `entropic-physlib-linear-full@f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| Current carrier | One-component nonrelativistic complex scalar NLS |
| Replacement target | Four-component Dirac spinor with local U(1), followed by a separately gated nonlinear localization model |

## Current model

| Attribute | Status |
| --- | --- |
| Localized family | `eta=gN/2`, `psi=eta/sqrt(g) sech(eta x) exp(i eta^2 t/2)` |
| Reference candidate | `g=2`, `N=1`, phase frequency `1/2`, energy `-1/6`, RMS radius `pi/(2sqrt(3))` |
| Entropic clock | KL information discarded by one fixed doubly stochastic channel; channel depth is not physical time |
| Phase clock | Dimensionless; Compton and ZBW radius ratios are conditional unit-map identities |
| Charge | No local gauge connection, Gauss-law flux, or opposite-charge sector |
| Spin | Intrinsic scalar `2pi` action is `+1`; no spin-1/2 double-cover representation |
| Topology | The localized profile contracts to the zero vacuum through `H_s=(1-s)psi`; no protected winding is present |
| Dimensional scope | Exact and numerically verified in 1+1 dimensions only |
| Physical identity | Neutral mathematical soliton; no Standard Model species or mass prediction |

## Executable M9.6 findings

- global phase leaves density, norm, and energy invariant;
- conjugation leaves density, norm, and energy invariant while reversing current;
- the nonnegative scalar norm therefore is not a signed electric charge;
- the state contracts continuously to zero;
- scalar `2pi=+1`, while the spin-1/2 reference has `2pi=-1`, `4pi=+1`;
- all 15 audit checks pass.

## Replacement carrier contract

| Stage | Carrier | What it settles |
| --- | --- | --- |
| M9.6A | Pauli spinor + local U(1) | Nonrelativistic spin and gauge coupling |
| M9.6B | Dirac spinor + local U(1) | Spinorial `2pi` sign and opposite-charge sectors |
| M9.6C | Nonlinear localized Dirac-gauge model | Charged spin-1/2 candidate only after 3D numerical gates |

The replacement preserves the positive density `psi-dagger psi`, complex
action/phase carrier, current, and field-to-probability interface required by the
CAT/EPT clock. It is a specification, not an implemented particle.

## Implementation status

| Target | Status |
| --- | --- |
| M9.1 formal contract | Complete |
| M9.2 free solver | Complete |
| M9.3 coarse-graining clock | Complete |
| M9.4 localized scalar candidate | Complete |
| M9.5 exact scaling family | Complete |
| M9.6 scalar no-go and replacement contract | Complete |
| 3D charged spinor dynamics | Not implemented; next major program |
| Interactive launcher | Deferred until validated 3D dynamics exists |

## Help wanted

Useful contributions are a Pauli/Dirac carrier implementation reusing Physlib,
a gauge-covariant CAT/EPT probability/current bridge, or a preregistered 3D
localization model with virial, radiation, window, and perturbation gates.
