"""M5.20 phases B/C: endpoint verdicts per the pre-registered classifier.

Per run (JSON trajectory + saved endpoint state):
  - guarded winding reads at the endpoint over r_w in {3,4,5,6,8,10,12}
    centered on the |M13|^2 centroid (the M5.19 audit lesson: single-radius
    mid-slosh reads are unreliable; the verdict uses the endpoint SET);
  - m13_max + the |M13|^2 cloud second moment (is there still a ring core?);
  - the E_abs(t) series: post-transient absorbed fraction + saturation test
    (last-quarter growth vs the classifier);
  - PE_in8 trend (energy leaving the ring neighborhood);
  - the classifier verdict: HELD / UNWOUND / RADIATES / MIXED.

Transient exclusion: window starts at t_w = first local max of KE(t) plus
one echo (t_w doubled), per the plan.

Usage: python m5_20_b1_verdicts.py <run_name> [...] -> ../data/m5_20_verdicts.json
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_20_a1_dynamics import NR, NZ, H, WSCALE           # noqa: E402
from m5_19_d1_relax import ring_by_m13, winding_measure   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

RWS = (3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0)


def endpoint_reads(name):
    st = np.load(os.path.join(DATA, f"m5_20_{name}_state.npz"))
    M = st["M0"].astype(np.float64)
    rd = ring_by_m13(M, NR, NZ, H)
    reads = {}
    for rw in RWS:
        q = winding_measure(M, NR, NZ, H, rd["ring13_rho"], rd["ring13_z"],
                            r_w=rw)
        reads[str(rw)] = None if not np.isfinite(q) else round(float(q), 4)
    # |M13|^2 cloud spread (second moment about the centroid)
    m13 = M[: NR - 1, 1:-1, 1, 3]
    w2 = m13 ** 2
    tot = float(np.sum(w2))
    ri = (np.arange(NR - 1) + 0.5) * H
    zj = (np.arange(1, NZ - 1) - NZ / 2 + 0.5) * H
    RR, ZZ = np.meshgrid(ri, zj, indexing="ij")
    if tot > 1e-30 and np.isfinite(rd["ring13_rho"]):
        spread = float(np.sqrt(np.sum(
            w2 * ((RR - rd["ring13_rho"]) ** 2 + (ZZ - rd["ring13_z"]) ** 2))
            / tot))
    else:
        spread = float("nan")
    return {"ring": rd, "q_reads": reads, "m13_spread": spread}


def classify(name):
    with open(os.path.join(DATA, f"m5_20_{name}.json")) as f:
        d = json.load(f)
    tr = d["trajectory"]
    t = np.array([r["t"] for r in tr])
    ke = np.array([r["KE"] for r in tr])
    ab = np.array([r["E_abs"] for r in tr])
    pe = np.array([r["PE"] for r in tr])
    E0 = tr[0]["PE"]
    # transient window: first local max of KE, doubled
    imax = 1
    for i in range(1, len(ke) - 1):
        if ke[i] >= ke[i - 1] and ke[i] >= ke[i + 1]:
            imax = i
            break
    t_w = 2.0 * t[imax]
    post = t >= t_w
    ep = endpoint_reads(name)
    qs = [v for v in ep["q_reads"].values() if v is not None]
    q_seed = abs(tr[0].get("q_meas") or 0.0)
    q_end_max = max((abs(q) for q in qs), default=0.0)
    held_wind = (len(qs) >= 3 and
                 all(abs(abs(q) - q_seed) < 0.1 for q in qs))
    unwound = (len(qs) >= 3 and q_end_max < 0.1)
    ab_frac = float(ab[-1] / E0) if E0 else 0.0
    ab_post = ab[post]
    growing = (len(ab_post) > 4 and
               (ab_post[-1] - ab_post[-len(ab_post) // 4]) > 0.05 * ab_post[-1]
               and ab_frac > 0.0)
    if d["mode"] == "sponge" and ab_frac > 0.05 and growing:
        verdict = "RADIATES"
    elif unwound:
        verdict = "UNWOUND"
    elif held_wind and (d["mode"] != "sponge" or ab_frac < 0.01):
        verdict = "HELD"
    else:
        verdict = "MIXED"
    return {"name": name, "mode": d["mode"], "variant": d["variant"],
            "E0": E0, "t_window": t_w,
            "PE_end": float(pe[-1]), "KE_end": float(ke[-1]),
            "E_abs_end": float(ab[-1]), "abs_frac": round(ab_frac, 5),
            "abs_growing_last_quarter": bool(growing),
            "endpoint": ep, "q_seed": q_seed,
            "verdict": verdict}


if __name__ == "__main__":
    out = {}
    for name in ARGV:
        try:
            out[name] = classify(name)
            e = out[name]
            print(f"[{name}] {e['verdict']}: abs_frac {e['abs_frac']}, "
                  f"q_reads {e['endpoint']['q_reads']}, "
                  f"m13_spread {e['endpoint']['m13_spread']:.1f}")
        except FileNotFoundError as ex:
            print(f"[{name}] SKIP ({ex})")
    with open(os.path.join(DATA, "m5_20_verdicts.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("wrote m5_20_verdicts.json")
