"""M5.18 phase B figure: the universal spectral potential vs the quartic LdG.

Panels:
  (a) V(s) along the uniaxial path M_sp = s n n^T (both potentials at their
      calibrated scales): the melt-economics picture in one curve.
  (b) relaxed melt profiles s(r): LdG beta=1 (M5.16 b100_n96) vs spectral
      (m5_18 n96), same instrument, same grid.
  (c) r_half physical prediction: spectral (3 grids) vs the LdG beta-flat
      band vs Faber's 3.075 fm.
Reads the JSONs; run AFTER `m5_18_spectral.py calibrate`.
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
os.makedirs(PLOTS, exist_ok=True)

BLUE = "#2a78d6"      # spectral (the new potential)
ORANGE = "#c65a1e"    # quartic LdG (the superseded instrument)
GRAY = "#666666"

R_HALF_FABER = 3.0754
R_HALF_LDG = 2.926


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


lock = load("m5_18_spectral_lock.json")
spec96 = load("m5_18_spectral_spec_n96.json")
ldg96 = load("m5_16_axisym_b100_n96.json")
w = spec96["params"]["wscale"]
csc = ldg96["params"]["cscale_used"]

fig, ax = plt.subplots(1, 3, figsize=(14, 4.4))

# (a) V(s) on the uniaxial path
s = np.linspace(-0.15, 1.5, 400)
v_spec = w * ((s - 1) ** 2 + (s ** 2 - 1) ** 2 + (s ** 3 - 1) ** 2)
b_l = 1.0 * csc
c_l = csc
a_l = 0.5 * (3 * b_l - 4 * c_l)
vvac = a_l - b_l + c_l
v_ldg = a_l * s ** 2 - b_l * s ** 3 + c_l * s ** 4 - vvac
ax[0].plot(s, 1e3 * v_spec, color=BLUE, lw=2,
           label=f"spectral (melt cost 3w = {3e3 * w:.2f}e-3)")
ax[0].plot(s, 1e3 * v_ldg, color=ORANGE, lw=2,
           label=f"LdG beta=1 (melt cost c-b/2 = {5e2 * csc:.2f}e-3)")
ax[0].axvline(1.0, ls=":", c=GRAY, lw=0.8)
ax[0].axhline(0.0, ls=":", c=GRAY, lw=0.8)
ax[0].set_xlabel("uniaxial amplitude s")
ax[0].set_ylabel("V(s) x 1e3  (sim units, calibrated scales)")
ax[0].set_title("(a) melt economics, ABSOLUTE (same instrument)")
ax[0].legend(fontsize=8)

# (b) relaxed melt profiles
rb_s = np.array(spec96["obs"]["r_bins"])
sp_s = np.array(spec96["obs"]["s_profile"])
rb_l = np.array(ldg96["obs"]["r_bins"])
sp_l = np.array(ldg96["obs"]["s_profile"])
ax[1].plot(rb_l, sp_l, color=ORANGE, lw=2.6, label="LdG beta=1 (M5.16)")
ax[1].plot(rb_s, sp_s, color=BLUE, lw=1.4, ls="--", label="spectral (M5.18)")
ax[1].axhline(1.0, ls=":", c=GRAY, lw=0.8)
ax[1].set_xlim(0, 30)
ax[1].set_xlabel("r (grid units)")
ax[1].set_ylabel("s(r)")
ax[1].set_title("(b) relaxed melt profiles COINCIDE, n96")
ax[1].legend(fontsize=8)

# (c) r_half prediction
ns = [r["NR"] for r in lock["rows"]]
rh = [r["r_half_phys_fm"] for r in lock["rows"]]
ax[2].plot(ns, rh, "o-", color=BLUE, lw=1.8, label="spectral r_half(NR)")
ax[2].axhline(R_HALF_FABER, ls="--", c="r",
              label=f"Faber arctan ({R_HALF_FABER} fm)")
ax[2].axhline(R_HALF_LDG, ls="--", c=ORANGE,
              label=f"LdG beta-flat ({R_HALF_LDG} fm)")
ax[2].set_xlabel("NR (resolution)")
ax[2].set_ylabel("r_half (fm)")
ax[2].set_title("(c) parameter-free electron size prediction")
ax[2].legend(fontsize=8)

fig.suptitle("M5.18: Duda's universal spectral potential on the calibrated "
             "static instrument (Coulomb + m_e anchors, delta = 0)",
             fontweight="bold")
fig.tight_layout()
path = os.path.join(PLOTS, "m5_18_spectral.png")
fig.savefig(path, dpi=110)
print(f"plot -> {path}")
