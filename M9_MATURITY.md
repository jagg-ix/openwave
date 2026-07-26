# OpenWave M9 maturity profile

The current assessment keeps formal theorem status, numerical closure, state construction, physical identity, calibration, prediction readiness, and implementation evidence separate.

## Headline summary

| Headline | Count |
| --- | ---: |
| Validated in scope | 7 |
| Conditional validated | 5 |
| Reduced-model validated | 3 |
| Calibration pending | 1 |
| Candidate | 4 |
| Negative | 1 |
| **Total** | **21** |

M9.109 changes the **formal interpretation** of Newton's constant without hardcoding a new headline or claiming a numerical prediction.

## Newton-G status

| Layer | Current result |
| --- | --- |
| Formal relation | `G = hbar*c/m_anchor^2 = c^5/(hbar*omega_anchor^2) = hbar*c*sigma0_anchor^4` |
| Primitive status | `G` is canonicalized as derived, not primitive |
| Mass value | not derived |
| Particle-clock universality | rejected by electron/muon/proton audit |
| Universal gravity anchor | open |
| Physical unit map | open |
| Withheld `G` prediction | not executed |
| Weak/nonlinear coupling injection | blocked until prediction and unit map close |

The Compton anchor removes a free clock-frequency knob once a mass is fixed. It does not explain the mass hierarchy or identify an ordinary particle clock with the universal gravity scale.

## Quantitative implication

Using 2022 CODATA masses:

```text
electron G_clock / G_measured  about 5.71e44
muon     G_clock / G_measured  about 1.34e40
proton   G_clock / G_measured  about 1.69e38
```

The Planck-mass/frequency control reproduces measured `G` because it is obtained by inversion from measured `G`; it is not an independent prediction.

## Promotion rule

Gravity calibration may advance only after an independently grounded universal-gravity mass or clock, with no dependency on withheld `G`, produces the same frozen coupling through every registered path and an explicit SI-to-OpenWave unit map.

Natural-unit closure is internal consistency, not external calibration.
