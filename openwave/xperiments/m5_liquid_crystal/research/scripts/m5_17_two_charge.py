"""M5.17 phase C: the TWO-CHARGE Coulomb anchor (Duda's 2026-07-03 prescription).

Prescription (m5_4h_convo_2026.07.03.md, verbatim): "For Coulomb we rather
need two such charges in various distances - for large we get anchor for
Coulomb (uniaxial should suffice), for small femtometer-scale we should get
running coupling which should bring some details of potential."

CONFIGURATION (axisymmetric: both defects ON the z-axis, so the exact
equivariant (rho, z) reduction of m5_17_energy.py applies unchanged)
    Two hedgehog cores at z = -d/2 and z = +d/2. Uniaxial director ansatz
    (his "uniaxial should suffice") via tilt-angle superposition:
        Theta(rho, z) = theta_1 + q2 . theta_2,
        theta_i = atan2(rho, z - z_i),  q2 = +1 (like charges) or -1
        (hedgehog / anti-hedgehog),
        n = (sin Theta, 0, cos Theta) at phi = 0,
        M_sp = s(r_1) s(r_2) . n n^T   (each core melts: s = 1 - e^{-(r/rc)^2}).
    q2 = +1: total degree 2, both charges alike, Coulomb REPULSION expected.
    q2 = -1: total degree 0, opposite charges, ATTRACTION; far field ->
    uniform vacuum n = z_hat (exactly representable, zero azimuthal energy).

THE PREDICTION UNDER THE M5.16 LOCK (pre-registered)
    The M5.16 single-defect match set  32 pi c2 / r  ==  alpha hbar c / 2r,
    i.e.  c2 = alpha hbar c / 64 pi.  Two unit charges at distance d have
    EM interaction  +/- alpha hbar c / d, which in grid units (c2 = 1) is
        E_int(d) = q2 . 64 pi / d  ~  q2 . 201.06 / d .
    Extraction: fit  E_pair(d) = E0 + A / d  on the large-d branch (the
    constant E0 absorbs the two d-independent core self-energies and the
    d-independent part of the finite-box tail). GATES:
      C0  ansatz reduces exactly to the single melted hedgehog when the
          second charge is switched off (q2 = 0, d = 0)
      C1  large-d (d >= D_FIT_MIN) fit: sign(A) == q2 and |A / (q2 64 pi) - 1|
          reported; pre-registered consistency band 10% for the ANTIPAIR
          (its far field is vacuum, the cleanest); like-pair reported
      C2  pinned-core RELAXED energies at selected d reproduce the fixed-
          ansatz A within the fit's own scatter (relaxation must not move
          the far-field physics; cores frozen -> self-energy still cancels)
      C3  the running-coupling readout: alpha_eff(d)/alpha ==
          |E_pair(d) - E0| . d / (64 pi), reported for ALL d down to core
          overlap, in fm via the beta = 1 lock scale (0.2495 fm / grid unit)
    A genuine gap between A and 64 pi at large d is a first-class result
    (it would say the two-charge coupling differs from the self-energy
    coupling); the gate is the REPORT, not agreement by fiat.

POTENTIAL: the LOCKED beta = 1 calibration (m5_16_axisym_b100_n96.json):
    cscale_used = 3.7705544498939964e-3, a = (3b - 4c)/2, autochi OFF here
    (the potential is fixed by the lock; this run TESTS it, it must not
    retune it).

Run (from research/scripts/):
    python m5_17_two_charge.py fixed  [NR NZ]      # E(d) curve, both signs
    python m5_17_two_charge.py relax  [NR NZ] --sign -1 --dlist 12,16,24,32
Outputs: ../data/m5_17_two_charge_<mode>*.json (small; no file > 1 MB).
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
os.makedirs(DATA, exist_ok=True)
sys.path.insert(0, HERE)

from m5_17_energy import (  # noqa: E402
    PI, G_TIME, ldg_coeffs, cell_weights, curvature_density_np,
    potential_density_np, total_energy_np, energy_gradient_np,
    grid_coords, hedgehog_field,
)

# the LOCKED beta = 1 potential (m5_16_axisym_b100_n96.json, autochi result)
CSCALE_LOCK = 3.7705544498939964e-3
BETA_LOCK = 1.0
RC_CORE = 8.0                      # the M5.16 seed core scale (fixed, d-independent)
ELL_FM = 0.2495                    # fm per grid unit (beta = 1 m_e lock)

MODE = sys.argv[1] if len(sys.argv) > 1 else "fixed"
_pos = [a for a in sys.argv[2:] if not a.startswith("--")]
NR = int(_pos[0]) if len(_pos) > 0 else 96
NZ = int(_pos[1]) if len(_pos) > 1 else 192
H = 1.0


def _flag(name, default, cast=float):
    for i, a in enumerate(sys.argv):
        if a == "--" + name and i + 1 < len(sys.argv):
            return cast(sys.argv[i + 1])
    return default


SIGN = _flag("sign", -1, int)
DLIST = _flag("dlist", "12,16,24,32", str)
ITERS = _flag("iters", 3000, int)
D_FIT_MIN = _flag("dfitmin", 16.0)


def pair_field(R, Z, d, r_c, q2, g_time=G_TIME):
    """two-charge tilt-superposition ansatz (docstring above); q2 = 0 switches
    the second charge off (single hedgehog at z = -d/2, gate C0)."""
    z1, z2 = -0.5 * d, +0.5 * d
    th1 = np.arctan2(R, Z - z1)
    th2 = np.arctan2(R, Z - z2)
    Th = th1 + q2 * th2
    r1 = np.sqrt(R ** 2 + (Z - z1) ** 2)
    r2 = np.sqrt(R ** 2 + (Z - z2) ** 2)
    s1 = 1.0 - np.exp(-((r1 / r_c) ** 2))
    s2 = np.ones_like(r2) if q2 == 0 else 1.0 - np.exp(-((r2 / r_c) ** 2))
    s = s1 * s2
    n1 = np.sin(Th)
    n3 = np.cos(Th)
    Mnp = np.zeros(R.shape + (4, 4))
    Mnp[..., 1, 1] = s * n1 * n1
    Mnp[..., 1, 3] = s * n1 * n3
    Mnp[..., 3, 1] = s * n1 * n3
    Mnp[..., 3, 3] = s * n3 * n3
    Mnp[..., 0, 0] = g_time
    return Mnp


def gate_c0():
    """q2 = 0, d = 0: the ansatz must equal the single melted hedgehog at the
    origin EXACTLY (same formulas through a different code path)."""
    R, Z = grid_coords(NR, NZ, H)
    Mp = pair_field(R, Z, 0.0, RC_CORE, 0)
    Mh = hedgehog_field(R, Z, RC_CORE)
    # atan2-vs-division constructions agree to fp rounding, not bit-exactly
    mx = float(np.max(np.abs(Mp - Mh)))
    return {"gate": "C0_single_limit", "ok": bool(mx < 1e-12), "max_abs": mx}


def coulomb_fit(ds, Es, dmin):
    """least-squares  E(d) = E0 + A/d  on d >= dmin; returns E0, A, rms."""
    ds = np.asarray(ds, float)
    Es = np.asarray(Es, float)
    m = ds >= dmin
    X = np.stack([np.ones(m.sum()), 1.0 / ds[m]], axis=1)
    coef, *_ = np.linalg.lstsq(X, Es[m], rcond=None)
    resid = Es[m] - X @ coef
    return float(coef[0]), float(coef[1]), float(np.sqrt(np.mean(resid ** 2)))


def run_fixed():
    a, b, c, vvac = ldg_coeffs(BETA_LOCK, CSCALE_LOCK)
    R, Z = grid_coords(NR, NZ, H)
    t0 = time.time()
    gates = [gate_c0()]
    print(f"[{'PASS' if gates[0]['ok'] else 'FAIL'}] C0_single_limit "
          f"max_abs={gates[0]['max_abs']:.2e}")
    E_single = total_energy_np(hedgehog_field(R, Z, RC_CORE), a, b, c, 1.0, H, vvac)
    ds = [4.0, 6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 36.0, 40.0]
    out = {"task": "M5.17", "script": "m5_17_two_charge.py", "mode": "fixed",
           "convention": "Duda index-0: D=diag(g,1,delta,0)",
           "grid": {"NR": NR, "NZ": NZ, "h": H},
           "params": {"beta": BETA_LOCK, "cscale": CSCALE_LOCK, "a": a, "b": b,
                      "c": c, "vvac": vvac, "rc_core": RC_CORE,
                      "d_fit_min": D_FIT_MIN},
           "prediction": {"A_grid_units": 64.0 * PI,
                          "statement": "E_int = q2 * 64*pi*c2/d from the "
                          "M5.16 single-defect Coulomb lock c2 = alpha*hbar*c/(64*pi)"},
           "E_single_same_box": E_single, "ell_fm_per_grid": ELL_FM,
           "gates": gates, "curves": {}}
    for q2, name in ((-1, "antipair"), (+1, "likepair")):
        Es = []
        for d in ds:
            E = total_energy_np(pair_field(R, Z, d, RC_CORE, q2),
                                a, b, c, 1.0, H, vvac)
            Es.append(E)
        E0, A, rms = coulomb_fit(ds, Es, D_FIT_MIN)
        Apred = q2 * 64.0 * PI
        run_alpha = [abs(E - E0) * d / (64.0 * PI) for d, E in zip(ds, Es)]
        out["curves"][name] = {
            "q2": q2, "d": ds, "E_pair": Es,
            "fit_E0": E0, "fit_A": A, "fit_rms": rms,
            "A_over_prediction": A / Apred,
            "sign_ok": bool(np.sign(A) == q2),
            "alpha_eff_over_alpha": run_alpha,
            "d_fm": [d * ELL_FM for d in ds],
        }
        print(f"[fixed:{name}] A={A:+.2f} pred={Apred:+.2f} "
              f"ratio={A / Apred:.4f} rms={rms:.3e} E0={E0:.3f}")
    out["wall_s"] = round(time.time() - t0, 1)
    path = os.path.join(DATA, "m5_17_two_charge_fixed.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {path}")
    return out


def run_relax():
    """pinned-core relax at each d: outer boundary + core disks (r_i < r_pin)
    frozen at the seed; everything else relaxes under the locked potential.
    The frozen cores keep the self-energy d-independent, so the d-fit still
    isolates the interaction."""
    from m5_16_axisym import fire_relax, pin_mask   # driver utilities
    a, b, c, vvac = ldg_coeffs(BETA_LOCK, CSCALE_LOCK)
    R, Z = grid_coords(NR, NZ, H)
    r_pin = 2.5 * H
    ds = [float(x) for x in DLIST.split(",")]
    rows = []
    for d in ds:
        M0 = pair_field(R, Z, d, RC_CORE, SIGN)
        z1, z2 = -0.5 * d, +0.5 * d
        r1 = np.sqrt(R ** 2 + (Z - z1) ** 2)
        r2 = np.sqrt(R ** 2 + (Z - z2) ** 2)
        pin = pin_mask(NR, NZ) | (r1 < r_pin) | (r2 < r_pin)
        free4 = (~pin)[..., None, None].astype(float)
        w = cell_weights(NR, NZ, H)
        wfull = np.ones((NR, NZ))
        wfull[: NR - 1, 1:-1] = w
        precond = (1.0 / wfull)[..., None, None]

        def egf(MM):
            return (total_energy_np(MM, a, b, c, 1.0, H, vvac),
                    energy_gradient_np(MM, a, b, c, 1.0, H, vvac))

        t0 = time.time()
        Mf, hist = fire_relax(M0, egf, free4, precond, max_iter=ITERS,
                              tol_rel=1e-4)
        E_seed, E_rel = hist["E"][0], hist["E"][-1]
        # melt bridge diagnostic (annihilation channel watch, antipair)
        msp = Mf[: NR - 1, 1:-1, 1:4, 1:4]
        s_cell = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
        mid = s_cell[: int(4 / H), :]          # near-axis strip
        rows.append({"d": d, "E_seed": E_seed, "E_relaxed": E_rel,
                     "drop": E_seed - E_rel,
                     "gnorm_decades": float(np.log10(
                         hist["gnorm"][0] / (hist["gnorm"][-1] + 1e-300))),
                     "melt_min_axis_strip": float(np.min(mid)),
                     "wall_s": round(time.time() - t0, 1)})
        print(f"[relax q2={SIGN} d={d:g}] E {E_seed:.3f} -> {E_rel:.3f} "
              f"(drop {E_seed - E_rel:.3f}) decades="
              f"{rows[-1]['gnorm_decades']:.1f} wall={rows[-1]['wall_s']}s")
    E0, A, rms = coulomb_fit([r["d"] for r in rows],
                             [r["E_relaxed"] for r in rows],
                             min(r["d"] for r in rows))
    Apred = SIGN * 64.0 * PI
    out = {"task": "M5.17", "mode": "relax", "sign": SIGN,
           "grid": {"NR": NR, "NZ": NZ, "h": H},
           "params": {"beta": BETA_LOCK, "cscale": CSCALE_LOCK,
                      "rc_core": RC_CORE, "r_pin": r_pin, "iters": ITERS},
           "rows": rows, "fit_E0": E0, "fit_A": A, "fit_rms": rms,
           "A_over_prediction": A / Apred}
    tag = "anti" if SIGN < 0 else "like"
    path = os.path.join(DATA, f"m5_17_two_charge_relax_{tag}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[relax:{tag}] A={A:+.2f} pred={Apred:+.2f} ratio={A / Apred:.4f}")
    print(f"json -> {path}")
    return out


if __name__ == "__main__":
    if MODE == "fixed":
        run_fixed()
    elif MODE == "relax":
        run_relax()
    else:
        print("modes: fixed [NR NZ] | relax [NR NZ] --sign -1 --dlist 12,16,24,32"
              " --iters 3000")
