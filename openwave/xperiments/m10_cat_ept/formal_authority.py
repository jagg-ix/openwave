"""Exact Physlib authority pin for the M10 model."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any, Mapping

FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "agent/dirac-cartan-2i-compton-yukawa"
FORMAL_HEAD = "b894a64e180b46c9bc1dd7e0100422b0cc6fb143"
FORMAL_PULL_REQUEST = 41
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/BinaryIcosahedralDiracSpinor.lean",
        "sha": "6c42acf2f9b1ca2d22a6332adbd0a49d5d700f6d",
        "theorem": "binary_icosahedral_dirac_spinor_assembly",
        "establishes": "four-complex-component 2I action, total-density preservation, and central-pair descent",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EinsteinCartanAxialTorsion.lean",
        "sha": "e963184d07364916516955a0d1bc403255227228",
        "theorem": "dirac_cartan_axial_elimination_assembly",
        "establishes": "canonical gamma-matrix axial current, algebraic Cartan equation, and Hehl-Datta contact reduction",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/DiracCartanComptonYukawaBridge.lean",
        "sha": "f5aedde7ca9f4b378b70fa093f322bb5185722e3",
        "theorem": "dirac_cartan_2I_compton_yukawa_assembly",
        "establishes": "binary-icosahedral Dirac density, Yukawa-Compton mass shell, entropy rate, and Dirac-sourced Cartan assembly",
    },
)


def canonical_payload() -> dict[str, Any]:
    return {
        "repository": FORMAL_REPOSITORY,
        "branch": FORMAL_BRANCH,
        "head": FORMAL_HEAD,
        "pull_request": FORMAL_PULL_REQUEST,
        "sources": [dict(source) for source in FORMAL_SOURCES],
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(
        json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
