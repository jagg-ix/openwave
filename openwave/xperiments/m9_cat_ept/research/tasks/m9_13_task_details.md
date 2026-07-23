# M9.13 task: coupled three-dimensional Maxwell--Dirac transport

## Equations

Two opposite-charge four-spinors evolve by

```text
i psi_s,t = [alpha.(-i grad-s q A) + beta m] psi_s
s in {+1,-1}.
```

The temporal-gauge Maxwell sector is

```text
A_t = -E
E_t = curl B - J - sigma E
B = curl A
rho_abs,t = -div(sigma E).
```

Gauss law is audited as `div E = rho_matter + rho_abs` without projection.

## Frozen inputs

```text
m=1, q=0.15, packet width=1.8
offsets=(4,1.5,0.75)
momenta=(0.8,0.25,0.15)
gauge seed amplitude=0.004, width=3.5.
```

## Scored studies

- refinement: `10^3,20^3,40^3`, `t=0.5`;
- coupled run: `20^3`, `t=2.5`;
- domain shapes: `16x14x12`, `16x16x14`, `16x18x16`, `t=1.2`.

## Acceptance

Self-convergence at least `1.2`; norm drift `<=3e-6`; corrected-energy drift `<=3e-5`; final Gauss `<=5e-4` absolute and `<=0.25` relative; neutral charge; reduced separation; nonzero magnetic/radiation diagnostics; and stable domain ledgers.

## Selection transparency

An initial `48^3` study exceeded the reproducibility runtime budget. The scored grids and horizons were reduced before the committed run. The coarse relative Gauss value and near-zero domain emission remain visible.

## Boundary

M9.13 is a coarse bounded transport qualification, not a stable particle or asymptotic-constraint theorem.
