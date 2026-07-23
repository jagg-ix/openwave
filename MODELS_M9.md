# OpenWave M9 CAT/EPT comparison profile

This is the script-backed M9 conformance profile for the shared OpenWave criteria.
The canonical source is `openwave/xperiments/m9_cat_ept/model_conformance.py`.

## Summary

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 0 |
| ⚠️ partial / with caveats | 4 |
| ❌ honest negative | 1 |
| 🚧 planned / not yet | 15 |
| **Explicit criteria** | **20** |

`MODELS.md` reports 21 criteria while the visible matrix contains 20 rows: 12
particle, 5 force, and 3 waves/quantum-emergence. M9 records the missing explicit
target as **heat / thermal sector** rather than silently inventing a status cell.

## Current M9 coverage

### Particles

| Criterion | Status |
| --- | --- |
| Charge quantization | 🚧 Not yet |
| Electron rest energy | 🚧 Not yet |
| de Broglie clock | ⚠️ Entropic clock implemented; ZBW/physical-time identity not established |
| Particle stability | ❌ No stable 3D candidate accepted |
| Magnetic moment and spin | 🚧 Not yet |
| Spin-1/2 statistics | 🚧 Not yet |
| Antimatter and annihilation | 🚧 Not yet |
| Lepton mass spectrum | 🚧 Not yet |
| Dark matter candidate | 🚧 Not yet |
| Quarks | 🚧 Not yet |
| Baryons | 🚧 Not yet |
| Mesons | 🚧 Not yet |

### Forces

| Criterion | Status |
| --- | --- |
| Electric force | ⚠️ Maxwell/Gauss transport exists; no force law between stable emergent charges |
| Magnetic force | ⚠️ Magnetic/Poynting fields exist; no particle-level interaction |
| Strong force | 🚧 Not yet |
| Weak force | 🚧 Not yet |
| Gravity | 🚧 Geometry manifest exists; dynamical metric back-reaction pending |

### Waves and quantum emergence

| Criterion | Status |
| --- | --- |
| EM waves | ⚠️ Vacuum Maxwell propagation qualified as a control, not an emergent derivation |
| Klein-Gordon | 🚧 Not yet |
| Orbital quantization | 🚧 Not yet |

## Boundary

A partial status means relevant simulation infrastructure exists. It does not mean
the phenomenon has been derived. M9 currently accepts no stable 3D particle, no
unique back-reaction mechanism, and no physical-time identity.
