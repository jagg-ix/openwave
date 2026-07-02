# M5.10: Effective Dirac description (toward a SM effective Lagrangian)

> Task **M5.10** (M5 / Liquid-Crystal model). Status: **Backlog** · Gated by: M5.9 · Roadmap: [`m5_roadmap.md`](../m5_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation.

---

## Current detail (from the roadmap, 2026-07-02 migration)

_No prior roadmap row; scoped entirely by GitHub #197 (migrated below)._

---

## GitHub issue archive (#197)

> Migrated from OpenWave GitHub issue [#197](https://github.com/openwave-labs/openwave/issues/197) on 2026-07-02 (M5 tracking moving to this local roadmap). Title: "Effective Dirac description of the M5 defect (toward a Standard-Model effective Lagrangian)". State at migration: OPEN. Labels: none.

### Issue body

## Goal

Show that the M5 liquid-crystal defect reduces to an **effective Dirac equation**, as the first concrete step toward an effective-Lagrangian description of the deep model that is close to the Standard Model.

The best experimentally confirmed theory is the Standard Model, so the deep nonperturbative LdGS model's effective (coarse-grained) description should land near the Standard-Model Lagrangian. The Dirac equation is the natural first target: it encodes a point object's spin direction and boost, and it enforces Zitterbewegung, the `E = mc²` clock carried in the phase `ψ ~ exp(−iEt/ℏ)`. The point-with-probability-density is the effective layer; Klein-Gordon-like phase evolution then appears near particles automatically (Dirac² = KG).

## Why this is mostly synthesis, not new discovery

The individual Dirac ingredients are **already validated** in the M5 program. The work is assembling them into one effective object and deriving the equation of motion, not finding new physics.

| Dirac feature | M5 status |
| --- | --- |
| Zitterbewegung, `E = mc²`, `ω = 2mc²/ℏ` | ✅ M5.8 molten clock; the apolar `ω_M = 2 ω_clock` factor of 2 is the ZBW doubling |
| Spin-½ (720° double cover) | ✅ M5.8 apolar π-symmetry, machine-exact |
| Spin as Noether clock charge | ✅ EID-C (`L_int`) |
| Klein-Gordon (each spinor component) | ✅ M5.6 geometric-mass KG emergence (Dirac² = KG) |
| Boost / Lorentz covariance | ⚠️ GEM boost sector measured; covariance of the defect not yet shown |
| 4-component bispinor mapping | 🚧 open, this is the synthesis |

## Proposed tiers (pick the depth)

| Tier | Scope | Effort |
| --- | --- | --- |
| **T1 — synthesis (tractable)** | Map the M5 defect DOF (clock phase, spin axis, particle/antiparticle = charge sign, boost) onto a 4-component Dirac bispinor; write the one-page dictionary; confirm the four validated Dirac signatures co-occur on ONE defect run (a single confirming script reading existing observables). Deliver a `MODELS.md` "effective Dirac description" note + the dictionary. | Small-medium (days); mostly assembling validated pieces, ~1 confirming script |
| **T2 — EOM derivation (theory-heavy)** | Show the Dirac equation emerges as the effective EOM: the γ-matrix Clifford algebra from the M5 4×4 frame / SO(3,1) structure, and the coarse-grained reduction LdGS field → point-particle `ψ` with `(iγ^μ ∂_μ − m)ψ = 0`. Numerically verify the dispersion `E² = p² + m²` and the ZBW interference of the ±E components. | Large (weeks); real derivation + Lorentz-covariance runs (closes the boost-covariance gap above) |
| **T3 — toward the SM Lagrangian (long-horizon)** | Extend the effective description toward gauge structure (EM is already in M5; weak/strong are the open M5.9 / Cornell sector plus the SU(3) neutrino/quark threads). A research program, not a single task. | Program (months+); gated on M5.9 |

## Recommended entry point

**T1 alone is a high-value, well-bounded deliverable.** It produces the "M5 → effective Dirac" dictionary using only already-validated results, and it decides whether T2 is worth pursuing. No hard gates (the pieces exist); benefits from unit calibration for the absolute `E = mc²`.

Physics-only, headless. Help welcome on any tier; T1 is the best first contribution.

---

*Motivation raised by Jarek Duda (Models of Particles group).*


---

## SUPPORTING RESULT — the de Broglie clock E(ω) energy minimum (2026-06)

The clock-energy comparison against Jarek Duda's 1+1D toy model is done and informs the **Boost / Lorentz covariance** row above:

- Activating the clock lowers the seed rest energy to a minimum **~21% below** the clock-stopped value ([`m5_8_2u_clock_energy_minimum.py`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/sandbox_vn/m5_8_2u_clock_energy_minimum.py)), and the settled clock relaxes to the toy model's **de Broglie frequency** (settled ω ≈ 1.1-1.2 vs the toy's ~1.07-1.29).
- **Key 3+1D difference**: imposing the frequency directly gives a **monotonic** E(ω) (forcing a higher frequency only costs energy). The energy minimum lives in the **static boost / GEM dressing** (the negative boost-sector kinetic term), not in a well along the frequency axis as in the 1+1D model. So the de Broglie endpoint is preserved; the route to it (minimize over the dressing) is the field-theoretic difference, and it is the boost-sector physics the T2 Lorentz-covariance work builds on.
- The absolute `E = mc²` (a physical-scale number rather than a ratio) awaits the units → physical-scale calibration (#208).


---

## DUDA INPUT + REFERENCE (2026-06-17)

- The de Broglie / electron clock has an experimental handle: a measurement with a **0.28% disagreement** — https://link.springer.com/article/10.1007/s10701-008-9225-1 (a calibration / cross-check target for the clock `ω = mc²/ℏ` once the unit map is fixed, see #208).
- A testable-consequence idea (Duda, thinking aloud): **two particles passing nearby could briefly modify each other's clock frequencies.** Open question what signature to search for in the data, but a candidate clock-clock observable worth keeping in view.

---

## DETAIL PLAN (T1, the effective-Dirac dictionary) (2026-06-17)

Scoped to **T1 only** (the tractable synthesis recommended above); T2 / T3 stay as the issue describes. T1 assembles already-validated M5 results into one effective Dirac object plus one confirming script. No new physics.

### The dictionary (the deliverable core): M5 defect DOF → Dirac bispinor

| Dirac structure | M5 observable (already validated) | Source script |
| --- | --- | --- |
| Clock phase `ψ ~ exp(−iEt/ℏ)`, ZBW at `ω = 2mc²/ℏ` | the de Broglie clock; the apolar doubling `ω_M = 2ω_clock` | `m5_8_2h_omega_attractor.py` (M5.8) |
| Spin-½ (720° double cover) | apolar π-symmetry `M(φ+π)=M(φ)`, machine-exact | `m5_8_2s_spin_half_apolar.py` (M5.8) |
| Spin as Noether clock charge | `L_int` (EID-C) | `m5_8_2r_electron_id.py` |
| Particle vs antiparticle (upper / lower components) | charge sign `Q = ±1` (topological winding) | `m5_8_1_topo_charge.py` |
| Each spinor component obeys KG (`Dirac² = KG`) | geometric-mass KG emergence | `m5_6_1_kg_operator_check.py` (M5.6) |
| Boost / bispinor mixing | the GEM boost-tilt of the 4×4 (covariance itself = T2, noted not closed) | `m5_8_2q_delta_scaling.py` |

### Phases

| Phase | Work | Output |
| --- | --- | --- |
| 1: the dictionary | Write the mapping table above into prose: each Dirac DOF mapped to its M5 field-theoretic realization, with the validated-result citation | the `MODELS.md` "effective Dirac description" note |
| 2: the confirming run | ONE script that reads the EXISTING observables on a single defect run and shows the four validated Dirac signatures **co-occur on the same object**: the clock ω, the spin-½ double cover, `L_int`, and the KG dispersion `E² = p² + m²` | the co-occurrence table / plot (four signatures, one run) |
| 3: the T2 go/no-go | From the dictionary + the co-occurrence, judge whether the full EOM derivation (T2: the γ-matrix Clifford algebra from the 4×4 SO(3,1) frame, the coarse-grained `(iγ^μ∂_μ − m)ψ = 0`, the `E²=p²+m²` dispersion + ZBW interference) is worth pursuing | a one-paragraph recommendation |

### How it relates to the absolute-scale work (#208)

T1 pins down **which frequency is the physical `ω = 2mc²/ℏ`** (the ZBW, via the exact `ω_M = 2ω_clock` doubling), exactly the relation the clock-anchor calibration in #208 turns on. The two share the clock-phase ↔ energy mapping, so settling T1's dictionary first removes ambiguity from #208's clock anchor. The absolute `E = mc²` (a physical number rather than a ratio) is the one piece T1 leaves to #208's calibration.

### Definition of done

- [ ] The M5 → effective-Dirac dictionary (the table above as a `MODELS.md` note).
- [ ] One confirming script: the four validated Dirac signatures co-occur on a single defect run, reading existing observables (no new physics, ~1 script).
- [ ] A T2 go/no-go recommendation.

Model: M5 Liquid Crystal. Physics-only, headless. T1 has no hard gates (the pieces exist); it benefits from #208 for the absolute `E = mc²`.

### Issue comments

_No issue comments._
