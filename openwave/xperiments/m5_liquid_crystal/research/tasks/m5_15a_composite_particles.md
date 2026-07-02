# 15a — Composite Particles

**Parallel research stage** — DEFERRED. Layers 3–5 are major undertakings; sub-stages sketched here for forward visibility but NOT on the critical path. Pursued once foundations exist.

> Pursued only if foundations succeed and resources permit. Hopfions, knots → nuclei. Liu et al. 2026 lab anchor (`project_particle_defect_correspondence` memory).

| Sub-phase | Layer | Headline |
| --- | --- | --- |
| **15a.1 / Nucleon assembly** | Layer 3 | Seed 3-string Y-configuration with color-neutral axis assignment; verify proton/neutron forms a stable bound state with mass dominated by string energy |
| **15a.2 / Color confinement test** | Layer 3 | Attempt to separate one quark from a 3-quark configuration; verify string tension prevents isolation (linear energy growth) |
| **15a.3 / Nuclear binding** | Layer 4 | Two-nucleon and few-nucleon bound states; measure residual strong force; reproduce binding-energy curve |
| **15a.4 / Atomic orbitals** | Layer 5 | Single electron orbiting a nucleus; verify discrete orbital shells emerge from standing-wave interference at atomic scales |
| **15a.5 / Multi-electron atom** | Layer 5 | Z electrons in a single-nucleus configuration; verify shell structure (Pauli-like exclusion via wave interference + topology) |

## Cross-mass-class machinery required for 15a.4+ (per [3c § How different-frequency Zitterbewegung emissions interfere](m5_1b_topological_defect.md#how-different-frequency-zitterbewegung-emissions-interferehydrogen-vs-positronium))

Atom-scale simulations (15a.4 onward) need additional architectural capability beyond the same-mass-class physics validated by M5.7–M5.8. The reason: in hydrogen-like systems, the proton ticks at `ω_p ≈ 1836 × ω_e`, so direct e-p Zitterbewegung interference does NOT form coherent standing waves. Instead, three layered mechanisms must work together:

- [ ] **Topological 1/d Coulomb** between e (Q=−1) and p (effective Q=+1) — provides the static potential well (already validated in M5.1)
- [ ] **Electron self-de-Broglie standing waves** — the electron's Zitterbewegung (ω_e at 10²¹ rad/s) + translational drift produces de Broglie wavelength `λ_dB = h/(m_e v)`. Standing waves of the electron's *own* emission (interfering with reflections off the central proton's potential well) quantize discrete Bohr orbital shells at `n·λ_dB = 2π·r_n`
- [ ] **Quasi-static heavy-center treatment** for the proton — because m_p ≫ m_e, the proton's intrinsic clock (10²⁴ rad/s) is invisible to the electron's slower 10²¹ rad/s response and time-averages out. 15a.4's solver must treat the proton as a fixed Coulomb center on the electron's time scale (with proton dynamics on its own slower scale only when needed)

This is structurally different from the same-mass cases: positronium (M5.7+) and quark-quark binding (M5.9) DO use direct Zitterbewegung interference; hydrogen-like atoms (15a.4) cannot. The transition criterion is `ω_a ≈ ω_b` (frequency-matched, direct interference works) vs `|ω_a − ω_b| ≫ min(ω_a, ω_b)` (frequency-mismatched, requires the three-mechanism layering above).

This testing-architecture distinction is **gating** for atom-scale simulations: 15a.4 cannot succeed by simply scaling up the same-mass mechanism. The cross-mass machinery is a separate effort.

## Field configurations from Duda's 2026-07-01 sketch (concrete targets for 15a.1–15a.3)

Duda's group-thread sketch ([`m5_4f_convo_2026.07.01.md`](m5_4f_convo_2026.07.01.md) § 2; figure [`../../theory/duda_2026-07-01_particle_field_configs.png`](../../theory/duda_2026-07-01_particle_field_configs.png)) spells out the composite field configurations, turning the sub-phase headlines above into concrete, falsifiable seeds. His item-12 argument: topological vortices form **knots** whose interaction enforces inward/outward field rotations = (fractional) charges.

| 15a sub-phase | Duda's field-configuration prescription | Falsifiable target |
| --- | --- | --- |
| **15a.1 nucleon assembly** | **Baryon = a vortex loop around a vortex**, the strands interacting as internal **twists (half-rotations)**. **Proton = the charge enclosed into a hedgehog** (elementary charge, the cheap config). **Neutron = must compensate** the charge (a costlier config), which is **why the neutron is heavier** | reproduce `m_n > m_p` from the compensating-vs-hedgehog energy gap (sign + rough scale), not by hand |
| **15a.2 color confinement** | **Quarks = fractional-charge excitations** set by an **inward/outward field rotation** of the knotted vortex (a fraction-of-π rotation; full π = elementary charge). Confinement = the gluon flux tube / quark string; violating charge quantization costs asymptotically linear energy (`σ ≈ 1 GeV/fm`) | the `±π/3` fractional charges + linear confinement from the string, consistent with the M5.9 Cornell result (#200) |
| **15a.3 nuclear binding (deuteron)** | **Deuteron = two baryons** satisfying the charge preference better than a single charge, producing the experimentally known **'+ − +' electric quadrupole moment** (Garçon charge densities on the slide) | reproduce the **sign structure** of the deuteron electric quadrupole ('+ − +'), a sharp, measured nuclear falsifier |
| **15a.3 (α particle)** | a larger multi-vortex hub/knot | bound 4-nucleon config; binding-energy scale |
| **mesons (adjacent)** | **Vortex reconnection**: kaon / hyperon Ξ, pion / hyperon Λ; **strangeness** as an extra internal twist | pion/kaon as reconnection intermediates; the β-decay `n → W⁻ → p + e + ν̄` is the same reconnection family |

The **deuteron '+ − +' quadrupole** is the standout near-term target here: it is a specific, measured number that the two-baryon charge-compensation picture predicts *structurally*, so it is a clean go/no-go for the composite program independent of absolute-mass calibration.
