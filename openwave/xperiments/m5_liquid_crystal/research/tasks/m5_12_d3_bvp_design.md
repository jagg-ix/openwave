# M5.12 phase D3 design: the time-periodic 4D BVP (formulation + gates, no runs)

> Block-4 deliverable of task [M5.12](m5_12_task_details.md) (2026-07-07, design-only per user decision). The three cheap routes are measured-closed (statics: block 1; undressed rotor clock: block 2; dressed rotor clock: block 3, each by pre-registered controls or adversarial audit): this document specifies the one remaining route, the genuine time-periodic boundary-value problem on the verified 4D Lagrangian, so the run blocks execute a design instead of improvising one. Method-note discipline: equations first; every derivation lands as a machine gate (BG-series) before any physics run.

## 1. The problem statement

Find **time-periodic stationary points of the 4D action** on the equivariant instrument:

```text
M(rho, z, t) symmetric 4x4, equivariant in phi, periodic in t with period T = 2pi/omega,
omega FREE (the nonlinear eigenvalue),

S[M; omega] = INT_0^T dt INT d^3x  L,
L = - [ SUM_{i<j} inner_eta(F_ij, F_ij)  -  SUM_i inner_eta(F_0i, F_0i) ] - V_4D(M)
F_munu = [d_mu M, d_nu M]_eta ,   [A,B]_eta = A.eta.B - B.eta.A ,
inner_eta = double internal eta raising ,  eta = diag(-1,1,1,1)
V_4D = w SUM_{p=1..4} ( Tr_eta(M^p) - c_p )^2 ,  c_p = SUM_i Lambda_i^p ,
Lambda = (g, 1, delta, 0), covariant vacuum m00 = -g   (delta = 0 sector first)
```

Signs and conventions are the M5.18-verified ones (`m5_18_lorentz_check.py`: `l_curv` carries the spacetime raising `sgn = eta_mumu eta_nunu`, so the `F_0i` terms enter L with the opposite sign to `F_ij`); the instrument spatial normalization (the 4x factor) is carried explicitly per the block-2 audit correction.

**Why a BVP and not time-stepping (the evidence, all measured):** the exact kinetic quadratic form has a NEGATIVE eigenvalue in every grid cell on defect backgrounds (block-3 audit, per-cell ghost eigs to −819); the M5.8 constrained 4D evolution ran away after ~2 clock periods (dt-invariant, f32 == f64: true dynamics of the action, not the integrator); and the owner's stated foundation is two-sided least action, "not Euler-Lagrange" evolution (2026-07-06, [`m5_18_convo.md`](m5_18_convo.md) reply 2). An IVP falls into the ghost sector; a periodic-orbit CRITICAL-POINT problem does not have to: stationarity is well-posed where minimization is not. This also converges with Track C's C3 conclusion (the breather is irreducibly time-dependent: pose a periodic orbit with omega free) and with resolved Q1 (particles are time-periodic resonances).

## 2. Discretization

| Axis | Scheme | Rationale |
| --- | --- | --- |
| Space | the calibrated equivariant (rho, z) grid (cell-centered rho, mirror ghost, 2 pi rho h^2 weights), production 96×192, h-family for convergence | the M5.16-gated reduction; the loop and hedgehog are both axisymmetric |
| Time | Fourier spectral: `M(x, t) = M_0(x) + SUM_{k=1..Nt} [ A_k(x) cos(k omega t) + B_k(x) sin(k omega t) ]`, Nt = 2-4 harmonics to start | the measured clock is near-monochromatic (M5.8 N-1: omega_1 + a 2 omega_1 harmonic over drift); spectral-in-time makes T-periodicity EXACT and d_t analytic |
| Rotating frame option | `M(x,t) = Lam(omega t) Mhat(x,t) Lam(omega t)^{-1}` with Mhat T-periodic and Lam = expm(omega t eta W_R12): solve for Mhat | captures the rotor limit as Mhat = const (block 2/3 exactness for R12: dress/rotate commute to 5.6e-17) and lets small harmonics ride on top; the winding is absorbed analytically. **⚠️ SCOPE CORRECTION (2026-07-07 block 7):** the frame trick requires `[W, equivariance] = 0`; the only commuting generators are R12 (PURE GAUGE on axisymmetric fields: the block-6 catch) and boosts (hyperbolic, non-periodic: no boost clock is a rigid periodic conjugation). The physical axis-swing clock is a genuine TEXTURE motion within the equivariant class (the direct Fourier solve handles it; a co-rotating frame does not exist for it on this reduction). The direct formulation + inner-solve strength is therefore the working route |
| DOF count | (Nt·2 + 1) × 96×192 × 10 sym components ≈ 0.9-1.7 M f64 | matrix-free methods mandatory; feasible on the M4 |

