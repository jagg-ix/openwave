# M9 input, calibration, and prediction ledger

## M9.12--M9.13 selected inputs

| Choice | Value | Classification |
| --- | --- | --- |
| Mass and charge | `m=1`, `q=0.15` | Dimensionless inputs |
| Packet width | `1.8` | Frozen localization input |
| Offsets | `(4,1.5,0.75)` | Frozen 3D collision |
| Momenta | `(0.8,0.25,0.15)` plus asymmetric opposite packet | Frozen transport |
| Gauge seed | amplitude `0.004`, width `3.5` | Magnetic perturbation |
| Numerics | centered differences, RK4, conductivity absorber | Numerical/boundary choice |
| Scored grids | refinement `10^3,20^3,40^3`; long `20^3` | Runtime-bounded qualification |

The relative Gauss threshold and reduced grids were fixed after exploratory runs. No physical charge or particle identity is inferred.
