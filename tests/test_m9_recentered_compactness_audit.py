import numpy as np

from openwave.xperiments.m9_cat_ept.recentered_compactness_audit import (
    l2_distance,
    recenter_known_translation,
)


def test_known_translation_recenters_exactly():
    reference = np.zeros((8, 8, 8), dtype=np.complex128)
    reference[2, 3, 4] = 1
    moved = np.roll(reference, 3, axis=0)
    assert l2_distance(reference, recenter_known_translation(moved, 3), 1.0) == 0.0