Time integrals of the action over one period are evaluated EXACTLY on the Fourier basis (products of trigs: quadrature by Nt-aliasing-safe sampling, N_samples ≥ 4Nt+1, trapezoid on the period = exact for band-limited integrands).

## 3. The solver: saddle-finding, not minimization

The discretized stationarity system:

```text
R[X; omega] = dS/dX = 0        (X = all Fourier coefficient fields)
+ one PHASE condition          (fix the t-origin: <dX0/dt-mode, X> = 0)
+ one AMPLITUDE/constraint eq. (select the branch: J = J*, or E = lambda L per
                                Duda's conservation mechanism, or |A_1| = a*)
with omega the matching free unknown (nonlinear eigenvalue: the M6 lesson,
"BVP with the eigenvalue FREE is what works")
```

Primary method: **Newton-Krylov on R** (matrix-free JVP by directional FD of R; GMRES inner; the static spectral-instrument Hessian diagonal as preconditioner). Newton finds critical points of ANY index: the ghost sector is not an obstacle to the solver, only to naive descent. Fallbacks: (a) pseudo-arclength continuation in omega (branch following from the seeds below); (b) the M5.8 2c constrained spectral-projection integrator reused as a RESIDUAL SMOOTHER, never as the truth.

Seeds for continuation: the D2b rotor states (audit-refuted as PHYSICS, legitimate as SEEDS: hedgehog b0 ≈ 1.7, loop b0 ≈ 0.45-0.6 at their J windows) and the static solutions + a small kick in the first harmonic.

## 4. Pre-registered gates (BG series: ALL must pass before any physics claim)

| Gate | Checks | Pass bar |
| --- | --- | --- |
| BG1 | the discrete residual R == FD of the discrete action S (random fields, random directions, both omega and X blocks) | rel < 1e-6 (FD-limited) |
| BG2 | static identity: any 3D-instrument static solution embeds (all harmonics 0) with `R_spatial == the gated static gradient` and `R_harmonics == 0` | machine (< 1e-12) |
| BG3 | the exact vacuum rotor: `M = Lam(omega t) M_vac Lam(omega t)^{-1}` must be an EXACT solution (R == 0) for every omega and every generator (Lorentz orbit of a vacuum is a vacuum) | machine |
| BG4 | rotor consistency: on the rigid-rotor manifold the residual's b0-projection reproduces d/db0 of the audited D2b `E(b0; J)` numbers (with the 4x normalization explicit) | rel < 1e-8 |
| BG5 | Noether energy conservation along t on any converged solution (H(t) drift over the period) | < 1e-10 relative |
| BG6 | convergence protocol: h-family (64/96/128) AND Nt-family (2/4/8) on the first converged branch point; Richardson where clean | reported, no bar (honesty gate) |
| BG7 | ghost-sector sanity: the converged solution's second-variation spectrum sampled (Lanczos, matrix-free): report the index (number of negative directions); a physical branch should have FINITE, h-stable index | reported |

## 5. The g-treatment (the gating design question)

Block-3's audit measured the mechanism: the negative channel scales with the g-vs-1 mismatch of the background (gain −13.5 / −21 / −2413 at g = 0/1/8; the g = 1 covariant vacuum is dressing-inert via `Lam eta Lam = eta`). Physical g ~ 1e10 is 9 orders beyond the working value. Design decision:

