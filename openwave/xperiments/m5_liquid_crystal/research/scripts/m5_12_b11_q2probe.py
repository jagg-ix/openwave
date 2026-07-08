"""M5.12 block 11: Q2-sign probe for the breather seed classes.

The audit (m5_12_audit_b11.json, C4/T6) proved the exact structure
    Shat(X, omega) = S0(X) - omega^2 Q2(X)
and that mixing-free harmonics have Q2 >= 0 at ANY amplitude, so no
free-period orbit exists in that class (the action balance needs
dS/domega = Shat/omega to have a root, impossible while Q2 >= 0 with
S0 > 0). The open question this probe answers: does the TIME-MIXING
(0i boost sector) seed class carry Q2 < 0, i.e. does the amplitude
ladder have anywhere to go?

Q2 is read off exactly: Q2 = S0 - Shat(omega=1) = Shat(0) - Shat(1).
Probes: the bmix seed (0i radial boost bump), the mixing-free block-10b
seed (control: must be >= 0), and an eps scan on the bmix class.

Run:  python m5_12_b11_q2probe.py [--nr 32] [--eps 0.15]
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import grid_coords                                      # noqa: E402
from m5_16_axisym import hedgehog_field                                   # noqa: E402
from m5_12_dressed import to_covariant                                    # noqa: E402
from m5_12_d3a_bvp import shat, x_pack                                    # noqa: E402
from m5_12_d3b_newton import wscale_at                                    # noqa: E402


def _flag(name, default, cast=float):
    for i, a in enumerate(ARGV):
        if a == "--" + name and i + 1 < len(ARGV):
            return cast(ARGV[i + 1])
    return default


def seed(nr, nz, h, eps, mix):
    """the m5_12_d3b_newton breather seed, both classes (kept in sync)."""
    scale = nr / 96.0
    rc_seed, w_b = 8.0 * scale, 8.0 * scale
    R, Z = grid_coords(nr, nz, h)
    M4 = to_covariant(hedgehog_field(R, Z, rc_seed))
    r2 = R ** 2 + Z ** 2
    bump = np.exp(-r2 / (w_b ** 2))[..., None, None]
    A1 = np.zeros_like(M4)
    if mix:
        rr = np.sqrt(r2) + 1e-12
        b2 = bump[..., 0, 0]
        A1[..., 0, 1] = A1[..., 1, 0] = eps * b2 * R / rr
        A1[..., 0, 3] = A1[..., 3, 0] = eps * b2 * Z / rr
    else:
        A1[..., 1:4, 1:4] = eps * bump * M4[..., 1:4, 1:4]
    return x_pack(M4, [A1, np.zeros_like(M4)],
                  [np.zeros_like(M4), np.zeros_like(M4)])


def q2_of(X, h, wscale):
    s0 = shat(X, 0.0, h, wscale)
    s1 = shat(X, 1.0, h, wscale)
    return s0, s0 - s1          # S0, Q2


def load_state(path, Nt=2):
    d = np.load(path)
    M0 = d["M0"].astype(np.float64)
    As = [d[f"A{k+1}"].astype(np.float64) for k in range(Nt)
          if f"A{k+1}" in d]
    Bs = [d[f"B{k+1}"].astype(np.float64) for k in range(Nt)
          if f"B{k+1}" in d]
    return x_pack(M0, As, Bs), float(d["omega"][0])


def main():
    nr = int(_flag("nr", 32, int))
    eps = _flag("eps", 0.15)
    state = _flag("state", None, str)
    nz, h = 2 * nr, 1.0
    wscale = wscale_at(nr, nz, h, 8.0 * nr / 96)
    if state:
        # Q2/S0 readout of a SAVED endpoint state: the balance diagnosis
        # c_omega(w) = -w*Q2 - S0/w has a root at w_bal = sqrt(S0/|Q2|)
        # iff Q2 < 0
        X, om = load_state(state)
        s0, q2 = q2_of(X, h, wscale)
        rec = {"state": os.path.basename(state), "omega": om, "S0": s0,
               "Q2": q2, "Q2_negative": bool(q2 < 0),
               "w_balance": (float(np.sqrt(s0 / -q2)) if q2 < 0 and s0 > 0
                             else None),
               "c_om_at_omega": float(-om * q2 - s0 / om)}
        print(f"[q2-state] {rec['state']}  omega={om:.4f}  S0={s0:+.4f}  "
              f"Q2={q2:+.6f}  w_bal={rec['w_balance']}  "
              f"c_om={rec['c_om_at_omega']:+.4f}")
        path = os.path.join(DATA, "m5_12_b11_q2state.json")
        with open(path, "w") as f:
            json.dump(rec, f, indent=2)
        print(f"json -> {os.path.basename(path)}")
        return
    out = {"task": "M5.12 block 11", "script": "m5_12_b11_q2probe.py",
           "nr": nr, "identity": "Shat = S0 - omega^2 Q2 (audit-verified)",
           "probes": []}
    for mix, label in ((True, "bmix_0i_boost"), (False, "mixfree_spatial")):
        for e in (eps, 2 * eps, 4 * eps):
            X = seed(nr, nz, h, e, mix)
            s0, q2 = q2_of(X, h, wscale)
            rec = {"class": label, "eps": e, "S0": s0, "Q2": q2,
                   "Q2_negative": bool(q2 < 0)}
            out["probes"].append(rec)
            print(f"[q2] {label:>16} eps={e:.2f}  S0={s0:+.4f}  "
                  f"Q2={q2:+.6f}  negative={q2 < 0}")
    path = os.path.join(DATA, "m5_12_b11_q2probe.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
