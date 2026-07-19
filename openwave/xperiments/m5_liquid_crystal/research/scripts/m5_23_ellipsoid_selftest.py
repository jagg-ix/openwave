"""
M5.23 — headless selftest of the VIZ.5 ellipsoid-shell glyph kernel (Stage A).

Builds a small TensorField, seeds a biaxial hedgehog at the center, runs
eigen_decompose, fills the shell center, calls update_ellipsoid_glyphs and
machine-checks the buffers (the task's goal-loop gate; design + decisions:
../tasks/m5_23_task_details.md):

  1. GEOMETRY   — every active glyph midpoint sits exactly on the S² shell
                  (radius R around the center, normalized render coords), and
                  the direction set matches the Fibonacci-sphere reference
  2. EIGENFRAME — every shaft is parallel to director_nhat at the snapped
                  voxel with length = base * clamp(lam1); the delta bar is
                  parallel to director_mid with length = base * clamp(lam2);
                  shaft and bar are orthogonal
  3. PHYSICS    — on a hedgehog shell the director is radial: |u . n| ~ 1 for
                  the overwhelming majority of directions (the disclination
                  melt neighborhoods exempt)
  4. HYGIENE    — slots beyond (n_centers, n_active) are zeroed; no NaNs;
                  the delta-density knob re-runs cleanly at another n_active

Also renders a matplotlib preview of the shell (research/plots/) so the look
can be checked without launching the GGUI app.

USAGE (repo root):
    python -m openwave.xperiments.m5_liquid_crystal.research.scripts.m5_23_ellipsoid_selftest
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import taichi as ti
from mpl_toolkits.mplot3d.art3d import Line3DCollection

ti.init(arch=ti.cpu, log_level=ti.WARN)

import openwave.xperiments.m5_liquid_crystal.engine1_seeds as seeds  # noqa: E402
import openwave.xperiments.m5_liquid_crystal.engine2_pde as pde  # noqa: E402
import openwave.xperiments.m5_liquid_crystal.engine4_render as viz  # noqa: E402
from openwave.xperiments.m5_liquid_crystal.medium import TensorField  # noqa: E402

# ----------------------------------------------------------------
# Setup: small grid + biaxial hedgehog at the exact center
# ----------------------------------------------------------------
UNIVERSE = [1.0e-15, 1.0e-15, 1.0e-15]  # arbitrary (geometry only)
TARGET_VOXELS = 40**3

wf = TensorField(UNIVERSE, TARGET_VOXELS)
nx, ny, nz = wf.nx, wf.ny, wf.nz
cx, cy, cz = (nx - 1) // 2, (ny - 1) // 2, (nz - 1) // 2
r0_vox = 0.10 * wf.max_grid_size
rhoc_vox = 3.0
BIAX_DELTA = 0.3
seeds.seed_biaxial_hedgehog_M(wf, cx, cy, cz, r0_vox, rhoc_vox, BIAX_DELTA)
pde.eigen_decompose(wf)

wf.ellipsoid_centers[0] = [float(cx), float(cy), float(cz)]
wf.ellipsoid_n_centers[None] = 1

R_FRAC = 0.22
R_VOX = R_FRAC * wf.max_grid_size
BASE_LEN = 0.02
N_ACTIVE = 162

viz.update_ellipsoid_glyphs(wf, R_VOX, BASE_LEN, N_ACTIVE)

verts = wf.ellipsoid_glyph_vertices.to_numpy()
cols = wf.ellipsoid_glyph_colors.to_numpy()
dverts = wf.ellipsoid_delta_vertices.to_numpy()
dcols = wf.ellipsoid_delta_colors.to_numpy()
nhat = wf.director_nhat.to_numpy()
nmid = wf.director_mid.to_numpy()
evals = wf.eigenvalues.to_numpy()

max_dim = float(wf.max_grid_size)
center_n = (np.array([cx, cy, cz], np.float64) + 0.5) / max_dim  # normalized center
fails = []
total = [0]


def check(name, ok, detail=""):
    total[0] += 1
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name}" + (f" ({detail})" if detail else ""))
    if not ok:
        fails.append(name)


# Fibonacci reference directions (must match the kernel closed form)
d_idx = np.arange(N_ACTIVE, dtype=np.float64)
zf = 1.0 - 2.0 * (d_idx + 0.5) / N_ACTIVE
rho = np.sqrt(np.maximum(1.0 - zf * zf, 0.0))
phi = d_idx * np.pi * (3.0 - np.sqrt(5.0))
u_ref = np.stack([rho * np.cos(phi), rho * np.sin(phi), zf], axis=1)

a = verts[0 : 2 * N_ACTIVE : 2].astype(np.float64)  # shaft base, active block (center 0)
b = verts[1 : 2 * N_ACTIVE : 2].astype(np.float64)  # shaft tip
mid = 0.5 * (a + b)
da = dverts[0 : 2 * N_ACTIVE : 2].astype(np.float64)
db = dverts[1 : 2 * N_ACTIVE : 2].astype(np.float64)
dmid = 0.5 * (da + db)

# ---- 1. GEOMETRY ----
r_norm = np.linalg.norm(mid - center_n, axis=1) * max_dim
check(
    "geometry: shell radius",
    np.allclose(r_norm, R_VOX, atol=1e-3),
    f"midpoint radius {r_norm.min():.4f}..{r_norm.max():.4f} vox vs R={R_VOX:.4f}",
)
u_meas = (mid - center_n) / np.linalg.norm(mid - center_n, axis=1, keepdims=True)
check(
    "geometry: Fibonacci direction set",
    np.allclose(u_meas, u_ref, atol=1e-4),
    f"max direction mismatch {np.abs(u_meas - u_ref).max():.2e}",
)
check(
    "geometry: delta bar centered on the same shell point",
    np.allclose(dmid, mid, atol=1e-6),
)

# ---- 2. EIGENFRAME ----
snap = np.clip(
    np.round(np.array([cx, cy, cz], np.float64) + R_VOX * u_ref).astype(int),
    0,
    [nx - 1, ny - 1, nz - 1],
)
ii, jj, kk = snap[:, 0], snap[:, 1], snap[:, 2]
n_vox = nhat[ii, jj, kk].astype(np.float64)
m_vox = nmid[ii, jj, kk].astype(np.float64)
l_vox = evals[ii, jj, kk].astype(np.float64)

shaft_v = b - a
shaft_len = np.linalg.norm(shaft_v, axis=1)
exp_shaft = BASE_LEN * np.clip(l_vox[:, 0], 0.12, 2.0)
check(
    "eigenframe: shaft length = base*clamp(lam1)",
    np.allclose(shaft_len, exp_shaft, atol=1e-5),
    f"max err {np.abs(shaft_len - exp_shaft).max():.2e}",
)
cross_n = np.linalg.norm(np.cross(shaft_v, n_vox), axis=1) / (shaft_len + 1e-15)
check("eigenframe: shaft parallel to director_nhat", np.all(cross_n < 1e-4))

bar_v = db - da
bar_len = np.linalg.norm(bar_v, axis=1)
exp_bar = BASE_LEN * np.clip(l_vox[:, 1], 0.12, 2.0)
check(
    "eigenframe: delta length = base*clamp(lam2)",
    np.allclose(bar_len, exp_bar, atol=1e-5),
    f"max err {np.abs(bar_len - exp_bar).max():.2e}",
)
cross_m = np.linalg.norm(np.cross(bar_v, m_vox), axis=1) / (bar_len + 1e-15)
check("eigenframe: delta bar parallel to director_mid", np.all(cross_m < 1e-4))
ortho = np.abs(np.sum(shaft_v * bar_v, axis=1)) / (shaft_len * bar_len + 1e-15)
check(
    "eigenframe: shaft orthogonal to delta bar",
    np.all(ortho < 1e-3),
    f"max |cos| {ortho.max():.2e}",
)

# ---- 3. PHYSICS ----
radial = np.abs(np.sum(u_ref * n_vox, axis=1))  # |u . n|, 1 = radial director
frac_radial = float(np.mean(radial > 0.9))
check(
    "physics: hedgehog shell director is radial",
    frac_radial >= 0.90,
    f"{100 * frac_radial:.1f}% of directions with |u.n| > 0.9 "
    f"(disclination-axis neighborhoods exempt)",
)

# ---- 4. HYGIENE ----
tail = slice(2 * N_ACTIVE, None)
check(
    "hygiene: slots beyond (n_centers, n_active) zeroed",
    np.all(verts[tail] == 0.0)
    and np.all(cols[tail] == 0.0)
    and np.all(dverts[tail] == 0.0)
    and np.all(dcols[tail] == 0.0),
)
check(
    "hygiene: no NaNs",
    np.all(np.isfinite(verts)) and np.all(np.isfinite(dverts)),
)
N2 = 642  # density re-run at the ceiling
viz.update_ellipsoid_glyphs(wf, R_VOX, BASE_LEN, N2)
v2 = wf.ellipsoid_glyph_vertices.to_numpy()
m2 = 0.5 * (v2[0 : 2 * N2 : 2] + v2[1 : 2 * N2 : 2]).astype(np.float64)
r2 = np.linalg.norm(m2 - center_n, axis=1) * max_dim
check(
    "hygiene: density knob re-run (n=642) stays on shell",
    np.allclose(r2, R_VOX, atol=1e-3) and np.all(v2[2 * N2 :] == 0.0),
)

# ---- 5. MULTI-CENTER (the dipole case: one shell per defect) ----
c2 = np.array([cx - 8, cy, cz], np.float64)
wf.ellipsoid_centers[1] = [float(c2[0]), float(c2[1]), float(c2[2])]
wf.ellipsoid_n_centers[None] = 2
viz.update_ellipsoid_glyphs(wf, R_VOX, BASE_LEN, N_ACTIVE)
v3 = wf.ellipsoid_glyph_vertices.to_numpy()
blk = 2 * wf.ellipsoid_max_dirs  # vertex block per center
m3a = 0.5 * (v3[0 : 2 * N_ACTIVE : 2] + v3[1 : 2 * N_ACTIVE : 2]).astype(np.float64)
m3b = 0.5 * (
    v3[blk : blk + 2 * N_ACTIVE : 2] + v3[blk + 1 : blk + 2 * N_ACTIVE : 2]
).astype(np.float64)
c2n = (c2 + 0.5) / max_dim
r3a = np.linalg.norm(m3a - center_n, axis=1) * max_dim
r3b = np.linalg.norm(m3b - c2n, axis=1) * max_dim
check(
    "multi-center: two shells, each on its own center",
    np.allclose(r3a, R_VOX, atol=1e-3) and np.allclose(r3b, R_VOX, atol=1e-3),
)
wf.ellipsoid_n_centers[None] = 1  # restore for the preview plot

# ----------------------------------------------------------------
# Preview plot (Agg) — the shell at the default density
# ----------------------------------------------------------------
viz.update_ellipsoid_glyphs(wf, R_VOX, BASE_LEN, N_ACTIVE)
verts = wf.ellipsoid_glyph_vertices.to_numpy()
dverts = wf.ellipsoid_delta_vertices.to_numpy()
fig = plt.figure(figsize=(9, 9))
ax = fig.add_subplot(111, projection="3d")
segs = verts[: 2 * N_ACTIVE].reshape(-1, 2, 3)
dsegs = dverts[: 2 * N_ACTIVE].reshape(-1, 2, 3)
ax.add_collection3d(Line3DCollection(segs, colors="#4aa3df", linewidths=1.6))
ax.add_collection3d(Line3DCollection(dsegs, colors="#00e5e5", linewidths=1.2))
ax.scatter(*center_n, color="k", s=18)
lim = (center_n[0] - 1.3 * R_FRAC, center_n[0] + 1.3 * R_FRAC)
ax.set_xlim(lim), ax.set_ylim(lim), ax.set_zlim(lim)
ax.set_box_aspect((1, 1, 1))
ax.set_title(
    f"M5.23 VIZ.5 ellipsoid shell (Stage A lines): biaxial hedgehog, "
    f"{N_ACTIVE} glyphs, R={R_FRAC:.2f}\nblue = director shaft (lam1), cyan = delta bar (lam2)"
)
plot_dir = os.path.join(os.path.dirname(__file__), "..", "plots")
os.makedirs(plot_dir, exist_ok=True)
out = os.path.join(plot_dir, "m5_23_shell_selftest.png")
fig.savefig(out, dpi=110, bbox_inches="tight")
print(f"[plot] {out}")

n_pass = total[0] - len(fails)
print(
    f"\nSELFTEST: {n_pass}/{total[0]} checks passed"
    + (f"; FAILED: {fails}" if fails else ": ALL GREEN")
)
sys.exit(1 if fails else 0)
