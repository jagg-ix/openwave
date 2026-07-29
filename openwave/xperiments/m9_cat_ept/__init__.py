"""M9 CAT/EPT stable evidence and latest model-integration lineages.

The stable public compatibility aliases remain at M9.126. The latest integrated
model is M9.140, which exposes the existing particle, coupled dynamics, and
Physlib authority surfaces behind one canonical API without promoting a
physical particle identity.

The package keeps compatibility with NumPy 2.x, where ``numpy.trapz`` was
removed in favor of ``numpy.trapezoid``. Historical M9 modules still call the
former name, so provide the exact numerical alias at package import time.
"""
from __future__ import annotations

import numpy as np

if not hasattr(np, "trapz"):
    np.trapz = np.trapezoid  # type: ignore[attr-defined]

STABLE_ALIAS_MILESTONE = "M9.126"
LATEST_MILESTONE = "M9.140"
CURRENT_MILESTONE = LATEST_MILESTONE

STABLE_REGISTRATION_SCHEMA = "openwave.model-registration.v29"
STABLE_CONFORMANCE_SCHEMA = "openwave.m9.models-conformance.v22"
LATEST_REGISTRATION_SCHEMA = "openwave.model-registration.latest.v1"
LATEST_CONFORMANCE_SCHEMA = "openwave.m9.models-conformance.latest.v1"

# Historical names are retained for downstream compatibility.
CURRENT_REGISTRATION_SCHEMA = STABLE_REGISTRATION_SCHEMA
CURRENT_CONFORMANCE_SCHEMA = STABLE_CONFORMANCE_SCHEMA
