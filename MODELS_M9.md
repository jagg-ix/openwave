# OpenWave M9 CAT/EPT comparison profile

The canonical source is `openwave/xperiments/m9_cat_ept/model_conformance.py`.

## Summary

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 0 |
| ⚠️ partial / with caveats | 19 |
| ❌ honest negative | 2 |
| 🚧 planned / not yet | 0 |
| **Explicit criteria** | **21** |

## Particles

| Criterion | Status |
| --- | --- |
| Charge quantization | ⚠️ Integer winding; electric identity open |
| Electron rest energy | ⚠️ Interior dimensionless scale; physical mass open |
| de Broglie clock | ⚠️ Clock channels separated; physical-time identity open |
| Particle stability | ❌ Trapped states remain bounded, but merged untrapped and Gaussian, exponential, super-Gaussian, shell, and vortex/toroidal scans spread or reach box scale |
| Magnetic moment and spin | ⚠️ Pauli-current field control; emergent g factor open |
| Spin-1/2 statistics | ⚠️ 2π sign reversal and 4π return; exchange open |
| Antimatter and annihilation | ⚠️ Reduced capture/annihilation/radiation ledger; full PDE open |
| Lepton mass spectrum | ❌ Current low-parameter hierarchy laws fail predictive gates |
| Dark matter candidate | ⚠️ Neutral fixed-charge variational candidate; full PDE and phenomenology open |
| Quarks | ⚠️ Finite SU(3), singlet, Wilson-loop, fractional-charge, and CKM controls; QCD open |
| Baryons | ⚠️ Charged-triplet graph control; physical baryon open |
| Mesons | ⚠️ Neutral-pair graph control; physical meson open |

## Forces

| Criterion | Status |
| --- | --- |
| Electric force | ⚠️ Regularized r^-2 kernel; stable-particle interaction open |
| Magnetic force | ⚠️ Regularized r^-4 dipole kernel; particle interaction open |
| Strong force | ⚠️ Cornell/flux-tube and string-breaking control; QCD open |
| Weak force | ⚠️ Left-selective transition/decay control; electroweak theory open |
| Gravity | ⚠️ Weak-field metric and equivalence-principle controls; GR open |

## Waves and quantum emergence

| Criterion | Status |
| --- | --- |
| EM waves | ⚠️ Transverse Maxwell reduction and massless scalar bridge |
| Klein-Gordon | ⚠️ Massive dispersion-qualified reduction; native particle open |
| Orbital quantization | ⚠️ Converged radial bound-mode ladder; native atom open |

## Thermal sector

| Criterion | Status |
| --- | --- |
| Heat / thermal-field sector | ⚠️ Conserved heat, entropy growth, and diffusion-dissipation control |

All 21 criteria have evidence. None is fully validated. The M9.49 and M9.52 negatives are finite-grid and family-bounded, not universal no-go theorems.
