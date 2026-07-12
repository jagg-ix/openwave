# M5.20.1 method note: biaxial (1, δ, 0) dynamics, does the spectral gap protect the vortex loop?

**Task**: [`m5_20_1_task_details.md`](../tasks/m5_20_1_task_details.md) · **Spec**: Duda 2026-07-11/12 ([`m5_20_convo.md`](../tasks/m5_20_convo.md)): "topological vortex requires potential with (1, delta, 0) minimum - preferred three different, which should regularize to two equal in center"; "the problem was indeed assuming delta=0 everywhere, for which there is no topological vortex"; "in 3D (1, delta, 0) you can start with". Predecessor: [`m5_20_method_note.md`](m5_20_method_note.md) (the δ = 0 verdict: all runs unwind, no radiation needed). Status: ✅ complete (audited; review approved 2026-07-12; merged into the combined note [`m5_20_2_method_note.md`](m5_20_2_method_note.md) as Part I).

## 0. FIELD CONTENT (what the engine evolves, and what THIS run evolves)

```text
THE SUBSTRATE IS THE FULL 4x4 TENSOR FIELD (engine default since M5.8.1):
   M(x) = O(x) · D · O(x)^T,   M real-symmetric 4x4,
   D = diag(g, 1, δ, 0),  index 0 = the time/g axis (your convention),
   g = 8.0  (medium.py: MDIM = 4, LC_G = 8.0).
Your 4D Lagrangian is verified on it to machine precision (M5.18:
Lorentz invariance 1.3e-11, Legendre map exact), and the spectral
potential pins the (g, 1, δ, 0) spectrum exactly (4 Tr-power targets).

THIS RUN evolves the spatial 3x3 block with target spectrum (1, δ, 0)
per your sanctioned start ("in 3D (1, delta, 0) you can start with",
2026-07-12). The time row rides along inert: with M_0μ = (g, 0, 0, 0)
uniform, every commutator channel leaves it invariant, so g is a
spectator of the spatial-block dynamics below.

THE FULL 4x4 OSCILLATION RUN is the declared successor M5.20.2. Its
machinery exists (the 4x4 substrate; the M5.18-verified Lagrangian; a
constrained 4D Minkowski integrator, M5.8.2c); what blocks it is
well-posedness, not code: the time/kinetic term in M variables (Q23),
the constraint structure of the degenerate Legendre map (Q18), and the
timelike branch choice (Q19).
```

## 1. Equations first

**The functional** (the M5.20 stack, spectral targets moved to the biaxial sector):

```text
L = ∫ 2πρ dρ dz [ (1/2) ||∂t M||_F²  −  u_curv  −  V ]

u_curv = 4 c₂ Σ_{μ<ν} ||[∂_μ M, ∂_ν M]||_F²        (c₂ = 1 sim units; the audited M5.17 form)
V      = w Σ_{p=1..3} (Tr M_sp^p − c_p)²,   c_p = 1 + δ^p   (target spectrum (1, δ, 0))
w      = 7.24e-4 (the M5.12-calibrated scale, FIXED across δ for controlled comparison;
         one recalibrated control bounds the scheme dependence)
```

