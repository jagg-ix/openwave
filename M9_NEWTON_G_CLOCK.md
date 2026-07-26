# M9.109 Newton-G clock anchor audit

## Re-evaluated formal result

Current Physlib proves the exact equivalence

```text
G = hbar*c/m_anchor^2
  = c^5/(hbar*omega_anchor^2)
  = hbar*c*sigma0_anchor^4
omega_anchor = m_anchor*c^2/hbar
```

It also canonicalizes `constant:newton-G` as derived rather than primitive. This removes a free `G` parameter only after a mass, clock frequency, or inference-width anchor is fixed. It does not derive the numerical mass scale.

## Universality implication

A particle's Compton clock cannot automatically be the universal gravitational clock. Electron, muon, and proton masses generate different effective values under `G = hbar*c/m^2`.

The default CODATA audit gives:

| Clock | `G_clock / G_measured` |
| --- | ---: |
| electron | about `5.71e44` |
| muon | about `1.34e40` |
| proton | about `1.69e38` |

The measured Newton coupling is recovered by the Planck-mass/Planck-frequency inversion control. That control uses measured `G`; it is an identity check, not a prediction.

## Current decision

- `G` formal status: **derived, conditional on an anchor**.
- arbitrary particle clock as universal gravity anchor: **rejected**.
- independent universal Planck-scale anchor: **open**.
- withheld numerical `G` prediction: **not executed**.
- calibrated injection into gravity campaigns: **blocked**.

## Reproduction

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_formal_G_authority.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_G_clock_universality.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_G_anchor_protocol.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_109_current_registration.py
```

## Promotion rule

A physical prediction of `G` requires one universal-gravity mass or frequency that is independently measured or derived without using `G`, plus an explicit SI-to-OpenWave unit map. The same frozen dimensionless coupling must then feed both weak and nonlinear gravity.

Natural-unit closure at `hbar = c = m = omega = sigma0 = G = 1` is not external calibration.
