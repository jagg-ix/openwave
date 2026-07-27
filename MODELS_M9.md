# OpenWave M9 CAT/EPT comparison profile

The canonical conformance profile is `model_conformance_m109.py`, schema v22. The canonical registration is `model_registration_m109.py`, schema v13.

## Authorities

```text
OpenWave base  bd0367fc73f2ffac2a033576bce94e51972bad8c
Physlib        398ba1976ce7602e30ed05ecbd0f228027335584
zil-lean       e09723a44185a1e70031ad2661c8009dc98bef74
```

## M9.109a — formal G authority

Current Physlib anchors the entropic clock to the Compton frequency and proves:

```text
hbar*omega0 = m*c^2
G = hbar*c/m^2
G = c^5/(hbar*omega0^2)
G = hbar*c*sigma0^4
```

The source and graph audit make `constant:newton-G` a canonical derived quantity. The same source explicitly retains that the mass value and three-origin mass coincidence are conditional.

## M9.109b — species universality audit

`newton_g_clock_universality.py` evaluates electron, muon, and proton Compton clocks against measured Newton `G`. The mass and clock forms agree algebraically for every species, but their effective couplings differ by millions between species and by 38--45 orders of magnitude from measured `G`.

Decision:

```text
formal equivalence                         preserved
ordinary particle clock = gravity anchor   false
one universal Planck-scale anchor required true
Planck inversion control = prediction      false
```

## M9.109c — anchor and gravity coupling protocol

`newton_g_anchor_protocol.py` rejects:

- particle-scoped clocks;
- anchors derived by inverting measured `G`;
- target-fitted anchors;
- natural-unit `G=1` as physical evidence.

`newton_g_gravity_adapter.py` requires an explicit unit conversion

```text
G_dimensionless = G_SI * mass_unit * time_unit^2 / length_unit^3
```

and derives the numerical inference width only after calibration. One frozen dimensionless coupling must feed both weak-field and nonlinear gravity.

The current default has no independent universal anchor, so no external prediction or calibrated injection is executed.

## Reproduction

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_formal_G_authority.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_G_clock_universality.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_G_anchor_protocol.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_current_registration.py
```

Committed result records:

```text
research/results/m9_109_newton_g_clock_universality.json
research/results/m9_109_newton_g_anchor_protocol.json
```

## Boundaries

- a derived relation is not a numerical prediction;
- an ordinary particle clock is not automatically a universal gravity clock;
- a Planck scale calculated from measured `G` is not independent evidence;
- a natural-unit coupling is not an SI calibration;
- a calibrated `G` still does not make the reduced conformal metric a general Einstein solver.
