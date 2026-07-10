"""M5.12 block-18 AUDIT, leg 1 (D1): the decider machinery.

Independent checks on m5_12_b18_decider.py / m5_12_b18_pencil.npz:
  (a) re-derive pencil entries by an INDEPENDENT polarization scheme
      (different formula: B(i+j) - B(i) - B(j), different amplitude
      eps2 = a2_star/200 vs the decider's /100, s0_q2 meter only)
  (b) re-run the eigensolve from the SAVED S/Q with my own whitening;
      reproduce lam0 / the k=0 coefficient content; tau sweep
  (c) the Gram question: the decider used G = I ("unit-a2 basis Gram
      proxy") but the members are NOT a2-orthogonal; compute the TRUE
      Gram M_ij = <B_i, B_j>_a2 and re-solve with it: how much of the
      model optimum is a Gram artifact?
  (d) reconstruct the k=0 candidate, re-probe it exactly (on-frame at
      full a2, in-frame via control_probe both wscales, and at small
      amplitude a2_star/100 where the quadratic model must be accurate)
      and DECOMPOSE the 3.275 -> 7.213 model-exact gap into
      (Gram proxy) + (S0 nonlinearity) + (the zoom-to-frame step).

Run:  python m5_12_audit_b18_pencil.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy.linalg import eigh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_16_axisym import pin_mask                                          # noqa: E402
from m5_12_d3a_bvp import x_pack                                           # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402
from m5_12_b14_seeds import s0_q2, probe                                   # noqa: E402
from m5_12_b17_control import (r_mean_of, control_probe,                   # noqa: E402
                               NR_T, NZ_T, H, A2_STAR)
from m5_12_b18_decider import (frame_bg, analytic_basis, endpoint_basis,   # noqa: E402
                               a2_of, make_X, R_TARGET, TAU)

R = None


def main():
    out = {"leg": "D1 decider machinery"}
    ws_native = wscale_at(NR_T, NZ_T, H, 8.0 * NR_T / 96.0)
    ws_matched = wscale_at(NR_T, NZ_T, H, R_TARGET)
    M0, Rg, Zg = frame_bg()
    pin = pin_mask(NR_T, NZ_T)
    basis = analytic_basis(Rg, Zg) + endpoint_basis()
    names = [n for n, _ in basis]
    B = []
    for _, A1 in basis:
        A1 = A1.copy()
        A1[pin] = 0.0
        B.append(A1 / np.sqrt(a2_of(A1, pin)))
    n = len(B)

    d = np.load(os.path.join(DATA, "m5_12_b18_pencil.npz"), allow_pickle=True)
    S_pub, Q_pub = d["S"], d["Q"]
    names_pub = [str(x) for x in d["names"]]
    assert names == names_pub, "basis name order mismatch"

    S_static = s0_q2(make_X(M0, np.zeros_like(B[0])), H, ws_native)[0]
    out["S_static"] = S_static

    # ---- (a) independent polarization, different scheme + amplitude ----
    eps2 = A2_STAR / 200.0
    t = np.sqrt(eps2)

    def bilin(A1):
        s0, q2 = s0_q2(make_X(M0, t * A1), H, ws_native)
        return (s0 - S_static) / eps2, q2 / eps2

    pairs = [(5, 5), (5, 19), (26, 25), (26, 26), (9, 24)]
    rows = []
    cache = {}

    def single(i):
        if i not in cache:
            cache[i] = bilin(B[i])
        return cache[i]

    for i, j in pairs:
        if i == j:
            s_ii, q_ii = single(i)
            s_mine, q_mine = s_ii, q_ii
        else:
            s_pp, q_pp = bilin(B[i] + B[j])
            s_i, q_i = single(i)
            s_j, q_j = single(j)
            s_mine = (s_pp - s_i - s_j) / 2.0
            q_mine = (q_pp - q_i - q_j) / 2.0
        rows.append({
            "pair": f"{names[i]},{names[j]}",
            "S_mine": s_mine, "S_pub": float(S_pub[i, j]),
            "S_rel": abs(s_mine - S_pub[i, j]) / max(abs(S_pub[i, j]), 1e-12),
            "Q_mine": q_mine, "Q_pub": float(Q_pub[i, j]),
            "Q_rel": abs(q_mine - Q_pub[i, j]) / max(abs(Q_pub[i, j]), 1e-12)})
        r = rows[-1]
        print(f"[pol] {r['pair']:>18}  S {s_mine:+.5f} vs {r['S_pub']:+.5f} "
              f"(rel {r['S_rel']:.2e})  Q {q_mine:+.6f} vs {r['Q_pub']:+.6f} "
              f"(rel {r['Q_rel']:.2e})")
    out["polarization_rederivation"] = rows

    # ---- (b) own eigensolve from the saved pencil ----
    G = np.eye(n)
    A = S_pub + (S_static / A2_STAR) * G
    negQ = -Q_pub
    w, V = eigh(negQ)
    keep = w > TAU * w.max()
    P = V[:, keep] / np.sqrt(w[keep])
    lam, U = eigh(P.T @ A @ P)
    out["eig_reproduce"] = {
        "n_kept": int(keep.sum()),
        "lam0": float(lam[0]),
        "model_omega0": float(np.sqrt(max(lam[0], 0.0))),
        "pub_lam0": 10.723892700056231,
        "rel": abs(lam[0] - 10.723892700056231) / 10.723892700056231}
    print(f"[eig] kept {int(keep.sum())}/{n}  lam0={lam[0]:.6f} "
          f"(pub 10.723893, rel {out['eig_reproduce']['rel']:.2e})")

    c0 = P @ U[:, 0]
    top5 = sorted(zip(names, np.abs(c0).round(4)), key=lambda p: -p[1])[:5]
    out["k0_coeff_top5_mine"] = [[a, float(b)] for a, b in top5]
    print("[eig] k0 top5:", top5)

    # tau sweep
    taus = {}
    for tau in (1e-4, 1e-6, 1e-8, 1e-10):
        kp = w > tau * w.max()
        Pt = V[:, kp] / np.sqrt(w[kp])
        lt = eigh(Pt.T @ A @ Pt, eigvals_only=True)
        taus[f"{tau:.0e}"] = {"kept": int(kp.sum()), "lam0": float(lt[0]),
                              "omega0": float(np.sqrt(max(lt[0], 0.0)))}
        print(f"[tau {tau:.0e}] kept {int(kp.sum())}  "
              f"omega0={taus[f'{tau:.0e}']['omega0']:.4f}")
    out["tau_sweep"] = taus

    # ---- (c) the TRUE Gram ----
    free = ~pin
    Bf = np.stack([b[free] for b in B]).reshape(n, -1)
    M = Bf @ Bf.T
    out["gram"] = {"diag_max_dev": float(np.abs(np.diag(M) - 1).max()),
                   "offdiag_max": float(np.abs(M - np.diag(np.diag(M))).max())}
    A_true = S_pub + (S_static / A2_STAR) * M
    lam_t = eigh(P.T @ A_true @ P, eigvals_only=True)
    out["model_omega0_trueGram"] = float(np.sqrt(max(lam_t[0], 0.0)))
    print(f"[gram] offdiag max {out['gram']['offdiag_max']:.3f}  "
          f"model omega0 with TRUE Gram = "
          f"{out['model_omega0_trueGram']:.4f} (I-Gram "
          f"{out['eig_reproduce']['model_omega0']:.4f})")
    # the k=0 direction's own Gram content
    cMc = float(c0 @ M @ c0)
    cIc = float(c0 @ c0)
    out["k0_gram_content"] = {"cMc": cMc, "cIc": cIc, "ratio": cMc / cIc}
    print(f"[gram] k0: c'Mc={cMc:.4f}  c'Ic={cIc:.4f}  ratio {cMc/cIc:.3f}")

    # ---- (d) exact re-probe + gap decomposition on the k=0 direction ----
    A1c = np.tensordot(c0, np.stack(B), axes=(0, 0))
    A1c[pin] = 0.0
    a2c = a2_of(A1c, pin)
    # model prediction for THIS direction with the true normalization
    s_hat = float(c0 @ S_pub @ c0) / cMc
    q_hat = float(c0 @ Q_pub @ c0) / cMc
    om_model_dir = float(np.sqrt((S_static / A2_STAR + s_hat) / (-q_hat)))
    out["k0_model_omega_trueGram_dir"] = om_model_dir

    # small-amplitude exact vs model (on-frame, no zoom)
    A1u = A1c / np.sqrt(a2c)          # unit a2
    rows_amp = []
    for frac in (0.01, 0.1, 1.0):
        a2t = A2_STAR * frac
        s0, q2 = s0_q2(make_X(M0, np.sqrt(a2t) * A1u), H, ws_native)
        s_ex = (s0 - S_static) / a2t
        q_ex = q2 / a2t
        om_ex = float(np.sqrt(s0 / -q2)) if q2 < 0 else None
        om_md = float(np.sqrt((S_static / a2t + s_hat) / (-q_hat)))
        rows_amp.append({"a2_frac": frac, "s_exact_perA2": s_ex,
                         "s_model_perA2": s_hat,
                         "s_rel": abs(s_ex - s_hat) / abs(s_hat),
                         "q_exact_perA2": q_ex, "q_model_perA2": q_hat,
                         "q_rel": abs(q_ex - q_hat) / abs(q_hat),
                         "omega_exact_onframe": om_ex,
                         "omega_model": om_md})
        print(f"[amp x{frac:g}] s/a2 {s_ex:+.4f} vs model {s_hat:+.4f} "
              f"(rel {rows_amp[-1]['s_rel']:.2e})  q/a2 {q_ex:+.5f} vs "
              f"{q_hat:+.5f} (rel {rows_amp[-1]['q_rel']:.2e})  "
              f"omega exact {om_ex if om_ex else float('nan'):.4f} "
              f"model {om_md:.4f}")
    out["amplitude_scan"] = rows_amp

    # in-frame exact (the decider's quoted numbers): control_probe path
    fields = {"M0": M0, "A1": np.sqrt(A2_STAR) * A1u,
              "A2": np.zeros_like(M0), "B1": np.zeros_like(M0),
              "B2": np.zeros_like(M0)}
    r0 = r_mean_of(fields, NR_T, NZ_T)
    inframe = {}
    for wtag, ws in (("native", ws_native), ("rc-matched", ws_matched)):
        pr, _ = control_probe(fields, NR_T, NZ_T, r0, R_TARGET, ws)
        inframe[wtag] = pr["omega_bal"]
        print(f"[inframe {wtag}] omega_bal={pr['omega_bal']:.4f} "
              f"(pub {'7.2131' if wtag == 'native' else '6.1475'})")
    out["k0_inframe_reprobe"] = {"r_mean_raw": r0, **inframe,
                                 "pub_native": 7.2131317823101355,
                                 "pub_rc": 6.147527393784886}

    # gap decomposition
    om_ex_frame = rows_amp[-1]["omega_exact_onframe"]
    out["gap_decomposition"] = {
        "model_I_gram": out["eig_reproduce"]["model_omega0"],
        "model_true_gram_same_dir": om_model_dir,
        "exact_onframe_full_a2": om_ex_frame,
        "exact_inframe_native": inframe["native"],
        "stage_gram_pct": 100 * (om_model_dir
                                 / out["eig_reproduce"]["model_omega0"] - 1),
        "stage_nonlin_pct": 100 * (om_ex_frame / om_model_dir - 1),
        "stage_zoom_pct": 100 * (inframe["native"] / om_ex_frame - 1)}
    g = out["gap_decomposition"]
    print(f"[gap] I-Gram model {g['model_I_gram']:.3f} -> true-Gram "
          f"{g['model_true_gram_same_dir']:.3f} ({g['stage_gram_pct']:+.1f}%)"
          f" -> exact on-frame {g['exact_onframe_full_a2']:.3f} "
          f"({g['stage_nonlin_pct']:+.1f}%) -> in-frame native "
          f"{g['exact_inframe_native']:.3f} ({g['stage_zoom_pct']:+.1f}%)")

    with open(os.path.join(DATA, "m5_12_audit_b18_pencil.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("json -> m5_12_audit_b18_pencil.json")


if __name__ == "__main__":
    main()
