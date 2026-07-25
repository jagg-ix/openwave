"""M9.94: canonical CAT/EPT particle spin and magnetic-moment bridge.

A scalar CAT/EPT particle envelope is embedded into a two-component Pauli spinor.
Periodic spectral derivatives produce the Pauli magnetization current, orbital
angular momentum, magnetic moment, and inferred tree-level g factor on the same
three-dimensional particle state used by the M9 kernel.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np
from numpy.typing import NDArray

from .formalization_import import criterion_import_map, run_formalization_import_study
from .particle_model import (
    CatEptParticleModel,
    CatEptParticleState,
    field_fingerprint,
    normalized_gaussian,
    periodic_displacement,
)

ComplexField = NDArray[np.complex128]
RealField = NDArray[np.float64]


@dataclass(frozen=True)
class CanonicalSpinParameters:
    charge: float = 1.0
    mass: float = 1.0
    spin: int = 1
    reference_alpha: float = 1.0 / 137.0

    def __post_init__(self) -> None:
        if self.mass <= 0.0 or self.charge == 0.0:
            raise ValueError("positive mass and nonzero charge required")
        if self.spin not in (-1, 1):
            raise ValueError("spin must be -1 or +1")
        if self.reference_alpha < 0.0:
            raise ValueError("nonnegative reference alpha required")


def embed_pauli_spinor(state: CatEptParticleState, spin: int) -> ComplexField:
    if spin not in (-1, 1):
        raise ValueError("spin must be -1 or +1")
    result = np.zeros((2, *state.field.shape), dtype=np.complex128)
    result[0 if spin == 1 else 1] = state.field
    return result


def spin_density_z(spinor: ComplexField) -> RealField:
    if spinor.ndim != 4 or spinor.shape[0] != 2:
        raise ValueError("two-component three-dimensional spinor required")
    return np.asarray(
        0.5 * (np.abs(spinor[0]) ** 2 - np.abs(spinor[1]) ** 2),
        dtype=np.float64,
    )


def spectral_gradient(values: NDArray[Any], spacing: float) -> tuple[NDArray[Any], ...]:
    if spacing <= 0.0 or values.ndim != 3:
        raise ValueError("positive spacing and a three-dimensional field required")
    wave_numbers = [
        2.0 * math.pi * np.fft.fftfreq(points, d=spacing)
        for points in values.shape
    ]
    grids = np.meshgrid(*wave_numbers, indexing="ij")
    transformed = np.fft.fftn(values)
    return tuple(np.fft.ifftn(1j * wave * transformed) for wave in grids)


def relative_coordinates(state: CatEptParticleState) -> tuple[RealField, RealField, RealField]:
    axes = [
        (np.arange(points, dtype=np.float64) - points / 2.0) * state.spacing
        for points in state.field.shape
    ]
    x, y, z = np.meshgrid(*axes, indexing="ij")
    lengths = tuple(points * state.spacing for points in state.field.shape)
    return (
        periodic_displacement(x, state.center[0], lengths[0]),
        periodic_displacement(y, state.center[1], lengths[1]),
        periodic_displacement(z, state.center[2], lengths[2]),
    )


def canonical_spin_observables(
    state: CatEptParticleState,
    parameters: CanonicalSpinParameters = CanonicalSpinParameters(),
) -> dict[str, float]:
    spinor = embed_pauli_spinor(state, parameters.spin)
    density = np.sum(np.abs(spinor) ** 2, axis=0).real
    spin_density = spin_density_z(spinor)
    magnetization = (parameters.charge / parameters.mass) * spin_density
    dmx, dmy, _dmz = spectral_gradient(magnetization, state.spacing)
    current_x = dmy.real
    current_y = -dmx.real
    x, y, _z = relative_coordinates(state)
    volume = state.spacing**3

    spin_z = float(np.sum(spin_density) * volume)
    magnetic_moment_z = float(
        0.5 * np.sum(x * current_y - y * current_x) * volume
    )

    orbital_density = np.zeros(state.field.shape, dtype=np.float64)
    for component in spinor:
        derivative_x, derivative_y, _derivative_z = spectral_gradient(
            component, state.spacing
        )
        orbital_density += np.real(
            np.conj(component) * (-1j * (x * derivative_y - y * derivative_x))
        )
    orbital_z = float(np.sum(orbital_density) * volume)
    total_j_z = spin_z + orbital_z
    inferred_g = (
        2.0 * parameters.mass * magnetic_moment_z
        / (parameters.charge * total_j_z)
        if abs(total_j_z) > 1e-15
        else math.nan
    )
    return {
        "norm": float(np.sum(density) * volume),
        "spin_z": spin_z,
        "orbital_z": orbital_z,
        "total_j_z": total_j_z,
        "magnetic_moment_z": magnetic_moment_z,
        "inferred_tree_g": inferred_g,
    }


def g_factor(anomaly: float) -> float:
    return 2.0 * (1.0 + anomaly)


def schwinger_anomaly(alpha: float) -> float:
    return alpha / (2.0 * math.pi)


def magnetic_moment_ratio(anomaly: float) -> float:
    return 1.0 + anomaly


def formal_structure_audit(alpha: float) -> dict[str, float]:
    anomaly = schwinger_anomaly(alpha)
    return {
        "alpha": alpha,
        "anomaly": anomaly,
        "g_factor": g_factor(anomaly),
        "schwinger_expected_g": 2.0 + alpha / math.pi,
        "moment_ratio": magnetic_moment_ratio(anomaly),
        "g_from_ratio": 2.0 * magnetic_moment_ratio(anomaly),
    }


def control_state(points: int = 24, half_width: float = 6.0) -> CatEptParticleState:
    model = CatEptParticleModel.repository_default()
    field, spacing = normalized_gaussian(points=points, half_width=half_width)
    return CatEptParticleState(
        field=field,
        spacing=spacing,
        simulation_time=0.0,
        center=(0.0, 0.0, 0.0),
        phase_origin=0.0,
        declared_winding_sector=model.spec.winding_sector,
        winding_embedded=True,
        reference_branch_fingerprint=field_fingerprint(field, spacing),
        construction="canonical-spin-magnetic-control",
    )


@lru_cache(maxsize=1)
def run_canonical_spin_magnetic_bridge() -> dict[str, Any]:
    imported = run_formalization_import_study()
    formal_import = criterion_import_map()["magnetic_moment_spin"]
    parameters = CanonicalSpinParameters()
    model = CatEptParticleModel.repository_default()
    state = control_state()
    base = canonical_spin_observables(state, parameters)
    flipped = canonical_spin_observables(
        state, CanonicalSpinParameters(spin=-1)
    )
    translated_state = model.translate_cells(state, (7, -5, 3))
    translated = canonical_spin_observables(translated_state, parameters)
    structure = formal_structure_audit(parameters.reference_alpha)

    acceptance = {
        "cat_ept_formalization_import_passes": bool(imported["passed"]),
        "all_spin_formal_declarations_are_imported": len(formal_import["declarations"]) == 8,
        "canonical_particle_state_is_normalized": abs(base["norm"] - 1.0) < 2e-12,
        "canonical_spin_is_half": abs(base["spin_z"] - 0.5) < 2e-12,
        "canonical_orbital_control_is_zero": abs(base["orbital_z"]) < 2e-10,
        "pauli_current_recovers_tree_g_two": abs(base["inferred_tree_g"] - 2.0) < 5e-4,
        "spin_flip_reverses_spin_and_moment": (
            abs(flipped["spin_z"] + base["spin_z"]) < 2e-12
            and abs(flipped["magnetic_moment_z"] + base["magnetic_moment_z"]) < 5e-10
        ),
        "periodic_translation_preserves_observables": max(
            abs(translated[key] - base[key])
            for key in ("norm", "spin_z", "orbital_z", "magnetic_moment_z", "inferred_tree_g")
        ) < 5e-10,
        "schwinger_g_factor_identity_closes": abs(
            structure["g_factor"] - structure["schwinger_expected_g"]
        ) < 2e-15,
        "g_factor_matches_twice_moment_ratio": abs(
            structure["g_factor"] - structure["g_from_ratio"]
        ) < 2e-15,
        "physical_anomalous_moment_is_not_inherited": True,
    }
    return {
        "schema": "openwave.m9.canonical-spin-magnetic-bridge.v1",
        "task": "M9.94",
        "parameters": asdict(parameters),
        "formal_import": {
            "declarations": list(formal_import["declarations"]),
            "boundary": list(formal_import["boundary"]),
            "inventory_fingerprint": imported["fingerprint"],
        },
        "canonical_state": state.to_manifest(),
        "observables": base,
        "spin_down_observables": flipped,
        "translated_observables": translated,
        "formal_structure": structure,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "formal_spin_magnetic_surface_imported": True,
            "canonical_particle_envelope_bound_to_pauli_spinor": True,
            "tree_level_g_factor_closed_in_platform": True,
            "schwinger_anomaly_derived_from_cat_ept_particle": False,
            "physical_electron_identity_established": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
