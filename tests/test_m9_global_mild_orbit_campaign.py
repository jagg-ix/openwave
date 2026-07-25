import numpy as np

from openwave.xperiments.m9_cat_ept.global_mild_orbit_campaign import (
    align_translation,
    phase_align,
)


def test_phase_and_translation_alignment():
    reference = np.zeros((8, 8, 8), dtype=np.complex128)
    reference[3, 3, 3] = 1
    moved = np.roll(reference * np.exp(0.4j), 2, axis=0)
    aligned = phase_align(reference, align_translation(reference, moved), 1.0)
    assert np.linalg.norm(reference - aligned) < 1e-12