"""M5.12 block-15 ADVERSARIAL AUDIT, part 1 (P4 + P2 endpoint arithmetic).

(1) P4 sweep integrity: load EVERY saved b15 seed npz, recompute a2_free,
    S0 = Shat(X,0), Q2 = Shat(X,0) - Shat(X,1), channel split, omega_bal
    directly on the audit-verified instrument; compare row by row against
    data/m5_12_b15_shapes.json; re-derive the floor ranking independently.
(2) instrument identity spot checks: Shat(X,w) == S0 - w^2 Q2 at w =
    omega_bal and one arbitrary w; H_mean(omega_bal) == 0 via bg5_noether.
(3) anchor guard: gauss_k1 / gauss_k2 / lag1_k1 vs m5_12_b14_seeds_n32.json.
(4) P2 endpoint arithmetic: f1/f2 (and wd for context) relaxed endpoints,
    recompute omega_bal / Q2 / split / a2 conservation / H_swing over S0.

Run:  python3 -u m5_12_audit_b15_reprobe.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_16_axisym import pin_mask                                        # noqa: E402
from m5_12_d3a_bvp import shat, x_pack                                   # noqa: E402
from m5_12_d3b_newton import wscale_at                                   # noqa: E402
from m5_12_gauntlet import bg5_noether                                   # noqa: E402

h, Nt = 1.0, 2
nr, nz = 32, 64
WSC = wscale_at(nr, nz, h, 8.0 * 32 / 96)


def load_x(path):
    d = np.load(path)
    X = x_pack(d["M0"].astype(np.float64),
               [d[f"A{k+1}"].astype(np.float64) for k in range(Nt)],
               [d[f"B{k+1}"].astype(np.float64) for k in range(Nt)])
    pin = pin_mask(nr, nz)
    for k in range(Nt):
        X["A"][k][pin] = 0.0
        X["B"][k][pin] = 0.0
    return X, pin


def a2_free(X, pin):
    free = np.broadcast_to((~pin)[..., None, None]
                           & np.ones((1, 1, 4, 4), bool), X["M0"].shape)
    return float(np.sum(X["A"][0][free] ** 2) + np.sum(X["B"][0][free] ** 2))


def q2_split(X):
    out = {}
    for key, keep_mix in (("mix", True), ("pos", False)):
        Xc = {"M0": X["M0"].copy(), "A": [a.copy() for a in X["A"]],
              "B": [b.copy() for b in X["B"]]}
        for arr in Xc["A"] + Xc["B"]:
            if keep_mix:
                arr[..., 1:4, 1:4] = 0.0
            else:
                arr[..., 0, :] = 0.0
                arr[..., :, 0] = 0.0
        s0 = shat(Xc, 0.0, h, WSC)
        out[key] = s0 - shat(Xc, 1.0, h, WSC)
    return out["mix"], out["pos"]


def probe(X):
    s0 = shat(X, 0.0, h, WSC)
    q2 = s0 - shat(X, 1.0, h, WSC)
    wb = float(np.sqrt(s0 / -q2)) if (q2 < 0 and s0 > 0) else None
    return s0, q2, wb


OUT = {"script": "m5_12_audit_b15_reprobe.py", "sections": {}}
t0 = time.time()

# ---------------- (1) P4: full sweep reprobe ----------------
print("=== (1) P4 sweep reprobe from saved seeds ===")
pub = json.load(open(os.path.join(DATA, "m5_12_b15_shapes.json")))
rows = []
worst = {"omega": 0.0, "S0": 0.0, "Q2": 0.0, "a2": 0.0}
for r in pub["rows"]:
    X, pin = load_x(os.path.join(DATA, r["state"]))
    a2 = a2_free(X, pin)
    s0, q2, wb = probe(X)
    q2m, q2p = q2_split(X)
    drow = {"profile": r["profile"], "kappa": r["kappa"],
            "a2_re": a2, "S0_re": s0, "Q2_re": q2, "omega_re": wb,
            "Q2_mix_re": q2m, "Q2_pos_re": q2p,
            "omega_pub": r["omega_bal"],
            "rel_omega": (abs(wb - r["omega_bal"]) / r["omega_bal"]
                          if wb else None),
            "rel_S0": abs(s0 - r["S0"]) / abs(r["S0"]),
            "rel_Q2": abs(q2 - r["Q2"]) / abs(r["Q2"]),
            "rel_a2": abs(a2 - r["a2"]) / r["a2"]}
    rows.append(drow)
    worst["omega"] = max(worst["omega"], drow["rel_omega"] or 0.0)
    worst["S0"] = max(worst["S0"], drow["rel_S0"])
    worst["Q2"] = max(worst["Q2"], drow["rel_Q2"])
    worst["a2"] = max(worst["a2"], drow["rel_a2"])
    print(f"  {r['profile']:>8} k={r['kappa']:<4g} "
          f"w_re={wb:.6f} pub={r['omega_bal']:.6f} "
          f"rel={drow['rel_omega']:.2e}")
ranked = sorted([d for d in rows if d["omega_re"]],
                key=lambda d: d["omega_re"])
my_top = [(d["profile"], d["kappa"], d["omega_re"]) for d in ranked[:6]]
pub_top = [(d["profile"], d["kappa"], d["omega_bal"])
           for d in pub["floor_ranked"]]
rank_match = all(a[0] == b[0] and a[1] == b[1]
                 for a, b in zip(my_top, pub_top))
print(f"  worst rel: omega {worst['omega']:.2e} S0 {worst['S0']:.2e} "
      f"Q2 {worst['Q2']:.2e} a2 {worst['a2']:.2e}")
print(f"  floor ranking match: {rank_match}")
print(f"  my top-2: {my_top[:2]}")
OUT["sections"]["p4_sweep"] = {"rows": rows, "worst_rel": worst,
                               "rank_match": bool(rank_match),
                               "my_floor_ranked": my_top}

# ---------------- (2) instrument identities ----------------
print("=== (2) instrument identity spot checks ===")
ids = []
for st in ("m5_12_b15_seed_rgauss_k2_n32.npz",
           "m5_12_b15_seed_shell_k1_n32.npz",
           "m5_12_b15_seed_gauss_k1_n32.npz"):
    X, pin = load_x(os.path.join(DATA, st))
    s0, q2, wb = probe(X)
    # Shat(w) = S0 - w^2 Q2 exactly
    for w in (wb, 2.34):
        sh = shat(X, w, h, WSC)
        pred = s0 - w * w * q2
        rel = abs(sh - pred) / (abs(sh) + abs(pred))
        ids.append({"state": st, "w": w, "rel_quad_identity": rel})
    # H_mean at omega_bal == 0 by construction (2*S0 - Shat(w_bal) and bg5)
    bg5 = bg5_noether(X, wb, h, WSC)
    hm_rel = abs(bg5["H_mean"]) / s0
    ids.append({"state": st, "H_mean_over_S0": hm_rel,
                "H_swing_over_S0": (bg5["H_max"] - bg5["H_min"]) / s0})
    print(f"  {st}: quad-identity rel {ids[-3]['rel_quad_identity']:.2e} "
          f"/ {ids[-2]['rel_quad_identity']:.2e}, "
          f"H_mean/S0 {hm_rel:.2e}")
OUT["sections"]["identities"] = ids

# ---------------- (3) anchors ----------------
print("=== (3) b14 anchor guard ===")
b14 = json.load(open(os.path.join(DATA, "m5_12_b14_seeds_n32.json")))
b14w = {s["class"]: s["omega_bal"] for s in b14["seeds"]}
anchors = {"gauss_k1_vs_bmix_rz": (11.0306, b14w.get("bmix_rz")),
           "gauss_k2_vs_wide_rz": (8.6194, b14w.get("wide_rz")),
           "lag1_k1_vs_node_rz": (8.9475, b14w.get("node_rz"))}
arows = {}
for k, (claim, b14v) in anchors.items():
    ok = b14v is not None and abs(claim - b14v) / b14v < 5e-4
    arows[k] = {"claimed_anchor": claim, "b14_json": b14v, "ok": bool(ok)}
    print(f"  {k}: claim {claim} vs b14 {b14v} -> {'OK' if ok else 'FAIL'}")
OUT["sections"]["anchors"] = arows

# ---------------- (4) P2 endpoint arithmetic ----------------
print("=== (4) P2 endpoints f1 / f2 / wd ===")
eps_rows = []
for tag, st, w_claim in (
        ("f1_rgauss", "m5_12_b12_hard_f1_1_state.npz", 7.3755),
        ("f2_shell", "m5_12_b12_hard_f2_1_state.npz", 6.9869),
        ("wd_wide", "m5_12_b12_hard_wd_1_state.npz", 7.455)):
    p = os.path.join(DATA, st)
    if not os.path.exists(p):
        print(f"  {tag}: MISSING {st}")
        continue
    X, pin = load_x(p)
    a2 = a2_free(X, pin)
    s0, q2, wb = probe(X)
    q2m, q2p = q2_split(X)
    bg5 = bg5_noether(X, wb, h, WSC)
    swing = (bg5["H_max"] - bg5["H_min"]) / s0
    row = {"tag": tag, "state": st, "omega_re": wb, "omega_claim": w_claim,
           "rel_omega": abs(wb - w_claim) / w_claim,
           "S0": s0, "Q2": q2, "Q2_mix": q2m, "Q2_pos": q2p,
           "a2_re": a2, "a2_rel_err_vs_star": abs(a2 / 0.3037246495 - 1.0),
           "H_mean_over_S0": bg5["H_mean"] / s0,
           "H_swing_over_S0": swing}
    eps_rows.append(row)
    print(f"  {tag}: w={wb:.4f} (claim {w_claim}) Q2={q2:+.5f} "
          f"(mix {q2m:+.4f} pos {q2p:+.4f}) a2={a2:.7f} "
          f"H_swing/S0={swing:.3f} H_mean/S0={bg5['H_mean']/s0:.2e}")
OUT["sections"]["p2_endpoints"] = eps_rows

OUT["wall_s"] = round(time.time() - t0, 1)
path = os.path.join(DATA, "m5_12_audit_b15_reprobe.json")
with open(path, "w") as f:
    json.dump(OUT, f, indent=1)
print(f"[done] wall={OUT['wall_s']}s json -> {os.path.basename(path)}")
