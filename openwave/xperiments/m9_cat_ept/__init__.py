"""M9 CAT/EPT current lineage through M9.133.

The package keeps compatibility with NumPy 2.x, where ``numpy.trapz`` was
removed in favor of ``numpy.trapezoid``. Historical M9 modules still call the
former name, so provide the exact numerical alias at package import time.
"""
from __future__ import annotations

import numpy as np

if not hasattr(np, "trapz"):
    np.trapz = np.trapezoid  # type: ignore[attr-defined]

CURRENT_MILESTONE = "M9.133"
CURRENT_REGISTRATION_SCHEMA = "openwave.model-registration.v29"
CURRENT_CONFORMANCE_SCHEMA = "openwave.m9.models-conformance.v22"
