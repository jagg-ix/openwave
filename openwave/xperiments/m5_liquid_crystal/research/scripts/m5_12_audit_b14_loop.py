"""M5.12 block-14 ADVERSARIAL AUDIT, part 2: the loop transplant (claim N4).

  (a) is the n32 object resolved enough to BE a loop? Ring/winding readout
      of the forged seed at n32 / n48 / n96 (same construction, finer
      grids), plus the saved seed npz and the live chain checkpoint.
  (b) does the chain preserve loop topology or relax toward the hedgehog
      sector? Winding + melt depth + M0 distances (checkpoint vs loop seed
      vs hedgehog seed).
  (c) is loop S0 = 217.6 vs hedgehog 69 meaningful? S0 relaxation
      trajectory from the chain's own progress records.

Run:  python3 -u m5_12_audit_b14_loop.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
from scipy.ndimage import map_coordinates

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import grid_coords                                     # noqa: E402
from m5_16_axisym import hedgehog_field                                  # noqa: E402
from m5_12_dressed import to_covariant                                   # noqa: E402
from m5_12_loop import loop_field, ring_readout                          # noqa: E402
from m5_12_d3a_bvp import shat, x_pack                                   # noqa: E402
from m5_12_d3b_newton import wscale_at                                   # noqa: E402


def director_angle_at(M, pts_rho, pts_z, nr, nz, h):
    """bilinear-interpolated meridional director angle theta = atan2(n3,n1)
    at physical points; n = top eigenvector of the (1,3)x(1,3) spatial
    subblock (the equivariant plane)."""
    ir = pts_rho / h - 0.5
    iz = pts_z / h + nz / 2.0 - 0.5
    comp = {}
    for (a, b) in ((1, 1), (1, 3), (3, 3)):
        comp[(a, b)] = map_coordinates(M[..., a, b], [ir, iz], order=1)
    thetas = []
    for k in range(len(pts_rho)):
        m2 = np.array([[comp[(1, 1)][k], comp[(1, 3)][k]],
                       [comp[(1, 3)][k], comp[(3, 3)][k]]])
        wv, vv = np.linalg.eigh(m2)
        n = vv[:, -1]
        thetas.append(np.arctan2(n[1], n[0]))
    return np.array(thetas)


def nematic_winding(M, c_rho, c_z, rad, nr, nz, h, npts=180):
    """nematic winding number q around the circle (c_rho, c_z, rad):
    accumulate the director angle mod pi; q = total/(2 pi)."""
    ang = np.linspace(0.0, 2.0 * np.pi, npts, endpoint=False)
    pr = c_rho + rad * np.cos(ang)
    pz = c_z + rad * np.sin(ang)
    if np.any(pr < 0.5 * h) or np.any(pr > (nr - 1) * h):
        return None
    th = director_angle_at(M, pr, pz, nr, nz, h)
    tot = 0.0
    for k in range(len(th)):
        d = th[(k + 1) % len(th)] - th[k]
        while d > np.pi / 2:
            d -= np.pi
        while d < -np.pi / 2:
            d += np.pi
        tot += d
    return tot / (2.0 * np.pi)


OUT = {"script": "m5_12_audit_b14_loop.py", "sections": {}}
h = 1.0
t0 = time.time()

# ---------- (a) forged-seed resolution study ----------
print("=== (a) loop seed structure vs grid ===")
rows = []
for n in (32, 48, 96):
    nz = 2 * n
    scale = n / 96.0
    R0, rc = 16.0 * scale, 8.0 * scale
    R, Z = grid_coords(n, nz, h)
    M = to_covariant(loop_field(R, Z, R0, 0.5, rc))
    rr = ring_readout(M, n, nz, h)
    winds = {}
    for frac in (0.5, 1.0):
        w = nematic_winding(M, R0, 0.0, frac * rc, n, nz, h)
        winds[f"q_at_{frac}rc"] = w
    row = {"nr": n, "R0": R0, "rc": rc, **rr, **winds}
    rows.append(row)
    print(f"  n{n}: R0={R0:.2f} rc={rc:.2f} ring=({rr['ring_rho']:.2f},"
          f"{rr['ring_z']:.2f}) min_s={rr['min_s']:.4f} "
          f"q(rc/2)={winds['q_at_0.5rc']} q(rc)={winds['q_at_1.0rc']}")
# hedgehog control: winding around an off-axis circle not enclosing origin
n, nz = 32, 64
R, Z = grid_coords(n, nz, h)
Mh = to_covariant(hedgehog_field(R, Z, 8.0 * 32 / 96))
qh = nematic_winding(Mh, 16.0 * 32 / 96, 0.0, 0.5 * 8.0 * 32 / 96, n, nz, h)
print(f"  hedgehog control n32, same circle: q={qh}")
OUT["sections"]["a_seed_resolution"] = {"rows": rows,
                                        "hedgehog_control_q": qh}

# ---------- saved seed npz + chain checkpoint ----------
print("=== (b) saved seed vs live chain checkpoint ===")
nr, nz = 32, 64
scale = 32 / 96.0
R0, rc = 16.0 * scale, 8.0 * scale
seed = np.load(os.path.join(DATA, "m5_12_b14_seed_loop_bmix_n32.npz"))
M0s = seed["M0"].astype(np.float64)
rr_s = ring_readout(M0s, nr, nz, h)
q_s = nematic_winding(M0s, R0, 0.0, rc, nr, nz, h)
print(f"  seed npz:  ring=({rr_s['ring_rho']:.2f},{rr_s['ring_z']:.2f}) "
      f"min_s={rr_s['min_s']:.4f} q(rc)={q_s}")
ck_path = os.path.join(DATA, "m5_12_b12_hard_lp_1_state_ck.npz")
sec_b = {"seed": {**rr_s, "q_at_rc": q_s}}
if os.path.exists(ck_path):
    ck = np.load(ck_path)
    M0c = ck["M0"].astype(np.float64)
    rr_c = ring_readout(M0c, nr, nz, h)
    # winding around the seed ring AND around the current melt minimum
    q_c_seedring = nematic_winding(M0c, R0, 0.0, rc, nr, nz, h)
    q_c_ownring = nematic_winding(M0c, rr_c["ring_rho"], rr_c["ring_z"],
                                  rc, nr, nz, h)
    # M0 distances (plain Frobenius over all cells) vs both seeds
    R, Z = grid_coords(nr, nz, h)
    Mhed = to_covariant(hedgehog_field(R, Z, rc))
    d_loop = float(np.sqrt(np.sum((M0c - M0s) ** 2)))
    d_hedge = float(np.sqrt(np.sum((M0c - Mhed) ** 2)))
    norm_gap = float(np.sqrt(np.sum((M0s - Mhed) ** 2)))
    sec_b["checkpoint"] = {**rr_c, "q_at_seed_ring": q_c_seedring,
                           "q_at_own_ring": q_c_ownring,
                           "omega_ck": float(ck["omega"][0]),
                           "dist_to_loop_seed": d_loop,
                           "dist_to_hedgehog_seed": d_hedge,
                           "seed_to_hedgehog_dist": norm_gap}
    print(f"  chain ck:  ring=({rr_c['ring_rho']:.2f},{rr_c['ring_z']:.2f})"
          f" min_s={rr_c['min_s']:.4f} q(seed ring)={q_c_seedring} "
          f"q(own ring)={q_c_ownring} omega={float(ck['omega'][0]):.4f}")
    print(f"  |M0_ck - loop_seed|={d_loop:.3f}  "
          f"|M0_ck - hedgehog|={d_hedge:.3f}  "
      f"|loop_seed - hedgehog|={norm_gap:.3f}")
else:
    print("  [gap] no lp checkpoint yet")
OUT["sections"]["b_chain_state"] = sec_b

# ---------- (c) S0 meaningfulness ----------
print("=== (c) S0: seed level vs relaxation trajectory ===")
prog_path = os.path.join(DATA, "m5_12_b12_hard_lp_1_progress.json")
sec_c = {}
wsc = wscale_at(nr, nz, h, rc)
# S0 of the two M0s WITHOUT harmonics (background energy comparison)
Zb = np.zeros_like(M0s)
X_loop_M0 = x_pack(M0s, [Zb.copy(), Zb.copy()], [Zb.copy(), Zb.copy()])
R, Z = grid_coords(nr, nz, h)
Mhed = to_covariant(hedgehog_field(R, Z, rc))
X_hed_M0 = x_pack(Mhed, [Zb.copy(), Zb.copy()], [Zb.copy(), Zb.copy()])
s0_loop_bg = shat(X_loop_M0, 0.0, h, wsc)
s0_hed_bg = shat(X_hed_M0, 0.0, h, wsc)
sec_c["S0_background_loop_seed"] = s0_loop_bg
sec_c["S0_background_hedgehog_seed"] = s0_hed_bg
print(f"  background-only S0: loop seed {s0_loop_bg:.3f}  "
      f"hedgehog seed {s0_hed_bg:.3f}")
if os.path.exists(prog_path):
    prog = json.load(open(prog_path))
    traj = [(r["iter"], r["S0"], r["omega_bal"], r["F_norm"])
            for r in prog["hist"]]
    sec_c["chain_S0_trajectory"] = traj
    for it, s0v, wv, fv in traj:
        print(f"  chain iter {it}: S0={s0v:.3f} w_bal={wv:.4f} |F|={fv:.1f}")
OUT["sections"]["c_S0"] = sec_c

OUT["wall_s"] = round(time.time() - t0, 1)
path = os.path.join(DATA, "m5_12_audit_b14_loop.json")
with open(path, "w") as f:
    json.dump(OUT, f, indent=1)
print(f"[done] wall={OUT['wall_s']}s json -> {os.path.basename(path)}")
