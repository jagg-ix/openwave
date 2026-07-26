import numpy as np

from openwave.xperiments.m9_cat_ept.charged_field_tools import periodic_contour_winding
from openwave.xperiments.m9_cat_ept.coupled_gauge_spinor_hartree_action import (
    CoupledActionConfig,
    project_winding_sector,
)
from openwave.xperiments.m9_cat_ept.formalization_m101_extension import (
    FORMAL_BRANCH,
    FORMAL_HEAD,
    FORMAL_SOURCES,
    PHYSLIB_ROOT_BLOB,
    canonical_payload,
)


def test_current_formal_head_and_sources_are_exact():
    assert FORMAL_BRANCH == "entropic-physlib-linear-full"
    assert FORMAL_HEAD == "acdbe8ce6456e66837bd18604cf3107d3181c4de"
    assert len(PHYSLIB_ROOT_BLOB) == 40
    assert len(FORMAL_SOURCES) == 11
    assert len({row["path"] for row in FORMAL_SOURCES}) == 11
    assert all(len(row["blob"]) == 40 for row in FORMAL_SOURCES)
    assert canonical_payload()["policy"]["scope_boundaries_are_mandatory"]


def test_natural_unit_newton_map_and_winding_projection_close():
    cfg = CoupledActionConfig(iterations=20, neutral_iterations=100)
    assert cfg.newton_coupling == cfg.hbar * cfg.light_speed * cfg.inference_width**4
    x, y, z = (
        -cfg.half_width
        + cfg.spacing * np.arange(cfg.points, dtype=np.float64)
        for _ in range(3)
    )
    xx, yy, zz = np.meshgrid(x, y, z, indexing="ij")
    amplitude = np.exp(-(xx * xx + yy * yy + zz * zz) / 6.0)
    spinor = np.zeros((2, cfg.points, cfg.points, cfg.points), dtype=np.complex128)
    spinor[0] = amplitude
    projected = project_winding_sector(spinor, cfg)
    norm = float(np.sum(np.abs(projected) ** 2) * cfg.spacing**3)
    winding = periodic_contour_winding(
        projected[0], cfg.spacing, radius=cfg.contour_radius
    )
    assert abs(norm - 1.0) < 2e-12
    assert winding["integer_winding"] == cfg.winding
    assert winding["quantization_error"] < 5e-3
