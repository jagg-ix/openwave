# OpenWave M9.103--M9.105 scientific closure campaigns

## Authorities

```text
OpenWave main  ca40b8648fcb02c23e56951f08c9988c24e763ab
Physlib        eba0124fcfbc1216d973bb6f504c5a6d324de60c
zil-lean       e09723a44185a1e70031ad2661c8009dc98bef74
```

Physlib's physics surfaces are unchanged from M9.102. `zil-lean` adds the Make-driven example/report runner while retaining the same `Zil` and `Zil.Native` root blobs.

## M9.103 -- unrestricted charged state

The M9.101 action solver projected to spin-up winding three after every descent step. M9.103 projects only during initialization. The full two-component field then evolves without a winding or spin projection.

The campaign reports independently:

- full stationary residual;
- measured winding;
- lower-spin-component fraction;
- action monotonicity;
- cross-seed distance;
- Maxwell constraints;
- spin-tilt, quadrupole and phase-chirp real-time tubes.

`passed=true` means the executable audit ran. State existence is controlled by `unrestricted_stationary_state_constructed` and `unrestricted_orbital_stability_qualified`.

## M9.104 -- refined packet spin

The regular lab-frame Thomas--BMT equation is registered as an explicit external postulate. It is not relabeled as a QED derivation.

The local packet torque and finite-time Maxwell--Dirac spin rate are compared to the exact initial Dirac generator on:

```text
16^3 and 20^3 grids
0.004 and 0.002 time steps
```

The refined gate requires the finest packet error to close and the error not to worsen beyond the declared slack under time refinement.

## M9.105 -- independent calibration

The calibration graph audits five required independent anchors:

- inference width `sigma0`;
- clock frequency;
- mass;
- charge unit;
- force unit.

The current defaults remain internal, derived, or absent. Therefore independent calibration remains false and the three preregistered predictions remain unexecuted. An external bundle is accepted only when every required anchor has independent evidence, no target-dependent fit, no missing dependency and no dependency cycle.

## Run

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_103_unrestricted_charged_stationary.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_104_packet_tbmt_refinement.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_105_independent_calibration.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_105_current_registration.py
```

ZIL graph checks after installing current `zil-lean`:

```bash
bin/zil expand openwave/xperiments/m9_cat_ept/research/zil/m9_103_105_scientific_closure.zc -
bin/zil trace openwave/xperiments/m9_cat_ept/research/zil/m9_103_105_scientific_closure.zc -
bin/zil query-ci openwave/xperiments/m9_cat_ept/research/zil/m9_103_105_scientific_closure.zc
```

## Claim boundary

These campaigns do not predetermine a successful state, packet reduction, calibration, particle identity, anomalous moment, physical unit map, or external prediction. Their purpose is to make each result executable and falsifiable.
