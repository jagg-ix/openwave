"""M5.20.1 phase B: biaxial (1, delta, 0) loop seeds + the gated instruments.

Builds on the M5.19/M5.20 stack (m5_19_c1_loop tensor loop + escape blend),
generalized to the biaxial vacuum spectrum (1, delta, 0), c_p = 1 + delta^p.

THE TWO WINDING PAIRINGS (phase-A chosen far fields, m5_20_1_a_theory.py):
    pair_1d : cross-section winds the (1, delta) pair in the meridional
              plane, out-of-plane (azimuthal) 0; two-equal core
              ((1+delta)/2, (1+delta)/2, 0); escape far field
              Me = diag(delta, 0, 1) [rho, phi, z] (-> e3e3^T at delta=0,
              the M5.20 z-escape arm; A_phi background ~ delta).
    pair_d0 : winds (delta, 0), out-of-plane 1; core (1, delta/2, delta/2);
              Me = diag(0, 1, delta) (-> e2e2^T at delta=0, the M5.19/20
              azimuthal arm; A_phi background ~ 1).

INSTRUMENTS (DoD 3, gated here before any production read)
    3a  winding_measure_biax: the (1,3)-block eigenframe angle read
        (theta = 0.5 atan2(2 M13, M11 - M33)) with a degeneracy-gap guard
        + an out-of-plane mixing monitor (max |M12|, |M23| on the circle
        vs the in-plane anisotropy: eigenframe reads are untrusted when
        the wound 2-plane mixes away).
    3b  core_spectrum: the core-equalization diagnostic (his 07-12
        mechanism made measurable): disk-averaged core eigenvalues
        (lam_hi, lam_mid, lam_lo), the two adjacent gaps, and WHICH pair
        sits equalized (gap_top < gap_bot -> the (1, delta) pair).

GATES
    B0  escaped-seed box-independence (3 boxes, rel <= 1e-9) per pairing
    B0b the far field beyond the blend shell is EXACTLY the enumerated
        vacuum (V = 0 to 1e-14)
    B1  winding read on synthetic known-q seeds: |q_meas - q| <= 0.05 at
        r_w in {3,4,5,6}, per (delta, pairing), mixing monitor ~ 0
    B2  core_spectrum reads the SEEDED pairing at t = 0, per (delta,
        pairing)

Run:  python m5_20_1_b_seeds.py
Out:  ../data/m5_20_1_b_gates.json
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import G_TIME, grid_coords                       # noqa: E402
from m5_18_spectral import total_energy_spec_np                    # noqa: E402
from m5_19_c1_loop import loop_field_tensor                        # noqa: E402
from m5_19_d1_relax import ring_by_m13                             # noqa: E402
from m5_12_core_pin import load_wscale                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
WSCALE = load_wscale()
NR, NZ, H = 128, 256, 1.0
NARROW = {"ws": 3.0, "wm": 3.0, "w3": 3.0}


def cps_of(delta):
    return (1.0 + delta, 1.0 + delta ** 2, 1.0 + delta ** 3)


def pairing_spec(delta, pairing):
    """far (lam_p, lam_m, lam3), two-equal core (mu0, nu0), escape vacuum
    diag (rho, phi, z), and the wound-pair anisotropy s_far."""
    if pairing == "pair_1d":
        return {"far": (1.0, delta, 0.0),
                "mu0": (1.0 + delta) / 2.0, "nu0": 0.0,
                "Me": (delta, 0.0, 1.0), "s_far": 1.0 - delta}
    if pairing == "pair_d0":
        return {"far": (delta, 0.0, 1.0),
                "mu0": delta / 2.0, "nu0": 1.0,
                "Me": (0.0, 1.0, delta), "s_far": delta}
    raise ValueError(pairing)


def loop_field_biax(R, Z, R0, q, delta, pairing, ws=NARROW["ws"],
                    wm=NARROW["wm"], w3=NARROW["w3"], shape="tanh",
                    dcut_fac=2.5, wcut_fac=1.0, g_time=G_TIME):
    """biaxial escaped loop: meridional winding of the chosen pair with the
    two-equal regularized core, blended beyond dd ~ dcut to the phase-A
    uniform vacuum Me (the m5_19_c1_loop escape construction, far/Me
    generalized)."""
    sp = pairing_spec(delta, pairing)
    M = loop_field_tensor(R, Z, R0, q, sp["mu0"], sp["nu0"], ws, wm, w3,
                          shape, far=sp["far"], g_time=g_time)
    dd = np.sqrt((R - R0) ** 2 + Z ** 2)
    dcut, wcut = dcut_fac * ws, wcut_fac * ws
    x = np.clip((dd - dcut) / wcut, 0.0, 1.0)
    beta = (x * x * (3 - 2 * x))[..., None, None]
    Me = np.zeros_like(M)
    Me[..., 1, 1], Me[..., 2, 2], Me[..., 3, 3] = sp["Me"]
    out = (1 - beta) * M + beta * Me
    out[..., 0, 0] = g_time
    return out


def winding_measure_biax(Mnp, nr, nz, h, rho_c, z_c, r_w=4.0, npts=720,
                         aniso_min=0.02):
    """the (1,3)-block eigenframe winding read (m5_19_d1_relax
    winding_measure) + the out-of-plane mixing monitor. Returns
    (q_meas, mix_ratio); q_meas = nan when the eigenframe is degenerate
    (aniso < aniso_min) or the wound 2-plane has mixed away
    (mix_ratio > 0.5)."""
    if not np.all(np.isfinite(Mnp)):
        return float("nan"), float("nan")
    ang = np.linspace(0.0, 2.0 * np.pi, npts, endpoint=True)
    rr = rho_c + r_w * np.cos(ang)
    zz = z_c + r_w * np.sin(ang)
    ii = np.clip(np.round(rr / h - 0.5).astype(int), 0, nr - 2)
    jj = np.clip(np.round(zz / h + (nz - 2) / 2 - 0.5).astype(int) + 1, 1,
                 nz - 2)
    m11 = Mnp[ii, jj, 1, 1]
    m33 = Mnp[ii, jj, 3, 3]
    m13 = Mnp[ii, jj, 1, 3]
    m12 = Mnp[ii, jj, 1, 2]
    m23 = Mnp[ii, jj, 2, 3]
    aniso = np.sqrt((m11 - m33) ** 2 + 4.0 * m13 ** 2)
    mix = float(np.max(np.sqrt(m12 ** 2 + m23 ** 2))
                / max(float(np.mean(aniso)), 1e-30))
    if float(np.min(aniso)) < aniso_min or mix > 0.5:
        return float("nan"), mix
    two_theta = np.arctan2(2.0 * m13, m11 - m33)
    dth = np.diff(two_theta)
    dth = (dth + np.pi) % (2.0 * np.pi) - np.pi
    return float(np.sum(dth) / (4.0 * np.pi)), mix


def core_spectrum(Mnp, nr, nz, h, rho_c, z_c, r_avg=1.5):
    """the core-equalization diagnostic: disk-averaged spatial-block
    eigenvalues at the core center + the two adjacent gaps + which pair
    sits equalized (the measured answer to the Q22 pairing half)."""
    if not (np.isfinite(rho_c) and np.isfinite(z_c)):
        return {"lam": [float("nan")] * 3, "gap_top": float("nan"),
                "gap_bot": float("nan"), "equalized": "none"}
    ri = (np.arange(nr - 1) + 0.5) * h
    zj = (np.arange(1, nz - 1) - nz / 2 + 0.5) * h
    RR, ZZ = np.meshgrid(ri, zj, indexing="ij")
    din = (RR - rho_c) ** 2 + (ZZ - z_c) ** 2 < r_avg ** 2
    if not np.any(din):
        return {"lam": [float("nan")] * 3, "gap_top": float("nan"),
                "gap_bot": float("nan"), "equalized": "none"}
    msp = Mnp[: nr - 1, 1:-1, 1:4, 1:4][din]
    mbar = 0.5 * (np.mean(msp, axis=0)
                  + np.mean(np.swapaxes(msp, -1, -2), axis=0))
    lam = np.sort(np.linalg.eigvalsh(mbar))[::-1]
    g_top, g_bot = float(lam[0] - lam[1]), float(lam[1] - lam[2])
    if not np.isfinite(g_top + g_bot):
        eq = "none"
    elif g_top < g_bot:
        eq = "pair_1d"          # the (1, delta) duo sits equalized
    else:
        eq = "pair_d0"          # the (delta, 0) duo sits equalized
    return {"lam": [float(x) for x in lam], "gap_top": g_top,
            "gap_bot": g_bot, "equalized": eq}


# ---------------- gates ----------------
def gate_b0(delta=0.3, R0=17.0, q=0.5):
    out = {}
    for pairing in ("pair_1d", "pair_d0"):
        es = []
        for (nr, nz) in ((128, 256), (192, 384), (256, 512)):
            R, Z = grid_coords(nr, nz, H)
            M = loop_field_biax(R, Z, R0, q, delta, pairing)
            es.append(float(total_energy_spec_np(M, WSCALE, H,
                                                 cps_of(delta))))
        spread = (max(es) - min(es)) / max(abs(es[0]), 1e-30)
        out[pairing] = {"E_by_box": es, "rel_spread": spread}
    ok = all(v["rel_spread"] <= 1e-9 for v in out.values())
    return ok, out


def gate_b0b(deltas=(0.1, 0.3, 0.5), R0=17.0, q=0.5):
    from m5_18_spectral import potential_density_spec_np
    out = {}
    R, Z = grid_coords(NR, NZ, H)
    dd = np.sqrt((R - R0) ** 2 + Z ** 2)[: NR - 1, 1:-1]
    far = dd > 2.5 * NARROW["ws"] + 1.0 * NARROW["ws"] + 0.5
    for delta in deltas:
        for pairing in ("pair_1d", "pair_d0"):
            M = loop_field_biax(R, Z, R0, q, delta, pairing)
            v = potential_density_spec_np(M, 1.0, cps_of(delta))
            out[f"d{delta}_{pairing}"] = float(np.max(np.abs(v[far])))
    ok = all(v < 1e-14 for v in out.values())
    return ok, out


def gate_b1(deltas=(0.1, 0.3, 0.5), R0=17.0, q=0.5):
    R, Z = grid_coords(NR, NZ, H)
    out = {}
    ok = True
    for delta in deltas:
        for pairing in ("pair_1d", "pair_d0"):
            M = loop_field_biax(R, Z, R0, q, delta, pairing)
            rd = ring_by_m13(M, NR, NZ, H)
            reads = {}
            for rw in (3.0, 4.0, 5.0, 6.0):
                qm, mix = winding_measure_biax(M, NR, NZ, H, R0, 0.0,
                                               r_w=rw)
                reads[str(rw)] = {"q": None if not np.isfinite(qm)
                                  else round(qm, 4),
                                  "mix": round(mix, 4)}
            qs = [r["q"] for r in reads.values() if r["q"] is not None]
            good = (len(qs) >= 3 and all(abs(abs(x) - q) <= 0.05
                                         for x in qs)
                    and all(r["mix"] < 0.05 for r in reads.values()))
            ok = ok and good
            out[f"d{delta}_{pairing}"] = {
                "ring_locator": [round(rd["ring13_rho"], 2),
                                 round(rd["ring13_z"], 2)],
                "reads": reads, "pass": bool(good)}
    return ok, out


def gate_b2(deltas=(0.1, 0.3, 0.5), R0=17.0, q=0.5):
    R, Z = grid_coords(NR, NZ, H)
    out = {}
    ok = True
    for delta in deltas:
        for pairing in ("pair_1d", "pair_d0"):
            M = loop_field_biax(R, Z, R0, q, delta, pairing)
            cs = core_spectrum(M, NR, NZ, H, R0, 0.0)
            good = cs["equalized"] == pairing
            ok = ok and good
            out[f"d{delta}_{pairing}"] = {**cs, "pass": bool(good)}
    return ok, out


def run_gates():
    results = {"task": "M5.20.1", "phase": "B", "wscale": WSCALE}
    for name, fn in [("B0", gate_b0), ("B0b", gate_b0b), ("B1", gate_b1),
                     ("B2", gate_b2)]:
        ok, detail = fn()
        results[name] = {"ok": bool(ok), "detail": detail}
        print(f"[{name}] {'PASS' if ok else 'FAIL'}")
    with open(os.path.join(DATA, "m5_20_1_b_gates.json"), "w") as f:
        json.dump(results, f, indent=1, default=float)
    print(json.dumps({k: v["ok"] for k, v in results.items()
                      if isinstance(v, dict) and "ok" in v}, indent=1))
    return results


if __name__ == "__main__":
    run_gates()
