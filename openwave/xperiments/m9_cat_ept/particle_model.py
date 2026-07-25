"""Reusable, explicitly uncalibrated CAT/EPT particle-model kernel.

The model wraps the existing M9.63 coefficient selection, M9.69 stationary branch,
and M9.87 split-flow implementation behind one API. A constructed state is a
mathematical localized branch. It is not named as an electron or another observed
particle unless a separate calibration and identity certificate passes.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np
from numpy.typing import NDArray

from .coefficient_self_consistency import selected_coefficients
from .physlib_contract import contract_fingerprint, validate_contract
from .stationary_non_gaussian_branch import (
    StationaryBranchConfig,
    normalize_state,
    solve_stationary,
)

ComplexField = NDArray[np.complex128]


@dataclass(frozen=True)
class CatEptActionSpec:
    dispersion: float
    alpha: float
    beta: float
    normalization: float = 1.0
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if min(self.dispersion, self.alpha, self.beta, self.normalization) <= 0.0:
            raise ValueError("positive action coefficients and normalization required")
        if not self.assumptions:
            raise ValueError("the action assumptions must be explicit")

    @classmethod
    def repository_default(cls) -> "CatEptActionSpec":
        selected = selected_coefficients()
        return cls(
            dispersion=0.65,
            alpha=float(selected["alpha"]),
            beta=float(selected["beta"]),
            normalization=1.0,
            assumptions=(
                "the local density-action minimum matches the reference peak density",
                "the normalized Gaussian reference is stationary at the declared scale",
                "these conditions are structural model choices, not experimental predictions",
            ),
        )


@dataclass(frozen=True)
class CatEptParticleSpec:
    particle_id: str
    winding_sector: int
    action: CatEptActionSpec
    formal_contract_fingerprint: str
    physical_assignment: str | None = None
    calibration_id: str | None = None

    def __post_init__(self) -> None:
        if not self.particle_id:
            raise ValueError("particle_id is required")
        if len(self.formal_contract_fingerprint) != 64:
            raise ValueError("formal contract fingerprint must be SHA-256")
        if self.physical_assignment is not None and self.calibration_id is None:
            raise ValueError("a physical assignment requires a calibration record")


@dataclass(frozen=True)
class CatEptParticleState:
    field: ComplexField
    spacing: float
    simulation_time: float
    center: tuple[float, float, float]
    phase_origin: float
    declared_winding_sector: int
    winding_embedded: bool
    reference_branch_fingerprint: str
    construction: str

    def __post_init__(self) -> None:
        if self.field.ndim != 3 or min(self.field.shape) < 4:
            raise ValueError("a three-dimensional complex field is required")
        if not np.iscomplexobj(self.field):
            raise TypeError("particle field must be complex-valued")
        if self.spacing <= 0.0 or self.simulation_time < 0.0:
            raise ValueError("positive spacing and nonnegative time required")
        if len(self.center) != 3 or not all(math.isfinite(value) for value in self.center):
            raise ValueError("a finite three-dimensional center is required")
        if not math.isfinite(self.phase_origin):
            raise ValueError("a finite phase origin is required")
        if len(self.reference_branch_fingerprint) != 64:
            raise ValueError("reference branch fingerprint must be SHA-256")
        if not self.construction:
            raise ValueError("state construction classification is required")

    @property
    def state_fingerprint(self) -> str:
        return field_fingerprint(self.field, self.spacing)

    def to_manifest(self) -> dict[str, Any]:
        return {
            "schema": "openwave.m9.cat-ept-particle-state.v1",
            "shape": list(self.field.shape),
            "spacing": self.spacing,
            "simulation_time": self.simulation_time,
            "center": list(self.center),
            "phase_origin": self.phase_origin,
            "declared_winding_sector": self.declared_winding_sector,
            "winding_embedded": self.winding_embedded,
            "reference_branch_fingerprint": self.reference_branch_fingerprint,
            "state_fingerprint": self.state_fingerprint,
            "construction": self.construction,
        }


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def field_fingerprint(field: ComplexField, spacing: float) -> str:
    contiguous = np.ascontiguousarray(field, dtype=np.complex128)
    digest = sha256()
    digest.update(str(tuple(contiguous.shape)).encode())
    digest.update(np.float64(spacing).tobytes())
    digest.update(contiguous.view(np.float64).tobytes())
    return digest.hexdigest()


def action_fingerprint(action: CatEptActionSpec) -> str:
    return sha256(_canonical_json(asdict(action)).encode()).hexdigest()


def field_mass(field: ComplexField, spacing: float) -> float:
    return float(np.sum(np.abs(field) ** 2) * spacing**3)


def wrap_periodic_coordinate(value: float, length: float) -> float:
    """Return one coordinate in the canonical periodic interval ``[-L/2, L/2)``."""
    if length <= 0.0:
        raise ValueError("positive periodic length required")
    return float((value + 0.5 * length) % length - 0.5 * length)


def periodic_displacement(
    coordinates: NDArray[np.float64],
    center: float,
    length: float,
) -> NDArray[np.float64]:
    """Return minimum-image displacements from ``center`` on a periodic axis."""
    if length <= 0.0:
        raise ValueError("positive periodic length required")
    return np.asarray(
        (coordinates - center + 0.5 * length) % length - 0.5 * length,
        dtype=np.float64,
    )


def wave_number_squared(
    shape: tuple[int, int, int],
    spacing: float,
) -> NDArray[np.float64]:
    axes = [2.0 * math.pi * np.fft.fftfreq(points, d=spacing) for points in shape]
    kx, ky, kz = np.meshgrid(*axes, indexing="ij")
    return np.asarray(kx * kx + ky * ky + kz * kz, dtype=np.float64)


def free_subflow(
    field: ComplexField,
    time: float,
    spacing: float,
    dispersion: float,
) -> ComplexField:
    k2 = wave_number_squared(tuple(field.shape), spacing)
    evolved = np.fft.ifftn(
        np.fft.fftn(field) * np.exp(-1j * dispersion * k2 * time)
    )
    return np.asarray(evolved, dtype=np.complex128)


def local_subflow(
    field: ComplexField,
    time: float,
    alpha: float,
    beta: float,
) -> ComplexField:
    density = np.abs(field) ** 2
    phase = np.exp(1j * (alpha * density - beta * density**2) * time)
    return np.asarray(field * phase, dtype=np.complex128)


def strang_step(
    field: ComplexField,
    time: float,
    spacing: float,
    action: CatEptActionSpec,
) -> ComplexField:
    first = local_subflow(field, 0.5 * time, action.alpha, action.beta)
    second = free_subflow(first, time, spacing, action.dispersion)
    return local_subflow(second, 0.5 * time, action.alpha, action.beta)


def normalized_gaussian(
    points: int = 8,
    half_width: float = 3.0,
) -> tuple[ComplexField, float]:
    if points < 4 or half_width <= 0.0:
        raise ValueError("a finite grid and positive half width are required")
    spacing = 2.0 * half_width / points
    axis = (np.arange(points, dtype=np.float64) - points / 2.0) * spacing
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    field = np.exp(-(x * x + y * y + z * z) / 2.0).astype(np.complex128)
    return normalize_state(field, spacing), spacing


@dataclass(frozen=True)
class CatEptParticleModel:
    spec: CatEptParticleSpec

    @classmethod
    def repository_default(
        cls,
        *,
        winding_sector: int = 0,
        particle_id: str | None = None,
    ) -> "CatEptParticleModel":
        validation = validate_contract()
        if not validation["passed"]:
            raise ValueError("the pinned PhysLib contract is invalid or stale")
        identifier = particle_id or f"cat-ept-localized-branch-q{winding_sector:+d}"
        return cls(
            CatEptParticleSpec(
                particle_id=identifier,
                winding_sector=winding_sector,
                action=CatEptActionSpec.repository_default(),
                formal_contract_fingerprint=contract_fingerprint(),
            )
        )

    def _requires_repository_coefficients(self) -> None:
        selected = selected_coefficients()
        alpha = float(selected["alpha"])
        beta = float(selected["beta"])
        if not math.isclose(
            self.spec.action.alpha,
            alpha,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("the current stationary solver is pinned to the repository alpha")
        if not math.isclose(
            self.spec.action.beta,
            beta,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("the current stationary solver is pinned to the repository beta")

    def construct_stationary_state(
        self,
        *,
        points: int = 20,
        seed: str = "super_gaussian",
        config: StationaryBranchConfig | None = None,
    ) -> CatEptParticleState:
        self._requires_repository_coefficients()
        cfg = config or StationaryBranchConfig(
            dispersion=self.spec.action.dispersion,
            grids=(points,),
            reference_grid=points,
        )
        if cfg.dispersion != self.spec.action.dispersion:
            raise ValueError("stationary configuration and action dispersion must agree")
        field, grid = solve_stationary(points, seed, cfg)
        spacing = float(grid[5])
        reference = sha256(
            (
                field_fingerprint(field, spacing)
                + action_fingerprint(self.spec.action)
                + seed
            ).encode()
        ).hexdigest()
        return CatEptParticleState(
            field=np.asarray(field, dtype=np.complex128),
            spacing=spacing,
            simulation_time=0.0,
            center=(0.0, 0.0, 0.0),
            phase_origin=0.0,
            declared_winding_sector=self.spec.winding_sector,
            winding_embedded=self.spec.winding_sector == 0,
            reference_branch_fingerprint=reference,
            construction="stationary-non-gaussian-branch",
        )

    def apply_phase_chirp(
        self,
        state: CatEptParticleState,
        strength: float,
        *,
        axis: int = 0,
    ) -> CatEptParticleState:
        if axis not in (0, 1, 2):
            raise ValueError("axis must be 0, 1, or 2")
        coordinates = (
            np.arange(state.field.shape[axis], dtype=np.float64)
            - state.field.shape[axis] / 2.0
        ) * state.spacing
        shape = [1, 1, 1]
        shape[axis] = state.field.shape[axis]
        phase = np.exp(1j * strength * coordinates.reshape(shape))
        return replace(
            state,
            field=np.asarray(state.field * phase, dtype=np.complex128),
            construction=f"{state.construction}+phase-chirp",
        )

    def translate_cells(
        self,
        state: CatEptParticleState,
        offsets: tuple[int, int, int],
    ) -> CatEptParticleState:
        if len(offsets) != 3 or any(
            not isinstance(offset, (int, np.integer)) for offset in offsets
        ):
            raise ValueError("three integer cell offsets are required")
        translated = np.roll(state.field, shift=offsets, axis=(0, 1, 2))
        lengths = tuple(points * state.spacing for points in state.field.shape)
        center = tuple(
            wrap_periodic_coordinate(value + int(offset) * state.spacing, length)
            for value, offset, length in zip(state.center, offsets, lengths)
        )
        return replace(
            state,
            field=np.asarray(translated, dtype=np.complex128),
            center=center,
            construction=f"{state.construction}+periodic-translation",
        )

    def evolve(
        self,
        state: CatEptParticleState,
        *,
        duration: float,
        time_step: float = 0.002,
    ) -> CatEptParticleState:
        if duration < 0.0 or time_step <= 0.0:
            raise ValueError("nonnegative duration and positive time step required")
        evolved = np.array(state.field, dtype=np.complex128, copy=True)
        remaining = duration
        while remaining > 1e-15:
            step = min(time_step, remaining)
            evolved = strang_step(evolved, step, state.spacing, self.spec.action)
            remaining -= step
        return replace(
            state,
            field=evolved,
            simulation_time=state.simulation_time + duration,
            construction=f"{state.construction}+split-flow",
        )

    def measure(self, state: CatEptParticleState) -> dict[str, Any]:
        shape = state.field.shape
        axes = [
            (np.arange(points, dtype=np.float64) - points / 2.0) * state.spacing
            for points in shape
        ]
        global_x, global_y, global_z = np.meshgrid(*axes, indexing="ij")
        lengths = tuple(points * state.spacing for points in shape)
        relative_x = periodic_displacement(global_x, state.center[0], lengths[0])
        relative_y = periodic_displacement(global_y, state.center[1], lengths[1])
        relative_z = periodic_displacement(global_z, state.center[2], lengths[2])
        radius_sq = relative_x**2 + relative_y**2 + relative_z**2
        density = np.abs(state.field) ** 2
        total_mass = field_mass(state.field, state.spacing)
        rms_radius = math.sqrt(
            float(
                np.sum(radius_sq * density)
                * state.spacing**3
                / max(total_mass, 1e-30)
            )
        )
        half_widths = [0.5 * length for length in lengths]
        boundary = np.maximum.reduce(
            (
                np.abs(relative_x) / half_widths[0],
                np.abs(relative_y) / half_widths[1],
                np.abs(relative_z) / half_widths[2],
            )
        ) > 0.75
        boundary_fraction = float(
            np.sum(density[boundary]) * state.spacing**3 / max(total_mass, 1e-30)
        )
        return {
            "mass": total_mass,
            "normalization_error": abs(total_mass - self.spec.action.normalization),
            "rms_radius": rms_radius,
            "boundary_fraction": boundary_fraction,
            "peak_density": float(np.max(density)),
            "state_fingerprint": state.state_fingerprint,
            "reference_branch_fingerprint": state.reference_branch_fingerprint,
            "declared_winding_sector": state.declared_winding_sector,
            "winding_embedded": state.winding_embedded,
            "physical_assignment": self.spec.physical_assignment,
            "calibration_id": self.spec.calibration_id,
        }

    def evaluate_identity(
        self,
        state: CatEptParticleState,
        evidence: Mapping[str, bool] | None = None,
    ) -> dict[str, Any]:
        observables = self.measure(state)
        supplied = dict(evidence or {})
        required_external = (
            "stable_localized_state",
            "charge_unit_calibrated",
            "rest_energy_calibrated",
            "clock_identified",
            "spin_and_exchange_closed",
            "magnetic_moment_closed",
            "far_field_force_closed",
            "out_of_sample_prediction",
        )
        gates = {
            "formal_contract_current": validate_contract()["passed"],
            "state_is_normalized": observables["normalization_error"] <= 2e-10,
            "state_is_localized": observables["boundary_fraction"] <= 2e-2,
            "state_sector_matches_model": (
                state.declared_winding_sector == self.spec.winding_sector
            ),
            "winding_sector_is_embedded": state.winding_embedded,
            "physical_name_is_requested": self.spec.physical_assignment is not None,
            "calibration_record_is_present": self.spec.calibration_id is not None,
            **{key: bool(supplied.get(key, False)) for key in required_external},
        }
        passed = all(gates.values())
        return {
            "schema": "openwave.m9.cat-ept-identity-certificate.v1",
            "particle_id": self.spec.particle_id,
            "requested_assignment": self.spec.physical_assignment,
            "gates": gates,
            "passed": passed,
            "decision": {
                "physical_identity_established": passed,
                "mathematical_branch_available": True,
                "default_identity_is_blocked": self.spec.physical_assignment is None,
            },
        }

    def promote_identity(
        self,
        state: CatEptParticleState,
        *,
        physical_assignment: str,
        calibration_id: str,
        evidence: Mapping[str, bool],
    ) -> "CatEptParticleModel":
        candidate = CatEptParticleModel(
            replace(
                self.spec,
                physical_assignment=physical_assignment,
                calibration_id=calibration_id,
            )
        )
        certificate = candidate.evaluate_identity(state, evidence)
        if not certificate["passed"]:
            failed = [
                name
                for name, passed_gate in certificate["gates"].items()
                if not passed_gate
            ]
            raise ValueError(f"physical identity gate failed: {', '.join(failed)}")
        return candidate


@lru_cache(maxsize=1)
def run_particle_kernel_study() -> dict[str, Any]:
    model = CatEptParticleModel.repository_default()
    field, spacing = normalized_gaussian()
    state = CatEptParticleState(
        field=field,
        spacing=spacing,
        simulation_time=0.0,
        center=(0.0, 0.0, 0.0),
        phase_origin=0.0,
        declared_winding_sector=0,
        winding_embedded=True,
        reference_branch_fingerprint=field_fingerprint(field, spacing),
        construction="synthetic-kernel-control",
    )
    time = 0.013
    free_reverse = free_subflow(
        free_subflow(field, time, spacing, model.spec.action.dispersion),
        -time,
        spacing,
        model.spec.action.dispersion,
    )
    local_reverse = local_subflow(
        local_subflow(field, time, model.spec.action.alpha, model.spec.action.beta),
        -time,
        model.spec.action.alpha,
        model.spec.action.beta,
    )
    translated = model.translate_cells(state, (3, -2, 1))
    base_observables = model.measure(state)
    translated_observables = model.measure(translated)
    evolved = model.evolve(state, duration=0.01, time_step=0.002)
    identity = model.evaluate_identity(evolved)
    free_error = float(np.linalg.norm(free_reverse - field) / np.linalg.norm(field))
    local_error = float(np.linalg.norm(local_reverse - field) / np.linalg.norm(field))
    mass_error = abs(field_mass(evolved.field, spacing) - field_mass(field, spacing))
    translation_radius_error = abs(
        translated_observables["rms_radius"] - base_observables["rms_radius"]
    )
    translation_boundary_error = abs(
        translated_observables["boundary_fraction"]
        - base_observables["boundary_fraction"]
    )
    acceptance = {
        "formal_contract_passes": validate_contract()["passed"],
        "repository_action_assumptions_are_explicit": bool(model.spec.action.assumptions),
        "free_subflow_is_reversible": free_error < 2e-14,
        "local_subflow_is_reversible": local_error < 2e-14,
        "split_flow_preserves_mass": mass_error < 2e-12,
        "periodic_translation_preserves_radius": translation_radius_error < 2e-14,
        "periodic_translation_preserves_boundary_fraction": (
            translation_boundary_error < 2e-14
        ),
        "state_manifest_is_replay_identifiable": len(evolved.state_fingerprint) == 64,
        "physical_identity_is_blocked_by_default": not identity["passed"]
        and identity["decision"]["default_identity_is_blocked"],
    }
    return {
        "schema": "openwave.m9.cat-ept-particle-kernel-result.v2",
        "task": "M9.93b",
        "model": asdict(model.spec),
        "control_state": evolved.to_manifest(),
        "errors": {
            "free_reverse": free_error,
            "local_reverse": local_error,
            "mass": mass_error,
            "translation_radius": translation_radius_error,
            "translation_boundary_fraction": translation_boundary_error,
        },
        "identity_certificate": identity,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "reusable_particle_kernel_available": True,
            "periodic_observables_are_translation_covariant": True,
            "localized_branch_is_a_physical_particle": False,
            "charged_stationary_branch_constructed": False,
            "physical_calibration_complete": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
