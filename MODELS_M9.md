# OpenWave M9 CAT/EPT comparison profile

This is the script-backed M9 conformance profile. The canonical source is
`openwave/xperiments/m9_cat_ept/model_conformance.py`.

## Summary

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 0 |
| ⚠️ partial / with caveats | 15 |
| ❌ honest negative | 2 |
| 🚧 planned / not yet | 3 |
| **Explicit criteria** | **20** |

`MODELS.md` reports 21 criteria while the visible matrix contains 20 rows. The
missing explicit target remains **heat / thermal sector**.

## Particles

| Criterion | Status |
| --- | --- |
| Charge quantization | ⚠️ Integer field winding; electric identity open |
| Electron rest energy | ⚠️ Interior dimensionless scale; physical mass open |
| de Broglie clock | ⚠️ Clock channels separated; physical-time identity open |
| Particle stability | ❌ Trapped 3D minimizer and 1D family exist; no self-bound stable 3D candidate |
| Magnetic moment and spin | ⚠️ Pauli-current field control; emergent g factor open |
| Spin-1/2 statistics | ⚠️ 2π sign reversal and 4π return; exchange open |
| Antimatter and annihilation | ⚠️ Reduced capture/annihilation/radiation ledger; full PDE open |
| Lepton mass spectrum | ❌ Current simple hierarchy laws fail prediction |
| Dark matter candidate | 🚧 Not yet |
| Quarks | 🚧 No dynamical color/quark sector yet |
| Baryons | ⚠️ Charged-triplet graph control; physical baryon open |
| Mesons | ⚠️ Neutral-pair graph control; physical meson open |

## Forces

| Criterion | Status |
| --- | --- |
| Electric force | ⚠️ Regularized r^-2 kernel; stable-particle interaction open |
| Magnetic force | ⚠️ Regularized r^-4 dipole kernel; particle interaction open |
| Strong force | ⚠️ Cornell/flux-tube and string-breaking control; QCD open |
| Weak force | ⚠️ Left-selective transition/decay control; electroweak theory open |
| Gravity | ⚠️ Weak-field metric, universality, redshift, tidal, and accelerated-frame controls; GR open |

## Waves and quantum emergence

| Criterion | Status |
| --- | --- |
| EM waves | ⚠️ Maxwell propagation control |
| Klein-Gordon | 🚧 Not yet |
| Orbital quantization | ⚠️ Converged radial bound-mode ladder; native CAT/EPT atom open |

Partial status records bounded simulation evidence, not a completed physical
derivation. The two honest negatives remain self-bound 3D stability and the
current lepton-hierarchy candidate laws. QCD, electroweak theory, and general
relativity are not established by the reduced controls.
