"""M5.12 block-14 ADVERSARIAL AUDIT, part 1: seed probe re-derivation.

Covers claims N2 (class coverage), N3 (object-scale statement), N5
(pre-registered honesty check on the scaling).

Independence: seeds are FORGED HERE from the documented formulas (not via
m5_12_b14_seeds.forge_seed); amplitudes and channel splits are computed
with local code. The 4D action evaluator shat() is the shared instrument
(independently verified by the block-11 audit) and is used as the meter.

Sections:
  A  re-derive every published number (12 seed npz files + grid + fixobj)
  B  A1/B1 degeneracy: structural test with RANDOM fields + phase shifts
  C  out-of-battery seeds at matched a2 (radial node, 2x/0.5x width,
     second-harmonic A2, combined spatial+mix, 2x-object bigrc)
  D  grid series at FIXED wscale (does the per-grid recalibration inject
     the trend?)
  E  grid series at MATCHED amplitude (raw a2 and weighted a2w)
  F  TRUE h-refinement (n32 h=1 vs n48 h=2/3 vs n64 h=1/2, same object,
     same box): the discretization test fixobj does NOT perform
  G  scaling fits + the honest extrapolation arithmetic

Run:  python3 -u m5_12_audit_b14_probe.py
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

from m5_17_energy import grid_coords, cell_weights, hedgehog_field       # noqa: E402
from m5_16_axisym import pin_mask                                        # noqa: E402
from m5_12_dressed import to_covariant                                   # noqa: E402
from m5_12_loop import loop_field                                        # noqa: E402
from m5_12_d3a_bvp import shat, x_pack                                   # noqa: E402
from m5_12_d3b_newton import wscale_at                                   # noqa: E402

BAND = (1.0712, 1.15)          # M5.8 band: sqrt(70/61) analytic anchor


# ---------------- local (audit-owned) helpers ----------------
def my_probe(X, h, wscale):
    s0 = shat(X, 0.0, h, wscale)
    q2 = s0 - shat(X, 1.0, h, wscale)
    wb = float(np.sqrt(s0 / -q2)) if (q2 < 0 and s0 > 0) else None
    return {"S0": s0, "Q2": q2, "omega_bal": wb}


def my_a2(X, pin):
    fr = ~pin
    return float(np.sum(X["A"][0][fr] ** 2) + np.sum(X["B"][0][fr] ** 2))


def my_a2_weighted(X, pin, h):
    nr, nz = X["M0"].shape[:2]
    wfull = np.ones((nr, nz))
    wfull[: nr - 1, 1:-1] = cell_weights(nr, nz, h)
    fr = ~pin
    return float(np.sum(wfull[fr][:, None, None]
                        * (X["A"][0][fr] ** 2 + X["B"][0][fr] ** 2)))


def my_forge(nr, nz, h, eps, rc, wb, profile="gauss", comp="rz",
             harmonic=1, M0_kind="hedgehog", loop_R0=None):
    """audit-owned forge from the documented formulas."""
    R, Z = grid_coords(nr, nz, h)
    if M0_kind == "loop":
        M4 = to_covariant(loop_field(R, Z, loop_R0, 0.5, rc))
        d = np.sqrt((R - loop_R0) ** 2 + Z ** 2) + 1e-12
        rad2 = d ** 2
        cr, cz = (R - loop_R0) / d, Z / d
    else:
        M4 = to_covariant(hedgehog_field(R, Z, rc))
        rad2 = R ** 2 + Z ** 2
        rr = np.sqrt(rad2) + 1e-12
        cr, cz = R / rr, Z / rr
    if profile == "gauss":
        b2 = np.exp(-rad2 / wb ** 2)
    elif profile == "node":
        b2 = np.exp(-rad2 / wb ** 2) * (1.0 - 2.0 * rad2 / wb ** 2)
    else:
        raise ValueError(profile)
    H = np.zeros_like(M4)
    if comp in ("rz", "r"):
        H[..., 0, 1] = H[..., 1, 0] = eps * b2 * cr
    if comp in ("rz", "z"):
        H[..., 0, 3] = H[..., 3, 0] = eps * b2 * cz
    if comp == "spatial+rz":
        H[..., 0, 1] = H[..., 1, 0] = eps * b2 * cr
        H[..., 0, 3] = H[..., 3, 0] = eps * b2 * cz
        H[..., 1:4, 1:4] += (eps * b2)[..., None, None] * M4[..., 1:4, 1:4]
    pin = pin_mask(nr, nz)
    H[pin] = 0.0
    Zb = np.zeros_like(M4)
    if harmonic == 1:
        X = x_pack(M4, [H, Zb.copy()], [Zb.copy(), Zb.copy()])
    else:
        X = x_pack(M4, [Zb.copy(), H], [Zb.copy(), Zb.copy()])
    return X, pin


def rescale_h(X, pin, a2_star, harmonic=1):
    k = harmonic - 1
    fr = ~pin
    a2 = float(np.sum(X["A"][k][fr] ** 2) + np.sum(X["B"][k][fr] ** 2))
    fac = np.sqrt(a2_star / a2)
    X["A"][k] = X["A"][k] * fac
    X["B"][k] = X["B"][k] * fac
    return X


def load_state(path):
    d = np.load(path)
    Nt = 2
    return x_pack(d["M0"].astype(np.float64),
                  [d[f"A{k+1}"].astype(np.float64) for k in range(Nt)],
                  [d[f"B{k+1}"].astype(np.float64) for k in range(Nt)])


OUT = {"script": "m5_12_audit_b14_probe.py", "sections": {}}
t_all = time.time()
h = 1.0
EPS = 0.164896465616327


# ================= A: re-derive published numbers =================
print("=== A: re-derivation of published probe numbers ===")
secA = {"seeds": [], "grid": [], "fixobj": []}
pub32 = json.load(open(os.path.join(DATA, "m5_12_b14_seeds_n32.json")))
pub48 = json.load(open(os.path.join(DATA, "m5_12_b14_seeds_n48.json")))
for pub, nr in ((pub32, 32), (pub48, 48)):
    nz = 2 * nr
    wsc = wscale_at(nr, nz, h, 8.0 * nr / 96)
    pin = pin_mask(nr, nz)
    for rec in pub["seeds"]:
        p = os.path.join(DATA, rec["state"])
        X = load_state(p)
        pr = my_probe(X, h, wsc)
        a2 = my_a2(X, pin)
        row = {"class": rec["class"], "nr": nr,
               "S0_rel_err": abs(pr["S0"] - rec["S0"]) / abs(rec["S0"]),
               "Q2_rel_err": abs(pr["Q2"] - rec["Q2"]) / abs(rec["Q2"]),
               "wbal_rel_err": (abs(pr["omega_bal"] - rec["omega_bal"])
                                / rec["omega_bal"]),
               "a2_rel_err": abs(a2 - rec["a2"]) / rec["a2"]}
        secA["seeds"].append(row)
        print(f"  {rec['class']:>10} n{nr}: S0err={row['S0_rel_err']:.2e} "
              f"Q2err={row['Q2_rel_err']:.2e} wberr={row['wbal_rel_err']:.2e}"
              f" a2err={row['a2_rel_err']:.2e}")
# grid + fixobj series: reforge with MY forge and compare
for mode, rcfix in (("grid", None), ("fixobj", 8.0 * 32 / 96)):
    pub = json.load(open(os.path.join(DATA, f"m5_12_b14_{mode}.json")))
    for rec in pub["series"]:
        n = rec["nr"]
        nz = 2 * n
        rc = rcfix if rcfix else 8.0 * n / 96
        wsc = wscale_at(n, nz, h, rc)
        X, pin = my_forge(n, nz, h, EPS, rc, rc)
        pr = my_probe(X, h, wsc)
        row = {"nr": n, "mode": mode,
               "S0_rel_err": abs(pr["S0"] - rec["S0"]) / abs(rec["S0"]),
               "Q2_rel_err": abs(pr["Q2"] - rec["Q2"]) / abs(rec["Q2"]),
               "wbal_rel_err": (abs(pr["omega_bal"] - rec["omega_bal"])
                                / rec["omega_bal"])}
        secA[mode].append(row)
        print(f"  {mode} n{n}: S0err={row['S0_rel_err']:.2e} "
              f"Q2err={row['Q2_rel_err']:.2e} "
              f"wberr={row['wbal_rel_err']:.2e}")
OUT["sections"]["A_rederive"] = secA


# ================= B: A1/B1 degeneracy structure =================
print("=== B: A1/B1 degeneracy (structural or coincidence?) ===")
nr, nz = 24, 48
wsc = wscale_at(nr, nz, h, 8.0 * nr / 96)
rng = np.random.default_rng(7)
R, Z = grid_coords(nr, nz, h)
M4 = to_covariant(hedgehog_field(R, Z, 2.0))
pin = pin_mask(nr, nz)
P = rng.normal(size=M4.shape)
P = 0.5 * (P + np.swapaxes(P, -1, -2)) * 0.1
P *= np.exp(-(R ** 2 + Z ** 2) / 16.0)[..., None, None]
P[pin] = 0.0
Zb = np.zeros_like(M4)
secB = {"tests": []}
for phi0 in (0.0, 0.5 * np.pi, 0.3, 1.234):
    A1 = P * np.cos(phi0)
    B1 = P * np.sin(phi0)
    X = x_pack(M4, [A1, Zb], [B1, Zb])
    pr = my_probe(X, h, wsc)
    secB["tests"].append({"phi0": phi0, **pr})
    print(f"  phi0={phi0:.4f}: S0={pr['S0']:.12f} Q2={pr['Q2']:+.12e}")
s0s = [t["S0"] for t in secB["tests"]]
q2s = [t["Q2"] for t in secB["tests"]]
secB["S0_spread_rel"] = (max(s0s) - min(s0s)) / abs(s0s[0])
secB["Q2_spread_rel"] = (max(q2s) - min(q2s)) / abs(q2s[0])
secB["argument"] = (
    "M(t) with (A1,B1) = (P cos phi0, P sin phi0) is a time translation "
    "t -> t - phi0/omega of the phi0 = 0 field. Shat is a period average; "
    "the N_s = 4Nt+2 = 10 trapezoid is exact for trig polynomials to "
    "degree 9 and the density is degree <= 8 (quartic in Nt = 2 "
    "harmonics), so the quadrature inherits exact translation invariance. "
    "A1 -> B1 is phi0 = pi/2: degeneracy holds for ANY seed, structurally.")
print(f"  spread over phi0: S0 {secB['S0_spread_rel']:.2e}  "
      f"Q2 {secB['Q2_spread_rel']:.2e}")
OUT["sections"]["B_degeneracy"] = secB


# ================= C: out-of-battery seeds, matched a2 =================
print("=== C: out-of-battery seeds at matched a2 (n32) ===")
nr, nz = 32, 64
rc32 = 8.0 * 32 / 96
wsc = wscale_at(nr, nz, h, rc32)
a2_star = pub32["a2_star"]
cands = [
    ("bmix_rz_CTRL", dict(profile="gauss", comp="rz", rc=rc32, wb=rc32)),
    ("node_rz", dict(profile="node", comp="rz", rc=rc32, wb=rc32)),
    ("wide_rz_2x", dict(profile="gauss", comp="rz", rc=rc32, wb=2 * rc32)),
    ("narrow_rz_0p5x", dict(profile="gauss", comp="rz", rc=rc32,
                            wb=0.5 * rc32)),
    ("combo_spatial_rz", dict(profile="gauss", comp="spatial+rz", rc=rc32,
                              wb=rc32)),
    ("bigrc_rz_2x", dict(profile="gauss", comp="rz", rc=2 * rc32,
                         wb=2 * rc32)),
    ("A2harm_rz", dict(profile="gauss", comp="rz", rc=rc32, wb=rc32,
                       harmonic=2)),
]
secC = {"a2_star": a2_star, "wscale": wsc, "rows": []}
for name, kw in cands:
    harm = kw.pop("harmonic", 1)
    X, pin = my_forge(nr, nz, h, EPS, kw["rc"], kw["wb"],
                      profile=kw["profile"], comp=kw["comp"], harmonic=harm)
    X = rescale_h(X, pin, a2_star, harmonic=harm)
    pr = my_probe(X, h, wsc)
    row = {"name": name, "harmonic": harm, **pr}
    if harm == 2 and pr["omega_bal"]:
        row["omega_eff"] = 2.0 * pr["omega_bal"]
    secC["rows"].append(row)
    eff = f" (eff {row.get('omega_eff'):.4f})" if harm == 2 else ""
    wb_s = f"{pr['omega_bal']:.4f}" if pr["omega_bal"] else "None"
    print(f"  {name:>18}: S0={pr['S0']:9.4f} Q2={pr['Q2']:+.6f} "
          f"w_bal={wb_s}{eff}")
OUT["sections"]["C_out_of_battery"] = secC


# ================= D: grid series at FIXED wscale =================
print("=== D: grid series, per-grid wscale vs FIXED wscale ===")
wsc32 = wscale_at(32, 64, h, 8.0 * 32 / 96)
secD = {"wscale_fixed": wsc32, "rows": []}
for n in (24, 32, 48, 64):
    nz = 2 * n
    rc = 8.0 * n / 96
    X, pin = my_forge(n, nz, h, EPS, rc, rc)
    wsc_own = wscale_at(n, nz, h, rc)
    pr_own = my_probe(X, h, wsc_own)
    pr_fix = my_probe(X, h, wsc32)
    row = {"nr": n, "wscale_own": wsc_own,
           "own": pr_own, "fixed_wscale": pr_fix}
    secD["rows"].append(row)
    wb_o = pr_own["omega_bal"]
    wb_f = pr_fix["omega_bal"]
    print(f"  n{n}: wsc {wsc_own:.4e} vs fixed {wsc32:.4e} | "
          f"w_bal own={wb_o:.4f} fixed={wb_f:.4f} | "
          f"S0 own={pr_own['S0']:.3f} fixed={pr_fix['S0']:.3f}")
OUT["sections"]["D_fixed_wscale"] = secD


# ================= E: grid series at MATCHED amplitude =================
print("=== E: grid series at matched amplitude (raw a2 / weighted a2w) ===")
a2w_ref = None
secE = {"rows": []}
for n in (24, 32, 48, 64):
    nz = 2 * n
    rc = 8.0 * n / 96
    wsc_own = wscale_at(n, nz, h, rc)
    X, pin = my_forge(n, nz, h, EPS, rc, rc)
    a2_raw = my_a2(X, pin)
    a2w_raw = my_a2_weighted(X, pin, h)
    if n == 32:
        a2w_ref = a2w_raw
    # matched raw a2
    Xa = rescale_h({"M0": X["M0"], "A": [a.copy() for a in X["A"]],
                    "B": [b.copy() for b in X["B"]]}, pin, a2_star)
    pr_a = my_probe(Xa, h, wsc_own)
    secE["rows"].append({"nr": n, "a2_raw": a2_raw, "a2w_raw": a2w_raw,
                         "matched_raw_a2": pr_a})
    print(f"  n{n}: a2_raw={a2_raw:.4f} a2w_raw={a2w_raw:.4f} | "
          f"matched-a2 w_bal={pr_a['omega_bal']:.4f} "
          f"S0={pr_a['S0']:.3f} Q2={pr_a['Q2']:+.6f}")
# weighted matching second pass (needs a2w_ref from n32)
for n, row in zip((24, 32, 48, 64), secE["rows"]):
    nz = 2 * n
    rc = 8.0 * n / 96
    wsc_own = wscale_at(n, nz, h, rc)
    X, pin = my_forge(n, nz, h, EPS, rc, rc)
    fac = np.sqrt(a2w_ref / row["a2w_raw"])
    X["A"][0] *= fac
    pr_w = my_probe(X, h, wsc_own)
    row["matched_weighted_a2w"] = pr_w
    print(f"  n{n}: matched-a2w w_bal={pr_w['omega_bal']:.4f} "
          f"S0={pr_w['S0']:.3f} Q2={pr_w['Q2']:+.6f}")
OUT["sections"]["E_matched_amplitude"] = secE


# ================= F: TRUE h-refinement =================
print("=== F: true h-refinement (same object rc=2.667, same 32x64 box) ===")
rcf = 8.0 * 32 / 96
secF = {"rows": []}
for n, hh in ((32, 1.0), (48, 2.0 / 3.0), (64, 0.5)):
    nz = 2 * n
    wsc_own = wscale_at(n, nz, hh, rcf)
    X, pin = my_forge(n, nz, hh, EPS, rcf, rcf)
    pr_own = my_probe(X, hh, wsc_own)
    pr_fix = my_probe(X, hh, wsc32)
    secF["rows"].append({"nr": n, "h": hh, "wscale_own": wsc_own,
                         "own": pr_own, "fixed_wscale32": pr_fix})
    print(f"  n{n} h={hh:.4f}: wsc={wsc_own:.4e} | own S0={pr_own['S0']:.4f}"
          f" Q2={pr_own['Q2']:+.6f} w_bal={pr_own['omega_bal']:.4f} | "
          f"fixed-wsc w_bal={pr_fix['omega_bal']:.4f}")
OUT["sections"]["F_h_refinement"] = secF


# ================= G: fits + honest extrapolation =================
print("=== G: scaling fits + extrapolation arithmetic ===")
ns = np.array([24.0, 32.0, 48.0, 64.0])
wb_fixed_eps = np.array([r["own"]["omega_bal"] for r in secD["rows"]])
wb_matched = np.array([r["matched_raw_a2"]["omega_bal"]
                       for r in secE["rows"]])
prod = wb_fixed_eps * ns
# log-log fit on fixed-eps family
p = np.polyfit(np.log(ns), np.log(wb_fixed_eps), 1)
slope, logc = p[0], p[1]
nr_cross = {b: float(np.exp((np.log(b) - logc) / slope)) for b in BAND}
a2_at_cross = {str(b): a2_star * (nr_cross[b] / 32.0) ** 2 for b in BAND}
ratio_matched = np.array([r["matched_raw_a2"]["S0"]
                          / -r["matched_raw_a2"]["Q2"]
                          for r in secE["rows"]])
secG = {
    "fixed_eps_wbal_times_nr": prod.tolist(),
    "fixed_eps_loglog_slope": slope,
    "nr_needed_for_band_fixed_eps": {str(k): v for k, v in nr_cross.items()},
    "a2_at_band_crossing_fixed_eps": a2_at_cross,
    "matched_a2_wbal_series": wb_matched.tolist(),
    "matched_a2_S0_over_Q2_series": ratio_matched.tolist(),
    "wbal_at_n96_object_fixed_eps_extrap": float(
        np.exp(logc + slope * np.log(96.0))),
}
print(f"  fixed-eps w_bal*nr: {[f'{v:.1f}' for v in prod]}")
print(f"  log-log slope: {slope:.4f}")
print(f"  nr needed for band (fixed eps): "
      f"{ {k: f'{v:.0f}' for k, v in nr_cross.items()} }")
print(f"  a2 at crossing: { {k: f'{v:.1f}' for k, v in a2_at_cross.items()} }")
print(f"  matched-a2 w_bal series: {[f'{v:.3f}' for v in wb_matched]}")
print(f"  matched-a2 S0/|Q2|: {[f'{v:.1f}' for v in ratio_matched]}")
print(f"  fixed-eps extrapolated w_bal at n96 object: "
      f"{secG['wbal_at_n96_object_fixed_eps_extrap']:.3f}")
OUT["sections"]["G_scaling"] = secG

OUT["wall_s"] = round(time.time() - t_all, 1)
path = os.path.join(DATA, "m5_12_audit_b14_probe.json")
with open(path, "w") as f:
    json.dump(OUT, f, indent=1)
print(f"[done] wall={OUT['wall_s']}s json -> {os.path.basename(path)}")