The kinetic term is the canonical sigma-model choice, as in M5.20; the conditionality (tracker [Q23](../m5_question_tracker.md#q23-detail)) is SOFTENED this round: the spatial (1, δ, 0) run is the author's sanctioned start, so the sector choice is his; the Γ-variable time term remains not derived and belongs to M5.20.2.

**Why δ ≠ 0 changes the protection question** (the phase-A theory, measured in § 3):

```text
Vacuum V-Hessian at diag(1, δ, 0) (6x6, symmetric-block directions):
  δ = 0 : FOUR zero modes = 3 conjugation flats + the splitting direction
          of the degenerate (0,0) pair (flat to quartic order)
          = the potential-free removability face M5.20's unwinding used.
  δ ≠ 0 : the splitting mode ACTIVATES ("activating potential"):
          lowest activated Hessian gap ω = 0.0041 / 0.0099 / 0.0125 at
          δ = 0.1 / 0.3 / 0.5 (the Rayleigh quotient along the pure
          diag(0,1,−1) split direction is higher: sqrt(w(4δ² + 9δ⁴)) =
          0.0054 / 0.0177 / 0.0336; audit-corrected presentation);
          zero modes drop 4 → 3 (conjugation only).
Analytic check: the eigenvalue-sector Hessian is 2w J^T J, J_pi = p λ_i^{p−1}
(the residual factors vanish at the exact minimum); rank J = 3 iff the three
eigenvalues are distinct (rank 2 at δ = 0: the one diagonal zero mode).
```

**The two winding pairings** (which pair of (1, δ, 0) spans the meridional cross-section plane; the out-of-plane eigenvalue rides the azimuthal axis) and the two-equal core his construction prescribes:

```text
pair_1d : winds (1, δ), out-of-plane 0;  core ((1+δ)/2, (1+δ)/2, 0)
          per-cell core barrier V/w = 0.611 / 0.288 / 0.095  (δ = 0.1/0.3/0.5)
pair_d0 : winds (δ, 0), out-of-plane 1;  core (1, δ/2, δ/2)
          per-cell core barrier V/w = 3e-5 / 0.0024 / 0.024
(reference: full melt (0,0,0) costs V/w = 3.23 / 3.93 / 5.08)
```

His 2026-07-12 mechanism ("energy minimization has to equalize 2 eigenvalues in the center") makes the pairing a MEASUREMENT, not a choice: both pairings are seeded and the core-equalization diagnostic (§ instruments) reads which pair the run holds equalized.

**Uniform vacua and the linear-radiation lemma per far field** (the M5.20 audit lesson, re-derived here per chosen vacuum):

```text
At δ ≠ 0 every uniform equivariant vacuum diag(a₁, a₂, a₃) [ρ, φ, z axes]
has a₁ ≠ a₂ for some pair (all three eigenvalues distinct), so:
  - NO assignment is axis-regular: every axisym biaxial far field carries a
    scheme-invisible axis disclination (u_curv charges it nothing: the lone
    A_φ = [J, M₀]/ρ channel has no commutator partner);
  - the A_φ background makes [A_pert, A_φ^bg] LINEAR in a perturbation:
    the linear-radiation channel strength scales with |a₁ − a₂|.
Chosen far fields (continuity with the M5.20 escape arms at δ → 0):
  pair_1d → diag(δ, 0, 1)  (→ e3e3^T): channel ∝ δ
            measured pulse spread −0.007 cells over T = 60 at δ = 0.3 (none)
  pair_d0 → diag(0, 1, δ)  (→ e2e2^T): channel O(1)
            measured pulse spread +0.79 cells over T = 60 (weak, the e2 analog)
```

**Discrete EOM, integrator, sponge, energy ledger**: verbatim M5.20 (velocity Verlet on `w_cell ∂t² M = −∂E/∂M`, split-step sponge with exact `E_abs` accumulation, `KE + PE + E_abs = const` up to Verlet drift).

## 2. Equation-to-code map

| Term / instrument | Function | File |
| --- | --- | --- |
| gap map: 6×6 vacuum V-Hessian at diag(1, δ, 0), zero modes, ω_split | `vacuum_hessian_delta`, `gap_map` | [`m5_20_1_a_theory.py`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_20_1_a_theory.py) |
| analytic eigenvalue-sector Hessian `2w J^T J` (gate A3) | `analytic_diag_hessian` | same |
| uniform-vacuum enumeration (V, u_curv, A_φ, axis regularity) | `enumerate_vacua` | same |
| two-equal core barrier table | `core_cost_table` | same |
| biaxial escaped loop seed (far = pair, two-equal core, blend to the enumerated vacuum) | `loop_field_biax`, `pairing_spec` | [`m5_20_1_b_seeds.py`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_20_1_b_seeds.py) |
| eigenframe winding read + mixing monitor (gate B1) | `winding_measure_biax` | same |
| core-equalization diagnostic (gate B2) | `core_spectrum` | same |
| fast gradient at general c_p (gate GF-d pins it to the audited path) | `grad_fast_biax` | [`m5_20_1_d_dynamics.py`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_20_1_d_dynamics.py) |
| production runs (closed / sponge / recal control) | `run_case` | same |
| pulse test per far-field vacuum (GA3-d) | `gate_ga3` | same |
| FIRE statics triage | `relax_case` | [`m5_20_1_c_statics.py`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_20_1_c_statics.py) |
| classifier v2 (both documented M5.20 bugs fixed: bilinear guard, full RADIATES conjunction) | `classify`, `winding_measure_bilin` | [`m5_20_1_e_verdicts.py`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_20_1_e_verdicts.py) |
| per-peak core hunt + endpoint maps | `core_hunt`, `maps` | same |
| remnant blob probe vs the δ-dependent mass ladder | `m5_20_1_f_blob.py` | [`m5_20_1_f_blob.py`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_20_1_f_blob.py) |
| inherited audited stack (curvature, spectral V, integrator, sponge, ring locator) | M5.17/18/19/20 modules | [`m5_20_a1_dynamics.py`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_20_a1_dynamics.py) etc. |

## 3. Results, each next to its gate

| Result | Number | Gate / verification |
| --- | --- | --- |
| Gap map: zero modes 4 → 3; lowest activated gap ω | 0.0041 / 0.0099 / 0.0125 at δ = 0.1/0.3/0.5 (Rayleigh along diag(0,1,−1): 0.00544 / 0.01770 / 0.03363 = sqrt(w(4δ²+9δ⁴)), audit) | gates A1-A3 (`data/m5_20_1_a_theory.json`); analytic 2wJ^TJ to 4.6e-10; audit claim 2 |
| Instruments valid | seed reads q = 0.5 exact at r_w 3-6, both instruments, every (δ, pairing) | gates B0-B2, bilinear gate (`data/m5_20_1_b_gates.json`) |
| Integrator valid at δ ≠ 0 | GF-d 0.0/1.3e-16; dt² ratios ~4; drift 9.7e-7 (dt 0.02, T 20) | gates GF/GA1/GA2 (`data/m5_20_1_d_gates.json`) |
| Linear channel per vacuum | pair_1d −0.007 cells / pair_d0 +0.79 cells (T = 60) | GA3-d, matches the § 1 lemma |
| Statics triage: ALL SIX DISSOLVE (net-charge) | E collapses toward vacuum (δ=0.3 pair_1d: 20.9 → 0.47), E strictly monotone (audit); centroid q reads 0 | FIRE, 4000 iters (`data/m5_20_1_c_statics.json`); NOT stationary (1.6-2.0 decades); ⚠️ audit: the δ=0.1 pair_1d endpoint retains a ±1/2 dipole at (ρ,z) ≈ (24-25, 0), net 0: dissolution incomplete there |
| **Dynamics verdict grid: UNWOUND at every δ, both pairings** (the headline) | 6/6 closed-box runs t = 2000; bilinear endpoint reads 0.0 at r_w 3-8; no wound core-hunt peak; energy conserved to ≤ 3.6e-6 (core 6) / ≤ 7.3e-6 (all 10) over 100k steps | classifier v2 (both M5.20 bugs fixed) + per-peak hunt + maps (`data/m5_20_1_verdicts.json`) |
| Unwinding needs NO radiation at δ ≠ 0 | closed boxes unwind with E conserved (drift ≤ 3.6e-6) | same as M5.20's audit-C4 logic, now in the gapped theory |
| Why the gap fails: barrier vs driving | integrated two-equal core-tube cost 1.34 / 0.63 / 0.21 (pair_1d) and ~0 / 0.005 / 0.05 (pair_d0) vs loop energies 48.7 / 20.9 / 7.8 (pair_1d): the activation is ~3% of the driving (audit: 2.7-3.0%) at the calibrated w = 7.24e-4 | analytic per-cell V (§ 1) × core tube π ws² × 2πR₀; statics E strictly monotone (audit claim 6) |
| Core-equalization readout (the measured Q22 pairing answer, audit-tempered) | the dynamics definitively ABANDONS the seeded (1,δ) two-equal core in every pair_1d run; the endpoint reads (δ,0)-equalized, CONFIRMED as genuine at δ ≥ 0.3 (remnant λ = (0.99, 0.23, 0.07)-class) and VACUUM-CONFOUNDED below (near-vacuum debris always carries the (δ,0) label for δ < 0.5; δ=0.1 unproven) | the DoD-3b diagnostic + audit claim 3; matches the near-free (δ,0) barrier |
| Unwind timing / remnant morphology | pair_d0: m13 half-life t ≈ 125-375, energy DISPERSES box-wide (the weak linear channel); pair_1d: a LOCALIZED unwound biaxial remnant persists to t = 2000 (m13 ≥ seed, PE_end 20.4 / 8.8 / 3.8), no winding | maps + trajectories; the remnant is the blob-probe target |
| Recal-w control: UNWOUND (the verdict is not a wscale artifact) | δ = 0.3 pair_1d at the seed-virial autochi w: same endpoint (bilinear reads 0.0, core drifts to (δ,0)-equalized) | classifier v2, `m5_20_1_run_d0p3_pair_1d_closed_recal` |
| δ = 0 anchor: UNWOUND (corpus continuity) | the new pipeline at δ = 0 reproduces the M5.20 outcome | `m5_20_1_run_d0p0_pair_1d_closed_anchor` |
| Remnant re-probe: a persistent localized oscillation with spectral power in a band overlapping the top mass line | broad non-stationary band 0.13-0.16 around the δ = 0.3 top line 0.1463 (window-dependent peak 0.137-0.148; the raw "0.1466 = 0.2%" was FFT-bin quantization, ±3.5% floor: audit claim 5); E_blob FLAT over T = 300 (0.348 → 0.349): persistent, unwound | blob probe + audit re-estimate; the δ = 0.5 pair_d0 remnant near the middle line (0.042-0.043 band) decays (0.326 → 0.296) |
| 🚧 Sponge arms (δ = 0.3, both pairings) | | running |

## 4. Inspection set (≤ 4 artifacts) + the object itself

**What the simulation evolves, seen directly**: the panels below are the axisym meridional cross-section (ρ, z); the 3D object is this half-plane revolved around the ρ = 0 axis. At t = 0 the neutrino-candidate vortex loop sits as a compact wound ring at (ρ = 17, z = 0): |M13| is the winding texture, the s-dip marks the two-equal regularized core, the energy density is the ring tube.

![t = 0: the seeded neutrino-candidate loop, both pairings at delta = 0.3](../plots/m5_20_1_seed_maps.png)

1. The headline: verdict grid + gap map + retention:

![protection vs delta](../plots/m5_20_1_protection.png)

2. Phase A: ω ladder, zero modes, core barriers:

![gap map](../plots/m5_20_1_gapmap.png)

3. Endpoint maps + core hunt at t = 2000 (the same cross-section after unwinding: the pair_1d localized remnant vs the pair_d0 dispersal):

![endpoint maps](../plots/m5_20_1_endpoints.png)

4. Trajectories: q(t), m13(t), PE_in8(t), core-equalization(t):

![dynamics trajectories](../plots/m5_20_1_dynamics.png)

## 5. Not computed here

- The full 4×4 (g, 1, δ, 0) oscillation run (M5.20.2: blocked on Q23 time term in M variables, Q18 constraint structure, Q19 branch choice).
- Any physical-unit anchoring of δ or of the loop scale (the δ value is an open sector parameter, Q22).
- 3D non-axisymmetric evolution (the axisym instrument cannot represent a Cartesian-uniform biaxial far field; the axis-disclination caveat in § 1 is the honest price).
- Radiated-spectrum decomposition per mode (the sponge ledger is total-energy only).

## 6. Adversarial audit (independent agent, 2026-07-12; own instruments: `m5_20_1_audit_check.py` → `data/m5_20_1_audit.json`)

The auditor built its own winding instruments (dense plaquette defect maps on all three 2-plane blocks, own bilinear circle reads, coarse circle grid), its own exact Hessian derivation, its own energy reimplementation (matches endpoint PE to ≤ 2e-7), and its own spectral estimator; validated on an own-built synthetic vortex, a null field, and the task seeds.

| Claim | Audit verdict | What changed in this note |
| --- | --- | --- |
| 1. UNWOUND 10/10 (the headline) | **CONFIRMED** (zero confirmed wound cores in every endpoint; the large δ=0.1 pair_1d remnant m13 carries NO winding; the 10 strong plaquettes in d0p5_pair_d0 are 1-cell ± dipoles, net 0, none circle-confirmed) | none |
| 2. Gap map 4 → 3, ω_split | **CONFIRMED with caveat**: ω_split (Rayleigh along diag(0,1,−1)) = sqrt(w(4δ² + 9δ⁴)) exactly, but the TRUE lowest activated gap is the Hessian ω = 0.0041 / 0.0099 / 0.0125 (25-63% below the Rayleigh number) | headline gap numbers now quote BOTH (§ 1 corrected) |
| 3. Minimization selects the (δ,0)-equalized core | **PARTIALLY**: real at δ = 0.3/0.5 (remnant λ = (0.99, 0.23, 0.07)-class, the seeded (1,δ) two-equal core definitively abandoned); UNPROVEN at δ = 0.1 (remnant gap_bot 0.20 > δ); the diagnostic label is vacuum-trivial for δ < 0.5 (near-vacuum debris always reads "(δ,0)") and statics endpoints keep the pair_1d label | claim reworded (§ 3): "the dynamics abandons the seeded (1,δ) two-equal core; the (δ,0)-equalization label is confirmed at δ ≥ 0.3 and is vacuum-confounded below" |
| 4. Conservation ≤ 3.6e-6 | **CONFIRMED** (6 core runs ≤ 3.6e-6; the δ=0 anchor 5.2e-6 endpoint / 7.3e-6 max; sponge ledgers close to 2.7e-6) | drift row now says "≤ 3.6e-6 (core 6) / ≤ 7.3e-6 (all 10)" |
| 5. Remnant "on the top mass line, 0.2%" | **REFUTED AS STATED**: 0.1466 is exactly FFT bin 7 (Δω = 0.0209, ±3.5% floor, no interpolation); refined estimates are window-dependent (0.137-0.148) over a broad non-stationary band (half-1 dominant 0.084, half-2 0.136); E_blob flatness confirmed | claim reworded everywhere: "a persistent localized oscillation with spectral power in a band overlapping the top mass line"; the 0.2% coincidence deleted |
| 6. Barrier vs driving | **CONFIRMED** (own closed forms match; statics E strictly monotone decreasing in all 6); actual barrier/driving 2.7-3.0% | "3-5%" → "~3%" |

**Audit side finding**: the δ = 0.1 pair_1d STATICS endpoint retains a tight +1/2 −1/2 defect DIPOLE at (ρ, z) ≈ (24-25, 0) (net charge 0, E collapsed 48.7 → 0.80, non-stationary): "DISSOLVES" is net-charge-true but dissolution is INCOMPLETE at δ = 0.1 after 4000 iters; the dynamics runs at the same δ show no such dipole. The statics row carries this footnote now.

**Instrument bugs found (documented, not fixed in the frozen task files, the M5.20 pattern)**: (1) `winding_measure_biax` has no axis/edge guard (`m5_20_1_b_seeds.py:103-131`; latent here, ring centers stayed ≥ 17; the endpoint classifier's `winding_measure_bilin` DOES guard); (2) the statics verdict path uses the debris-sensitive `ring_by_m13` centroid with no core-hunt backup (source of the masked δ=0.1 dipole); (3) `m5_20_1_f_blob.py` takes a raw FFT-bin argmax (the claim-5 artifact; `omega_peak_E` = bin 1 = detrend artifact); (4) `core_spectrum`'s equalization label is vacuum-trivial for δ < 0.5 and tie-breaks to pair_d0. Audit limits: non-coordinate-plane eigenframe windings only indirectly excluded; sub-cell cores near the axis outside instrument coverage; inter-snapshot drift not observable from trajectories (GA1 makes it implausible); the GA3 pulse numbers not re-run.