| Route | Status |
| --- | --- |
| (i) g-continuation: solve branches at g ∈ {1, 2, 4, 8, 16, 32}, measure the scaling law of every branch observable (omega, E, size, index), extrapolate with the law in hand (the M5.16 exact-polynomial-in-delta pattern applied where the g-dependence is polynomial; else fitted scaling, labeled) | ADOPTED as the working route |
| (ii) a g → infinity leading-order theory (the g-row dynamics may decouple or dominate cleanly) | derivation candidate, opened as a D3 side-question; attempt only if (i) shows clean power laws |
| (iii) ask the owner | the evidence bundle is now strong (the per-cell ghost structure, the g-mechanism identity, Q18/Q19 witnesses) but the ask stays HELD with the group share until the final M5.12 report (user decision, block-2 review) |

## 6. Prerequisites + unknowns

| Item | Status |
| --- | --- |
| `V_4D` recalibration (the p4 term shifts undressed statics 39%) | **D3-pre, REQUIRED**: rerun the M5.16 anchor chain (m_e scale, r_half, virial) under `V_4D` before any 4D-static or BVP number is compared to anything |
| The axis-swing rotor ambiguity (block-3 audit target B) | any axis-swing clock in D3 must re-derive its kinetic form inside the BVP (the Fourier formulation sidesteps the rotor ambiguity: no reduction, no ambiguity) |
| Unknowns quadrant (blindspot pass for the run blocks) | known-unknowns: does ANY nontrivial branch exist; the index of the first branch; the g-law. Unknown-knowns: what counts as "the neutrino" among branches (loop topology class per Q16; acceptance = Faber's 3-eigenstates + oscillating mixture). Unknown-unknowns flagged: Newton basin failures near the ghost sector; branch jumping under continuation; the p4-recalibration moving the static baseline under the seeds; Fourier truncation interacting with the winding (mitigated by the rotating-frame option); compute cost per Newton step (~30-60 energy-gradient-equivalents: minutes/step at n96: acceptable) |
| Phase plan for the run blocks | **D3a** residual + gates BG1-BG5 (one block); **D3b** vacuum rotor + static embedding + first hedgehog clock branch by continuation from the D2b seed, g = 8 (one block); **D3c** the g-continuation ladder on the hedgehog branch + BG6/BG7 (one block); **D3d** the LOOP branch (the actual neutrino attempt: seed from the D2b loop rotor state) + phase-E/F observables on whatever converges (masses via E = lambda L; PMNS from the preferred time derivatives per the owner's directive) |

## 7. What this design does NOT claim

No solution is claimed to exist. The honest outcomes of the D3 ladder are: a converged nontrivial branch (the program's first particle-candidate SOLUTION), or a measured non-existence/divergence pattern (a verdict-grade negative on the model's central stabilization claim, given the three closed reductions). Both are reportable; the second, after blocks 1-3, would carry real falsification weight, which is exactly the standing Duda gave the program ("should be used if it is right").

## Cross-links

- Task record + block findings: [`m5_12_task_details.md`](m5_12_task_details.md) (§ FINDINGS blocks 1-3 carry the closures this design rests on)
- The verified conventions: [`../findings/m5_18_verification_note.md`](../findings/m5_18_verification_note.md) + [`../scripts/m5_18_lorentz_check.py`](../scripts/m5_18_lorentz_check.py)
- The audited machinery reused: [`../scripts/m5_12_clock_q.py`](../scripts/m5_12_clock_q.py) (Q_W + normalization), [`../scripts/m5_12_dressed.py`](../scripts/m5_12_dressed.py) (dressed class + `V_4D`)
- Heritage: M5.8 2c (the IVP runaway evidence) + Track C C3 (periodic orbit, omega free) + the M6 transfer (BVP-with-free-eigenvalue; ansatz-gated lessons) in [`../m5_question_tracker.md § HARDEST PIECES`](../m5_question_tracker.md)
- Owner stance: [`m5_18_convo.md`](m5_18_convo.md) reply 2 (least action, two-sided BCs; negative-H intended)
