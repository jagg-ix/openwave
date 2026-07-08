"""M5.12 block-11 adversarial audit: verdict assembly.

Merges the measured numbers (m5_12_audit_b11_numbers.json, produced by
m5_12_audit_b11_run.py) with the auditor's per-claim verdicts into the
single verdict record data/m5_12_audit_b11.json.

Run:  python m5_12_audit_b11_verdicts.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

N = json.load(open(os.path.join(DATA, "m5_12_audit_b11_numbers.json")))
S = N["states"]

out = {
    "task": "M5.12 block 11",
    "role": "INDEPENDENT ADVERSARIAL AUDIT of the blocks 7-10 rotor-class candidate",
    "date": "2026-07-08",
    "scripts": ["m5_12_audit_b11_lib.py", "m5_12_audit_b11_run.py",
                "m5_12_audit_b11_verdicts.py"],
    "audit_tool_gates": N["gates"],
    "structural_fact": (
        "Machine-verified (4.9e-16): M(t_j) is omega-independent and Mdot ~ omega, "
        "so Shat(X,w) = S0(X) - w^2 Q2(X) and R(X,w) = R_sp(X) + w^2 R_t(X) EXACTLY. "
        "The least-squares-optimal omega at fixed X is closed-form: "
        "w*^2 = -<R_sp,R_t>/|R_t|^2."),

    "claims": {
        "C1_branch_frequency": {
            "verdict": "REFUTED",
            "claim": ("omega* = 0.6446/0.6564/0.6569 (n32/48/64), Richardson ~0.657, "
                      "is a physical grid-converged property of a genuine branch"),
            "evidence": [
                "omega* IS the closed-form least-squares balance frequency of the "
                "UNCONVERGED state: w_ls = 0.64346/0.65634/0.656943 vs saved "
                "0.64464/0.65642/0.656943 (n64 agrees to 7e-7). It is computable from "
                "any state whatsoever and has no branch-eigenvalue status.",
                "The omega-selecting inner products live 99.89-99.92% in the core "
                "cells (r < 2rc), the SAME cells that carry 84-94% of the plateau "
                "residual which C3 attributes to discretization error. If C3 is "
                "right, omega* is a function of the discretization-error field; "
                "C1 and C3 cannot both stand.",
                "No run converged: F_rel_end = 3.3e-3/7.0e-3/2.9e-2 vs the 1e-5 "
                "target; the claimant's own verdict field says stalled_or_partial "
                "3/3; LSMR hit maxiter (istop=7) on EVERY iteration of every run.",
                "The grids are one warm-start chain, not independent: |R| of the "
                "n32 endpoint zoomed to n48 = 102161.9 vs the n48 run's logged "
                "|F|0 = 102160 (exact match); n64's omega0 = 0.65642 = n48's "
                "endpoint. Grid-to-grid omega agreement is inherited.",
                "The omega sequence CONTRADICTS h^2 convergence: observed diff "
                "ratio 22.5 vs h^2-predicted 2.86 (off x7.9); the two Richardson "
                "extrapolations disagree: 0.6658 (32/48) vs 0.6576 (48/64), spread "
                "0.0082 = 16x the (n48,n64) grid difference; n64's within-run "
                "omega drift (0.0037, still +0.0007/iter at stop) is 7x the "
                "(n48,n64) grid difference (0.0005).",
                "Free-period stationarity is violated by 4-5 orders and is "
                "UNSATISFIABLE: c_omega = dShat/dw - Shat/w = -25290/-36484/-47064 "
                "(vs Shat = +352/-426/-1554); c_omega = -(S0 + w^2 Q2)/w with "
                "measured S0 > 0 AND Q2 > 0 (S0 = 8327/11761/14682, Q2 = "
                "19193/28284/37621) has NO root at any omega. The object can only "
                "be a driven/constrained forced response (pinned boundary carries "
                "rotating values, max |A1| = 0.5 on pinned cells; the soft c_amp "
                "row imposes the seed amplitude).",
                "The claimant's own solution-quality metric refutes it: BG5 H "
                "drift = 2.17/2.20/2.19 across n32/48/64 (I recomputed "
                "independently), grid-INDEPENDENT at 220%. An approach to a "
                "genuine branch limited by h^2 core error would show the drift "
                "improving with grid. It does not move.",
                "omega_ls is a knife-edge function of the imposed amplitude: "
                "rescaling the harmonics by 0.7 destroys the interior minimum "
                "entirely (w_ls^2 < 0); by 1.3 sends it to 8.2. The 'branch "
                "frequency' exists only at the constraint-imposed amplitude.",
            ],
            "surviving_form": (
                "At the plateau state, |R(w)|^2 does have a genuine interior "
                "minimum in w (depth 0.87/0.94/0.96 relative to w=0), "
                "reproducibly near 0.65-0.66 along the warm-start chain: a "
                "forced-balance frequency of the constrained, driven-boundary, "
                "unconverged rotor configuration. Nothing more."),
            "numbers": {
                "omega_ls_vs_saved": {n: [S[n]["omega_ls_closed_form"],
                                          S[n]["omega_saved"]]
                                      for n in ("n32", "n48", "n64")},
                "core_share_of_omega_selection": {
                    n: S[n]["omega_ls_by_region"]["core_r<2rc"]["share_of_Rt2"]
                    for n in ("n32", "n48", "n64")},
                "c_omega": {n: S[n]["c_omega_free_period"]
                            for n in ("n32", "n48", "n64")},
                "S0_Q2": {n: [S[n]["S0"], S[n]["Q2"]]
                          for n in ("n32", "n48", "n64")},
                "H_drift_rel": {n: S[n]["H_drift_rel"]
                                for n in ("n32", "n48", "n64")},
                "richardson": N["histories"]["richardson"],
                "warmstart_forensic_n32_to_n48": [
                    N["inject"]["n32_state_zoomed_to_n48_Rfree"], 102160.0],
                "omega_ls_vs_amplitude_n32": S["n32"]["omega_ls_vs_amplitude"],
                "omega_selection_depth": {
                    n: S[n]["omega_selection_depth"]
                    for n in ("n32", "n48", "n64")},
            },
        },

        "C2_load_bearing_rotation": {
            "verdict": "WEAKENED",
            "claim": ("the state is not a trivially-rotating static solution nor "
                      "a symmetry/gauge orbit; evidence: rigidity 0.132, "
                      "static-residual-of-co-rotating-mean 851"),
            "evidence": [
                "SURVIVES (non-gauge): the (2,3) swing is genuinely non-gauge. "
                "R12 conjugation of M0 changes the static energy by 9.5e-16 "
                "(exact isometry, block-6 confirmed); the swing orbit's sampled "
                "spatial+V energy varies by 240-250% over the period; A1 is "
                "orthogonal to every one-parameter generator tangent [W, M0]_eta "
                "(6-generator least-squares fit residual 0.999).",
                "REFUTED (interpretation of rigidity): rigidity 0.132 (n48; I "
                "reproduce 0.13230, ns-independent) is 4.1% of the swing "
                "amplitude (max |A1| = 3.25) and 1.7% of the field scale: the "
                "co-rotating profile is CONSTANT to within 5%. The state "
                "satisfies the rigid-rotor algebra to high precision: "
                "|[W23, M0]|/|M0| = 0.0011, |B1 - [W23,A1]|/|B1| = 0.008, "
                "|A1 + [W23,B1]|/|A1| = 0.008 (n48). It is numerically a "
                "UNIFORM-ROTATION-ANSATZ configuration, the same class the "
                "block-2/3 audit already handled, not a new time-periodic object.",
                "REFUTED (static residual 851): the co-rotating mean's static "
                "residual (I reproduce 851.45 at n48; 1124/851/734 across grids) "
                "is 1.09-1.15x the state's OWN unconverged plateau residual "
                "(1030/742/661) with per-cell distribution cosine similarity "
                "0.91/0.94/0.93 and the same core concentration (87-97% vs "
                "84-94%). It is the same unconverged core residual measured "
                "twice; it cannot distinguish 'load-bearing rotation' from "
                "'unconverged rotating configuration'.",
            ],
            "surviving_form": (
                "The axis-swing motion is not a gauge/symmetry orbit (that part "
                "stands). But the state is a near-rigid uniform-rotation-ansatz "
                "configuration far from solving anything; 'load-bearing' is "
                "unestablished: both its evidence numbers are re-measurements of "
                "the same unconverged core residual."),
            "numbers": {
                "rigidity": {n: S[n]["rigidity_ns12"] for n in ("n32", "n48", "n64")},
                "rigidity_rel_to_swing": {n: S[n]["rigidity_rel_to_swing"]
                                          for n in ("n32", "n48", "n64")},
                "rotor_identities_n48": [S["n48"]["rotor_id_WM0_rel"],
                                         S["n48"]["rotor_id_B1_eq_WA1_rel"],
                                         S["n48"]["rotor_id_A1_eq_minusWB1_rel"]],
                "staticR_vs_plateau": {n: [S[n]["staticR_of_corot_mean"],
                                           S[n]["Rfree_at_saved_omega"],
                                           S[n]["staticR_vs_plateau_cell_cosine"]]
                                       for n in ("n32", "n48", "n64")},
                "orbit_fit_A1_rel_residual": {n: S[n]["orbit_fit_A1_rel_residual"]
                                              for n in ("n32", "n48", "n64")},
                "gauge_check_n32": S["n32"]["gauge_check_static_energy"],
                "sampleE_variation_rel": {n: S[n]["sampleE_variation_rel"]
                                          for n in ("n32", "n48", "n64")},
            },
        },

        "C3_plateau_is_h2_core_error": {
            "verdict": "WEAKENED",
            "claim": ("the unconverged residual (RMS/cell 19.94/9.11/5.82) is "
                      "core discretization error scaling as h^2, not a sign the "
                      "branch does not exist"),
            "evidence": [
                "SURVIVES (core concentration): the plateau residual is core-"
                "concentrated: 84/90/94% of |R|^2 within r < 2rc, and per-cell "
                "RMS falls with grid (my recompute at the saved states: "
                "23.5/11.2/7.4).",
                "WEAKENED (h^2 attribution): my RMS ratios are 2.11 (32->48) and "
                "1.51 (48->64) vs h^2-predicted 2.25 and 1.78; the second is off "
                "by 15% and the comparison is polluted: wscale changes 15x across "
                "grids (0.0341/0.00695/0.00223) and the runs stopped at different "
                "depths.",
                "REFUTED (plateau established): no plateau is demonstrated. |F| "
                "was still falling at every stop (-1.6%/-1.1%/-1.6% per iteration "
                "at n32/48/64); n64 ran only 6 iterations; LSMR hit maxiter "
                "(istop=7) on every iteration, so the stall is at least partly "
                "LINEAR-SOLVER truncation, not a converged least-squares floor.",
                "REFUTED (h^2-error reading of the obstruction): if the only "
                "obstruction were h^2 core error, solution-quality metrics would "
                "improve with grid. The Noether H drift is 2.17/2.20/2.19 "
                "(grid-independent), the co-rotating static residual stays "
                "1.1x the plateau at every grid, and omega's h^2 Richardson "
                "fails by x7.9.",
                "State-injection test (n64 state zoomed to n32/n48) inconclusive: "
                "interpolation error dominates (order-1 vs order-3 differ 1.6-3x).",
            ],
            "surviving_form": (
                "The residual is core-resident and shrinks with resolution, "
                "consistent with SOME resolution-limited core structure; but "
                "'h^2 discretization error of an existing branch' is not "
                "established, the plateau itself is not established, and the "
                "grid-independent H drift positively suggests the obstruction "
                "is not mere discretization error."),
            "numbers": {
                "rms_per_free_cell": {n: S[n]["rms_per_free_cell"]
                                      for n in ("n32", "n48", "n64")},
                "rms_ratios_observed_vs_h2": [[2.105, 2.25], [1.505, 1.778]],
                "core_share_of_R2": {n: S[n]["R2_share_by_region"]["core_r<2rc"]
                                     for n in ("n32", "n48", "n64")},
                "F_slope_per_iter_at_stop": {
                    n: N["histories"][n]["F_slope_per_iter_at_stop"]
                    for n in ("n32", "n48", "n64")},
                "wscale_per_grid": [0.03407, 0.0069546, 0.0022265],
                "injection_test": N["inject"],
            },
        },

        "C4_breather_obstruction": {
            "verdict": "WEAKENED",
            "claim": ("c_omega pins to -Shat/omega within 0.3%, hence "
                      "dShat/domega ~ 0 at small amplitude and genuine "
                      "free-period orbits require large amplitude"),
            "evidence": [
                "The 0.3% 'pin' is an exact algebraic identity, not a "
                "measurement: Shat is exactly quadratic in omega (verified "
                "4e-16), so c_omega = -(S0 + w^2 Q2)/w identically and the gap "
                "to -Shat/w equals 2 w^2 Q2 / |Shat| = 0.003034 for the saved "
                "state: precisely the observed 0.3%. Any near-static state of "
                "any physics gives the same pin; it restates 'the harmonics are "
                "small'.",
                "dShat/domega ~ amplitude^2 is likewise structural, not "
                "discovered: Q2(lam)/(lam^2 Q2) = 0.9995 (lam=0.5) and 1.0018 "
                "(lam=2.0).",
                "The surviving (and sharpened) content is the SIGN measurement: "
                "Q2 = +0.0549 > 0 with S0 = +39.31, and the free-period root "
                "needs w^2 Q2 = -S0 < 0. Moreover the breather state has ZERO "
                "time-mixing content (Q2_mixing = 0.0 exactly), and for "
                "mixing-free states inner_eta is non-negative, so Q2 >= 0 at ANY "
                "amplitude in this class: 'requires large amplitude' is an "
                "UNDERSTATEMENT; it requires developing eta-negative time-mixing "
                "channels that dominate Q2, which the class as posed does not "
                "contain at all.",
                "The breather run itself shows no branch: omega drifting "
                "monotonically down (1.086 -> 1.041), amplitude sliding off its "
                "target (c_amp -0.10 and growing), c_omega parked at -38, LSMR "
                "istop=7 throughout: slow collapse toward the static solution.",
            ],
            "surviving_form": (
                "As a measurement: only the signs Q2 > 0, S0 > 0 (and Q2_mix = "
                "0) survive; the correct conclusion is stronger than the claim: "
                "in the mixing-free breather class NO free-period orbit exists "
                "at any amplitude; a root requires a sign flip of Q2 via "
                "dominant time-mixing channels."),
            "numbers": N["breather"],
        },
    },

    "targets": {
        "T1_g8_background_disease": {
            "finding": (
                "The block-3 form of the disease does NOT recur: the "
                "omega-channel is defect/core-resident, not g-background-"
                "resident. Q2 is 92.5% core (r < 2rc), only 5% far-field; the "
                "eta-negative mixing part of Q2 is only ~6-8% of Q2 "
                "(-1511/-1712/-1973 vs +19193/+28284/+37621); the PURE-VACUUM "
                "(2,3) rotor has Q2 = 1e-28 (exactly zero time channel), so no "
                "background rotor structure exists to ride; the g=1 repose "
                "(m00/8, mixing/sqrt8) keeps Q2 > 0 (1699 vs S0 1789): no root "
                "structure appears or disappears with g. HOWEVER a different "
                "background pathology exists: 91-92% of the volume-weighted "
                "swing amplitude |A1|^2+|B1|^2 lives in the far field (r > 6rc) "
                "and the PINNED boundary carries rotating values (max |A1| = 0.5 "
                "on pinned cells): the c_amp branch selector + BC maintain a "
                "box-wide driven rotating texture; the core carries only "
                "1.2-1.6% of the swing amplitude."),
            "verdict_effect": "C1 dies by other means (core-error selection); "
                              "the amplitude constraint is exposed as mostly a "
                              "far-field/boundary rotation constraint.",
            "numbers": {
                "Q2_core_share": {n: S[n]["Q2_share_by_region"]["core_r<2rc"]
                                  for n in ("n32", "n48", "n64")},
                "Q2_mixing_over_Q2": {
                    n: S[n]["Q2_mixing_part"] / S[n]["Q2"]
                    for n in ("n32", "n48", "n64")},
                "amp2_far_share": {
                    n: S[n]["amp2_weighted_share_by_region"]["far_r>6rc"]
                    for n in ("n32", "n48", "n64")},
                "A1_max_on_pinned_boundary": 0.5,
                "vacuum_rotor_Q2": [1.3e-28, 2.2e-28],
                "g1_repose": S["n32"]["g1_repose"],
            },
        },
        "T2_constraint_artifact": {
            "finding": (
                "CONFIRMED as the operative mechanism. omega is not determined "
                "by any stationarity of the action (c_omega = -25290 to -47064, "
                "unsatisfiable while Q2 > 0); it is the closed-form LS balance "
                "w*^2 = -<R_sp,R_t>/|R_t|^2 of the unconverged residual, "
                "reproducing the saved omegas to 1e-3/8e-5/7e-7. It exists only "
                "at the imposed amplitude (harmonics x0.7: no minimum; x1.3: "
                "w_ls = 8.2) and moved 0.6564 -> 0.6440 in the claimant's own "
                "om2 side-run when row weights changed. The raw seed's w_ls is "
                "3.4 (not 0.65): the 0.65 value forms during relaxation as the "
                "core residual reorganizes: a forced-response/balance frequency "
                "of the constrained system."),
            "numbers": {
                "omega_ls_amplitude_scan_n32": S["n32"]["omega_ls_vs_amplitude"],
                "seed_omega_ls": {k: v for k, v in N["seeds"].items()
                                  if k.startswith("seed")},
                "claimant_om2_log_shift": [0.6564, 0.6440],
            },
        },
        "T3_gauge_symmetry_orbit": {
            "finding": (
                "The (2,3) swing is NOT a gauge/symmetry orbit: R12 conjugation "
                "is an exact isometry of the reduced functional (9.5e-16) while "
                "the (2,3) orbit's sample energies vary 240-250%; no "
                "one-parameter generator W fits A1 ~ [W, M0]_eta (residual "
                "0.999; forced: M0 is charge-0 under W23 so [W23, M0] ~ 0 while "
                "A1 is charge-1). C2's non-gauge sub-claim stands. But the "
                "harmonic content satisfies the rigid-rotor charge algebra to "
                "0.1-1.7%: the state is the uniform-rotation ANSATZ in Fourier "
                "clothes, not a new orbit class."),
            "numbers": {
                "orbit_fit": {n: S[n]["orbit_fit_A1_rel_residual"]
                              for n in ("n32", "n48", "n64")},
                "rotor_algebra_n48": [S["n48"]["rotor_id_WM0_rel"],
                                      S["n48"]["rotor_id_B1_eq_WA1_rel"],
                                      S["n48"]["rotor_id_A1_eq_minusWB1_rel"]],
            },
        },
        "T4_rot_test_validity": {
            "finding": (
                "Plain conjugation IS the correct group action for (2,3) "
                "rotations: expm(eta W23 th) equals the plain rotation and the "
                "eta-action Lam^-T M Lam^-1 equals L M L^T (both machine-zero, "
                "gate AG5), so the ROT numbers are well-defined; rigidity is "
                "ns-independent (ns=12 vs 36 identical, as forced by the Nt=1 "
                "band limit) and I reproduce 0.13230 at n48. The INTERPRETATION "
                "fails, not the arithmetic: staticR(mean) = 1.09-1.15x the "
                "state's own plateau |R| with cell-map cosine 0.91-0.94 and the "
                "same core concentration: it is the plateau residual re-measured, "
                "not independent evidence of load-bearing rotation."),
            "numbers": {
                "eta_vs_plain": [N["gates"]["AG5_eta_vs_plain_rot_lam"],
                                 N["gates"]["AG5_eta_vs_plain_rot_action"]],
                "staticR_over_plateau": {
                    n: S[n]["staticR_of_corot_mean"] / S[n]["Rfree_at_saved_omega"]
                    for n in ("n32", "n48", "n64")},
                "cell_cosine": {n: S[n]["staticR_vs_plateau_cell_cosine"]
                                for n in ("n32", "n48", "n64")},
            },
        },
        "T5_h2_arithmetic_richardson": {
            "finding": (
                "The omega sequence CONTRADICTS h^2 convergence: observed "
                "difference ratio 22.5 vs h^2-predicted 2.86 (off x7.9); "
                "Richardson from (32,48) gives 0.6658, from (48,64) gives "
                "0.6576: spread 0.0082 = 16x the (48,64) grid difference, so "
                "'Richardson ~0.657' cherry-picks the second pair. The n64 "
                "point is 6 shallow iterations still drifting +0.0007/iter "
                "(total within-run drift 0.0037 = 7x the grid difference it is "
                "supposed to resolve), warm-started from n48's endpoint "
                "(omega0 = 0.65642); n48 was warm-started from n32 (forensic: "
                "zoomed-n32 |R| = 102161.9 vs logged |F|0 = 102160). My RMS "
                "ratios 2.11/1.51 vs h^2 2.25/1.78."),
            "numbers": N["histories"]["richardson"],
        },
        "T6_breather_identity_triviality": {
            "finding": (
                "It IS an identity: exact omega-quadraticity of Shat makes "
                "c_omega = -(S0 + w^2 Q2)/w for every state, and the 0.3% gap "
                "equals 2 w^2 Q2/|Shat| = 0.003034 computed from the state: the "
                "'pin' is contentless as a measurement; dShat/dw ~ amplitude^2 "
                "is structural (Q2 scaling 0.9995/1.0018 at lam 0.5/2.0). What "
                "survives: the signs (Q2 = +0.0549, S0 = +39.31) and the "
                "sharper theorem that the mixing-free breather class has "
                "Q2 >= 0 at ANY amplitude (Q2_mix = 0 exactly; eta-negative "
                "contributions require time-mixing entries), so no free-period "
                "orbit exists in the class as posed: large amplitude alone "
                "cannot rescue it."),
            "numbers": N["breather"],
        },
    },

    "most_damaging_finding": (
        "omega* is the closed-form least-squares balance frequency "
        "w*^2 = -<R_sp,R_t>/|R_t|^2 of an unconverged state (reproduces the "
        "claimed 0.6446/0.6564/0.6569 to up to 7e-7), and that balance is "
        "selected 99.9% by the same core cells whose residual C3 attributes to "
        "discretization error, on a warm-start chain whose runs never "
        "converged, never conserved H (drift 2.2, grid-independent), and can "
        "never satisfy the free-period condition while Q2 > 0. The branch "
        "candidate is a constrained forced response; C1 and C3 are mutually "
        "exclusive as stated."),
    "what_a_fix_requires": [
        "Converge SOMETHING: drive one grid to F_rel < 1e-5 (more LSMR "
        "iterations / better preconditioning / a direct sparse solve at n32) "
        "so 'plateau' claims have a converged object behind them; if |F| "
        "floors far above roundoff at a genuine LS floor, report that floor "
        "and its h-scaling with fixed wscale normalization.",
        "Replace the omega story: a genuine free-period branch needs the "
        "c_omega row satisfied (dS/domega = 0), which is impossible while "
        "Q2 > 0; either exhibit states with dominant eta-negative time-mixing "
        "(Q2 < 0) or reframe the object honestly as a driven-boundary forced "
        "response and stop calling omega* a branch frequency.",
        "Kill the boundary drive: rerun with static (time-independent) "
        "pinned boundary (A1 = B1 = 0 on pinned cells) and check whether any "
        "nontrivial time-periodic content survives; currently max |A1| = 0.5 "
        "on the pinned shell and 91% of the swing amplitude is far-field.",
        "Grid study without warm-start inheritance: independent seeds per "
        "grid, equal convergence depth, fixed-physical-units normalization, "
        "and H-drift as the convergence metric (it currently does not improve "
        "with grid at all).",
    ],
    "compute_note": "All checks ran at full grids (n32/n48/n64 states); total "
                    "audit compute ~1 min (single residual evaluations are "
                    "cheap; the expensive part of the claimant's runs was LSMR, "
                    "which the closed-form omega analysis bypasses).",
}

path = os.path.join(DATA, "m5_12_audit_b11.json")
with open(path, "w") as f:
    json.dump(out, f, indent=1)
print(f"verdicts -> {path}")
for c, v in out["claims"].items():
    print(f"  {c}: {v['verdict']}")
