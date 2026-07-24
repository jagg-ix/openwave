# OpenWave M9 CAT/EPT comparison profile

This file is the canonical **M9 extension column** for the shared OpenWave comparison rubric. The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`.

Platform validation and formal theorem status are deliberately separated. A scoped Lean theorem improves the evidence attached to a row, but it does not become an in-platform physical validation without the corresponding calibrated OpenWave result.

## Platform summary after M9.59

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 0 |
| ⚠️ partial / with caveats | 20 |
| ❌ honest negative | 1 |
| 🚧 planned / not yet | 0 |
| **Explicit criteria** | **21** |

## Particles

| Criterion | Status |
| --- | --- |
| Charge quantization | ⚠️ Integer winding; electric identity open |
| Electron rest energy | ⚠️ Interior dimensionless scale; physical mass open |
| de Broglie clock | ⚠️ Clock channels separated; physical-time identity open |
| Particle stability | ⚠️ M9.49/M9.52 disperse for the original action; M9.59 adds an explicit bounded cubic--quintic action term and retains an untrapped candidate across three grids. Orbital stability, continuum existence, uniqueness of the term, and physical calibration remain open. |
| Magnetic moment and spin | ⚠️ Pauli-current field control; emergent calibrated g factor open |
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
| Gravity | ⚠️ OpenWave has weak-field and equivalence-principle controls. PhysLib also has scoped metric-built Einstein--Maxwell--entropic action/PDE interfaces, global Einstein--Hilbert integration, ADM constraint propagation, and conditional maximal-development infrastructure. Concrete calibrated coupled evolution remains open. |

## Waves and quantum emergence

| Criterion | Status |
| --- | --- |
| EM waves | ⚠️ Transverse Maxwell reduction and massless bridge; scoped intrinsic/distributional formal Maxwell interfaces exist, but common calibrated Cauchy data remain open |
| Klein-Gordon | ⚠️ Massive dispersion-qualified reduction; native particle open |
| Orbital quantization | ⚠️ Converged radial bound-mode ladder; native atom open |

## Thermal sector

| Criterion | Status |
| --- | --- |
| Heat / thermal-field sector | ⚠️ Conserved heat, entropy growth, and diffusion-dissipation control |

## Formal interface summary

| Formal layer | Status |
| --- | --- |
| Metric-built Einstein--Maxwell--entropic field-equation constructors | proved with explicit scope |
| Global Einstein--Hilbert action and dominated Palatini derivative | proved with explicit scope |
| Global electrogravitic action derivative interface | proved with explicit scope |
| Intrinsic curved Maxwell equation and atlas independence | directly proved |
| ADM constraint propagation and global flow | conditional on explicit vector-field/Lipschitz/tangency data |
| Maximal-development gluing | conditional on fixed-Cauchy extension and smooth quotient data |
| Full CAT/EPT continuum generator and quantum dynamical semigroup | not closed end-to-end |
| Continuum kinetic hypoelliptic theorem | not closed end-to-end |

All 21 platform criteria have evidence. None is fully validated. The remaining negative is the predictive lepton-mass hierarchy. M9.59 replaces the former bounded particle-stability negative with a bounded partial result; it does not establish a physical particle.
