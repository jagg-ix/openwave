"""M5.12 block 18 leg (a): the optimizer-saturation decider.

The b17 audit's fastest hard decider for the phase-D close: Rayleigh-
optimize omega_bal DIRECTLY under the standing fixed-(size, a2) metric.
If even the optimizer's best direction lands within ~5% of p1 in-frame,
the family search is OPTIMIZER-SATURATED and phase D closes on a measured
endpoint; if it lands lower by more than 5%, the search is still open and
the direction becomes the documented reopening condition.

Method:
    1. Basis (~38 members, all A1-first-harmonic on the n32 frame):
       the analytic aniso-gaussian family (wr x wz grid + component
       variants 0r-only / 0z-only / 0phi + shells + rgauss + nodes) PLUS
       the relaxed endpoint A1 fields (p1, p2, f1, f2, wd, c2) zoomed
       into the frame: the span contains every shape the task has probed.
    2. Pencil by exact-Shat polarization at small amplitude (a2_pol =
       a2_star/100): for each pair, probe(b_i + b_j) and probe(b_i - b_j)
       give both the harmonic S-form and the Q-form (Q2 is exact-
       quadratic to 6e-4 per the b15 audit; the S harmonic part is
       quadratic-model, its ~20% optimum error is handled by step 4).
    3. Generalized eigensolve: minimize (S_static/a2_star + s(c)) / q(c)
       over the Q2 < 0 cone, modest Gram truncation (the b15-audit tau
       lesson: aggressive truncation fabricates S0 < 0 artifacts).
    4. EXACT-probe the top-k model directions at full a2 in the
       controlled frame (zoom to r_target, a2 -> a2_star, one wscale,
       the b17 machinery), both wscale conventions.
    5. Verdict vs TWO references: (i) p1's A1 on the STANDARD hedgehog
       background in-frame (equal-background comparison, the primary
       rule) and (ii) the full relaxed p1 in-frame (5.44 native / 5.11
       rc-matched at 4.77, its own M0).

Anchors: pure analytic members must reproduce m5_12_b16_aniso.json.

Run:  python m5_12_b18_decider.py
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

from m5_17_energy import grid_coords                                      # noqa: E402
from m5_16_axisym import hedgehog_field, pin_mask                          # noqa: E402
from m5_12_dressed import to_covariant                                     # noqa: E402
from m5_12_d3a_bvp import x_pack                                           # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402
from m5_12_b14_seeds import a2_free, probe                                 # noqa: E402
from m5_12_b17_control import (load_state, r_mean_of, zoom_to_frame,       # noqa: E402
                               control_probe, NR_T, NZ_T, H, A2_STAR)

R_TARGET = 4.77
K_TOP = 6
TAU = 1e-6            # Gram truncation (modest, per the b15-audit lesson)


def frame_bg():
    R, Z = grid_coords(NR_T, NZ_T, H)
    return to_covariant(hedgehog_field(R, Z, 8.0 * NR_T / 96.0)), R, Z


def analytic_basis(R, Z):
    """(name, A1) analytic members on the n32 frame."""
    w_b = 8.0 * NR_T / 96.0
    rr = np.sqrt(R ** 2 + Z ** 2) + 1e-12
    cr, cz = R / rr, Z / rr
    r2 = R ** 2 + Z ** 2
    out = []

    def a1_of(b, pattern):
        A1 = np.zeros(R.shape + (4, 4))
        if pattern in ("rz", "0r"):
            A1[..., 0, 1] = A1[..., 1, 0] = b * cr
        if pattern in ("rz", "0z"):
            A1[..., 0, 3] = A1[..., 3, 0] = b * cz
        if pattern == "0phi":
            A1[..., 0, 2] = A1[..., 2, 0] = b * cr
        return A1

    for kr in (1.0, 2.0, 3.0, 4.0):
        for kz in (0.5, 1.0, 2.0):
            b = np.exp(-(R ** 2) / (kr * w_b) ** 2
                       - (Z ** 2) / (kz * w_b) ** 2)
            out.append((f"g_r{kr:g}z{kz:g}", a1_of(b, "rz")))
    for kr, kz in ((3.0, 1.0), (4.0, 1.0)):
        b = np.exp(-(R ** 2) / (kr * w_b) ** 2 - (Z ** 2) / (kz * w_b) ** 2)
        for pat in ("0r", "0z", "0phi"):
            out.append((f"g_r{kr:g}z{kz:g}_{pat}", a1_of(b, pat)))
    for r0 in (1.0, 2.0, 3.0):
        b = np.exp(-((np.sqrt(r2) - r0 * w_b) ** 2) / w_b ** 2)
        out.append((f"shell{r0:g}", a1_of(b, "rz")))
    for k in (1.0, 2.0, 3.0):
        b = (np.sqrt(r2) / (k * w_b)) * np.exp(-r2 / (k * w_b) ** 2)
        out.append((f"rgauss{k:g}", a1_of(b, "rz")))
    for k in (1.0, 2.0):
        b = np.exp(-r2 / (k * w_b) ** 2) * (1.0 - 2.0 * r2 / (k * w_b) ** 2)
        out.append((f"node{k:g}", a1_of(b, "rz")))
    return out


def endpoint_basis():
    out = []
    for tag, path in (("ep_p1", "m5_12_b12_hard_p1_1_state.npz"),
                      ("ep_p2", "m5_12_b12_hard_p2_1_state.npz"),
                      ("ep_f1", "m5_12_b12_hard_f1_1_state.npz"),
                      ("ep_f2", "m5_12_b12_hard_f2_1_state.npz"),
                      ("ep_wd", "m5_12_b12_hard_wd_1_state.npz"),
                      ("ep_c2", "m5_12_b12_hard_c2_1_state.npz")):
        fields, nr_s, nz_s = load_state(path)
        r0 = r_mean_of(fields, nr_s, nz_s)
        zf = zoom_to_frame(fields, nr_s, nz_s, R_TARGET / r0)
        out.append((tag, zf["A1"]))
    return out


def a2_of(A1, pin):
    free = ~pin
    return float(np.sum((A1 ** 2)[free]))


def make_X(M0, A1):
    z = np.zeros_like(M0)
    return x_pack(M0, [A1, z], [np.zeros_like(M0), z])


def main():
    ws_native = wscale_at(NR_T, NZ_T, H, 8.0 * NR_T / 96.0)
    ws_matched = wscale_at(NR_T, NZ_T, H, R_TARGET)
    M0, R, Z = frame_bg()
    pin = pin_mask(NR_T, NZ_T)
    basis = analytic_basis(R, Z) + endpoint_basis()
    names = [n for n, _ in basis]
    B = []
    for _, A1 in basis:
        A1 = A1.copy()
        A1[pin] = 0.0
        B.append(A1 / np.sqrt(a2_of(A1, pin)))     # unit-a2 members
    n = len(B)
    print(f"[basis] {n} members")

    # anchor: pure g_r2z2 vs b16_aniso (wr=2, wz=2)
    with open(os.path.join(DATA, "m5_12_b16_aniso.json")) as f:
        b16 = {(r.get("kr"), r.get("kz")): r for r in json.load(f)["rows"]}
    i22 = names.index("g_r2z2")
    Xa = make_X(M0, B[i22] * np.sqrt(A2_STAR))
    anc = probe(Xa, H, ws_native)
    ref = b16[(2.0, 2.0)]["omega_bal"]
    da = abs(anc["omega_bal"] - ref) / ref
    print(f"[anchor] g_r2z2 w_bal={anc['omega_bal']:.4f} vs b16 {ref:.4f} "
          f"rel={da:.2e}")
    if da > 5e-3:
        raise RuntimeError("anchor mismatch; basis/frame not trusted")

    # pencil by polarization at small amplitude
    eps2 = A2_STAR / 100.0
    t = np.sqrt(eps2)
    X0 = make_X(M0, np.zeros_like(B[0]))
    S_static = probe(X0, H, ws_native)["S0"]
    S = np.zeros((n, n))
    Q = np.zeros((n, n))
    for i in range(n):
        for j in range(i, n):
            recs = []
            for sgn in (1.0, -1.0):
                A1 = t * (B[i] + sgn * B[j]) / (1.0 if i == j else 1.0)
                r = probe(make_X(M0, A1), H, ws_native)
                recs.append(r)
            sp, sm = recs[0]["S0"] - S_static, recs[1]["S0"] - S_static
            qp, qm = recs[0]["Q2"], recs[1]["Q2"]
            S[i, j] = S[j, i] = (sp - sm) / (4.0 * eps2)
            Q[i, j] = Q[j, i] = (qp - qm) / (4.0 * eps2)
        if i % 8 == 0:
            print(f"[pencil] row {i+1}/{n}")
    np.savez_compressed(os.path.join(DATA, "m5_12_b18_pencil.npz"),
                        S=S, Q=Q, names=np.array(names))

    # generalized eigensolve on the -Q > 0 cone
    G = np.eye(n)                                  # unit-a2 basis Gram proxy
    A = S + (S_static / A2_STAR) * G
    negQ = -Q
    w, V = eigh(negQ)
    keep = w > TAU * w.max()
    print(f"[pencil] -Q spectrum: {int(keep.sum())}/{n} kept "
          f"(range {w.min():.2e}..{w.max():.2e})")
    P = V[:, keep] / np.sqrt(w[keep])              # whiten -Q
    Ared = P.T @ A @ P
    lam, U = eigh(Ared)
    out = {"task": "M5.12 block 18", "mode": "decider",
           "r_target": R_TARGET, "a2_star": A2_STAR, "tau": TAU,
           "anchor_rel": da, "model_omega2_min": float(lam[0]),
           "candidates": [], "references": {}}
    print(f"[model] omega_bal(model) top: "
          + "  ".join(f"{np.sqrt(max(v, 0)):.3f}" for v in lam[:K_TOP]))

    # exact-probe top-k model directions in-frame
    for k in range(min(K_TOP, lam.size)):
        c = P @ U[:, k]
        A1 = np.tensordot(c, np.stack(B), axes=(0, 0))
        A1[pin] = 0.0
        fields = {"M0": M0, "A1": A1, "A2": np.zeros_like(M0),
                  "B1": np.zeros_like(M0), "B2": np.zeros_like(M0)}
        r0 = r_mean_of(fields, NR_T, NZ_T)
        rec = {"k": k, "model_omega_bal": float(np.sqrt(max(lam[k], 0.0))),
               "r_mean_raw": r0,
               "coeff_top": sorted(zip(names, np.abs(c).round(4)),
                                   key=lambda p: -p[1])[:5]}
        for wtag, ws in (("native", ws_native), ("rc-matched", ws_matched)):
            pr, _ = control_probe(fields, NR_T, NZ_T, r0, R_TARGET, ws)
            rec[f"inframe_{wtag}"] = pr
            print(f"[exact k={k}] {wtag:>10} w_bal="
                  f"{pr['omega_bal'] if pr['omega_bal'] else float('nan'):.4f}"
                  f"  (model {rec['model_omega_bal']:.3f}, r_raw {r0:.2f})")
        out["candidates"].append(rec)

    # references: p1's A1 on the standard background + full p1, in-frame
    fields, nr_s, nz_s = load_state("m5_12_b12_hard_p1_1_state.npz")
    r0 = r_mean_of(fields, nr_s, nz_s)
    zf = zoom_to_frame(fields, nr_s, nz_s, 1.0)    # native scale copy
    fA = {"M0": M0, "A1": zf["A1"], "A2": np.zeros_like(M0),
          "B1": np.zeros_like(M0), "B2": np.zeros_like(M0)}
    rA = r_mean_of(fA, NR_T, NZ_T)
    for wtag, ws in (("native", ws_native), ("rc-matched", ws_matched)):
        pr_bg, _ = control_probe(fA, NR_T, NZ_T, rA, R_TARGET, ws)
        pr_full, _ = control_probe(fields, nr_s, nz_s, r0, R_TARGET, ws)
        out["references"][wtag] = {
            "p1_A1_on_standard_bg": pr_bg, "p1_full": pr_full}
        print(f"[ref] {wtag:>10} p1-on-std-bg w_bal={pr_bg['omega_bal']:.4f}"
              f"  p1-full w_bal={pr_full['omega_bal']:.4f}")

    # verdict per the pre-registered rule
    best = {}
    for wtag in ("native", "rc-matched"):
        cand = min((c[f"inframe_{wtag}"]["omega_bal"]
                    for c in out["candidates"]
                    if c[f"inframe_{wtag}"]["omega_bal"]), default=None)
        refv = out["references"][wtag]["p1_A1_on_standard_bg"]["omega_bal"]
        best[wtag] = {"optimum": cand, "p1_ref": refv,
                      "gain_vs_p1": (refv - cand) / refv if cand else None}
    out["verdict_rule"] = ("optimizer-saturated if the in-frame optimum is "
                           "within 5% of the p1 reference (equal background)"
                           " in BOTH wscale conventions")
    out["best"] = best
    sat = all(v["gain_vs_p1"] is not None and v["gain_vs_p1"] < 0.05
              for v in best.values())
    out["optimizer_saturated"] = bool(sat)
    for wtag, v in best.items():
        print(f"[verdict] {wtag}: optimum {v['optimum']:.4f} vs p1 "
              f"{v['p1_ref']:.4f}  gain {100 * v['gain_vs_p1']:.1f}%")
    print(f"[VERDICT] optimizer_saturated = {sat}")
    with open(os.path.join(DATA, "m5_12_b18_decider.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("json -> m5_12_b18_decider.json")


if __name__ == "__main__":
    main()
