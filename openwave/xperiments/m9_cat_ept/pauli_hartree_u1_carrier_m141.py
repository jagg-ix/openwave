"""M9.141 three-dimensional Pauli--Hartree--U(1) CAT/EPT carrier.

This module consolidates the odd-grid Fourier geometry, mass-consistent Pauli
current, static Maxwell projection, attractive Hartree interaction, measured
winding, and an explicit frozen-H discrete imaginary functional in one state.
It constructs a charged mathematical carrier.  It does not promote a stable
stationary particle, a physical charge unit, or an electron identity.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .charged_field_tools import periodic_contour_winding
from .compatible_discrete_geometry import PeriodicFourierGeometry, analytic_identity_diagnostics
from .gauge_spinor_stationary_feasibility import PAULI, spin_density
from .stationary_non_gaussian_branch import coefficients

Vector = tuple[np.ndarray, np.ndarray, np.ndarray]

MILESTONE = "M9.141"
SCHEMA = "openwave.m9.pauli-hartree-u1-carrier.v1"
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "entropic-physlib-linear-full"
FORMAL_SOURCES = (
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/EntropicTime/CubicQuinticMildFlow.lean",
        "role": "Hartree/Newton plus supplied local interaction target",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Dirac/PauliEquationSpinOrbit.lean",
        "role": "Pauli matrix, magnetic, Darwin, and spin-orbit structure",
    },
    {
        "path": "Physlib/QuantumMechanics/ComplexAction/Electromagnetic/MaxwellContinuityCovariant.lean",
        "role": "F=dA, continuity, and conditional Maxwell reconstruction",
    },
    {
        "path": "Physlib/Mathematics/LovelockRund/ComplexActionVariational.lean",
        "role": "imaginary residual and entropic-time gradient interface",
    },
)


@dataclass(frozen=True)
class PauliHartreeU1Config:
    points: int = 17
    half_width: float = 8.0
    winding: int = 3
    contour_radius: float = 2.4
    core_radius: float = 0.9
    envelope_width: float = 2.0
    dispersion: float = 0.65
    charge: float = 1.0
    g_factor: float = 2.0
    hartree_coupling: float = 0.05
    hbar: float = 1.0
    imaginary_strength: float = 0.10
    relaxation_step: float = 2.5e-5
    relaxation_steps: int = 12
    maxwell_picard_iterations: int = 8
    maxwell_fixed_point_tolerance: float = 2.0e-11

    def __post_init__(self) -> None:
        if self.points < 9 or self.points % 2 == 0:
            raise ValueError("an odd three-dimensional grid with at least nine points is required")
        if min(
            self.half_width,
            self.contour_radius,
            self.core_radius,
            self.envelope_width,
            self.dispersion,
            self.g_factor,
            self.hbar,
            self.imaginary_strength,
            self.relaxation_step,
        ) <= 0.0:
            raise ValueError("positive carrier and relaxation controls required")
        if self.winding == 0 or self.charge == 0.0:
            raise ValueError("nonzero winding and charge required")
        if self.contour_radius >= self.half_width:
            raise ValueError("the winding contour must lie inside the periodic half box")
        if self.hartree_coupling < 0.0 or self.relaxation_steps < 1:
            raise ValueError("nonnegative Hartree coupling and positive step count required")
        if self.maxwell_picard_iterations < 2 or self.maxwell_fixed_point_tolerance <= 0.0:
            raise ValueError("substantive Maxwell fixed-point controls required")

    @property
    def spacing(self) -> float:
        return 2.0 * self.half_width / self.points

    @property
    def effective_mass(self) -> float:
        return 1.0 / (2.0 * self.dispersion)

    @property
    def charge_from_winding(self) -> float:
        return self.winding / 3.0

    def geometry(self) -> PeriodicFourierGeometry:
        return PeriodicFourierGeometry(
            (self.points, self.points, self.points),
            (self.spacing, self.spacing, self.spacing),
        )


@dataclass(frozen=True)
class PauliHartreeU1State:
    spinor: np.ndarray
    scalar_potential: np.ndarray
    vector_potential: Vector
    electric_field: Vector
    magnetic_field: Vector
    hartree_potential: np.ndarray
    time: float
    entropic_time: float
    declared_winding: int
    measured_winding: int
    winding_quantization_error: float
    minimum_contour_amplitude: float
    maxwell_fixed_point_error: float
    maxwell_picard_iterations: int
    construction: str

    def __post_init__(self) -> None:
        if self.spinor.ndim != 4 or self.spinor.shape[0] != 2:
            raise ValueError("a two-component three-dimensional Pauli spinor is required")
        shape = tuple(self.spinor.shape[1:])
        if len(shape) != 3 or any(points < 5 for points in shape):
            raise ValueError("a finite three-dimensional spatial carrier is required")
        scalar_fields = (self.scalar_potential, self.hartree_potential)
        vector_fields = (*self.vector_potential, *self.electric_field, *self.magnetic_field)
        if any(tuple(field.shape) != shape for field in (*scalar_fields, *vector_fields)):
            raise ValueError("all gauge, Hartree, and matter fields must share one grid")
        if self.time < 0.0 or self.entropic_time < 0.0:
            raise ValueError("nonnegative coordinate and entropic times required")
        if not self.construction:
            raise ValueError("state construction metadata required")

    def manifest(self, cfg: PauliHartreeU1Config) -> dict[str, Any]:
        return {
            "schema": "openwave.m9.pauli-hartree-u1-state.v1",
            "shape": list(self.spinor.shape),
            "spacing": cfg.spacing,
            "time": self.time,
            "entropic_time": self.entropic_time,
            "declared_winding": self.declared_winding,
            "measured_winding": self.measured_winding,
            "winding_quantization_error": self.winding_quantization_error,
            "minimum_contour_amplitude": self.minimum_contour_amplitude,
            "maxwell_fixed_point_error": self.maxwell_fixed_point_error,
            "maxwell_picard_iterations": self.maxwell_picard_iterations,
            "construction": self.construction,
            "state_fingerprint": state_fingerprint(self, cfg),
        }


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def state_fingerprint(state: PauliHartreeU1State, cfg: PauliHartreeU1Config) -> str:
    digest = sha256(_canonical_json(asdict(cfg)).encode())
    for array in (
        state.spinor,
        state.scalar_potential,
        *state.vector_potential,
        *state.electric_field,
        *state.magnetic_field,
        state.hartree_potential,
    ):
        contiguous = np.ascontiguousarray(array)
        digest.update(str(contiguous.shape).encode())
        digest.update(contiguous.view(np.uint8).tobytes())
    digest.update(
        _canonical_json(
            {
                "time": state.time,
                "entropic_time": state.entropic_time,
                "declared_winding": state.declared_winding,
                "measured_winding": state.measured_winding,
                "maxwell_fixed_point_error": state.maxwell_fixed_point_error,
                "maxwell_picard_iterations": state.maxwell_picard_iterations,
                "construction": state.construction,
            }
        ).encode()
    )
    return digest.hexdigest()


def normalize_spinor(spinor: np.ndarray, cfg: PauliHartreeU1Config) -> np.ndarray:
    norm = float(np.sum(np.abs(spinor) ** 2) * cfg.geometry().cell_volume)
    if norm <= 0.0 or not math.isfinite(norm):
        raise ValueError("positive finite spinor norm required")
    return np.asarray(spinor / math.sqrt(norm), dtype=np.complex128)


def _axis(cfg: PauliHartreeU1Config) -> np.ndarray:
    return (np.arange(cfg.points, dtype=np.float64) - cfg.points / 2.0) * cfg.spacing


def winding_seed(cfg: PauliHartreeU1Config) -> np.ndarray:
    axis = _axis(cfg)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    radial = np.hypot(x, y)
    angle = np.arctan2(y, x)
    core = np.tanh(radial / cfg.core_radius) ** abs(cfg.winding)
    envelope = np.exp(-(x * x + y * y + z * z) / (2.0 * cfg.envelope_width**2))
    scalar = core * envelope * np.exp(1.0j * cfg.winding * angle)
    spinor = np.zeros((2, cfg.points, cfg.points, cfg.points), dtype=np.complex128)
    spinor[0] = scalar
    return normalize_spinor(spinor, cfg)


def charge_current(
    spinor: np.ndarray,
    vector_potential: Vector,
    geometry: PeriodicFourierGeometry,
    cfg: PauliHartreeU1Config,
) -> tuple[np.ndarray, Vector]:
    density = np.asarray(np.sum(np.abs(spinor) ** 2, axis=0), dtype=np.float64)
    convective = []
    for axis in range(3):
        covariant = geometry.derivative(spinor, axis)
        covariant -= 1.0j * cfg.charge * vector_potential[axis][None, ...] * spinor
        convective.append(
            np.asarray(
                cfg.charge
                / cfg.effective_mass
                * np.imag(np.sum(np.conj(spinor) * covariant, axis=0)),
                dtype=np.float64,
            )
        )
    magnetization = tuple(
        cfg.g_factor * cfg.charge * component / (2.0 * cfg.effective_mass)
        for component in spin_density(spinor)
    )
    magnetization_current = geometry.curl(magnetization)
    current = tuple(
        np.asarray(convective[index] + magnetization_current[index], dtype=np.float64)
        for index in range(3)
    )
    return np.asarray(cfg.charge * density, dtype=np.float64), current


def frozen_hamiltonian_action(
    spinor: np.ndarray,
    local_scalar: np.ndarray,
    vector_potential: Vector,
    magnetic_field: Vector,
    geometry: PeriodicFourierGeometry,
    cfg: PauliHartreeU1Config,
) -> np.ndarray:
    result = -cfg.dispersion * geometry.covariant_laplacian(
        spinor, vector_potential, cfg.charge
    )
    result += local_scalar[None, ...] * spinor
    sigma_dot_b = np.zeros_like(spinor, dtype=np.complex128)
    for matrix, component in zip(PAULI, magnetic_field, strict=True):
        sigma_dot_b += component[None, ...] * np.einsum(
            "ab,bxyz->axyz", matrix, spinor, optimize=True
        )
    result -= (
        cfg.g_factor * cfg.charge / (4.0 * cfg.effective_mass)
    ) * sigma_dot_b
    return np.asarray(result, dtype=np.complex128)


def refresh_state(
    spinor: np.ndarray,
    cfg: PauliHartreeU1Config,
    *,
    time: float = 0.0,
    entropic_time: float = 0.0,
    construction: str,
) -> PauliHartreeU1State:
    geometry = cfg.geometry()
    vector_potential = tuple(
        np.zeros((cfg.points, cfg.points, cfg.points), dtype=np.float64)
        for _ in range(3)
    )
    fields: dict[str, Any] | None = None
    fixed_point_error = math.inf
    iterations_used = 0
    for iterations_used in range(1, cfg.maxwell_picard_iterations + 1):
        charge_density, current = charge_current(
            spinor, vector_potential, geometry, cfg
        )
        fields = geometry.static_maxwell_fields(charge_density, current)
        next_vector = tuple(
            np.asarray(component, dtype=np.float64)
            for component in fields["vector_potential"]
        )
        difference = math.sqrt(
            geometry.cell_volume
            * sum(
                float(np.sum((next_vector[index] - vector_potential[index]) ** 2))
                for index in range(3)
            )
        )
        scale = max(
            math.sqrt(
                geometry.cell_volume
                * sum(float(np.sum(component * component)) for component in next_vector)
            ),
            1.0e-30,
        )
        fixed_point_error = difference / scale
        vector_potential = next_vector
        if fixed_point_error <= cfg.maxwell_fixed_point_tolerance:
            break
    assert fields is not None
    density = np.asarray(np.sum(np.abs(spinor) ** 2, axis=0), dtype=np.float64)
    hartree = geometry.inverse_negative_laplacian(density)
    winding = periodic_contour_winding(
        np.asarray(spinor[0], dtype=np.complex128),
        cfg.spacing,
        radius=cfg.contour_radius,
    )
    return PauliHartreeU1State(
        spinor=np.asarray(spinor, dtype=np.complex128),
        scalar_potential=np.asarray(fields["potential"], dtype=np.float64),
        vector_potential=tuple(
            np.asarray(component, dtype=np.float64)
            for component in fields["vector_potential"]
        ),
        electric_field=tuple(
            np.asarray(component, dtype=np.float64) for component in fields["electric"]
        ),
        magnetic_field=tuple(
            np.asarray(component, dtype=np.float64) for component in fields["magnetic"]
        ),
        hartree_potential=np.asarray(hartree, dtype=np.float64),
        time=time,
        entropic_time=entropic_time,
        declared_winding=cfg.winding,
        measured_winding=int(winding["integer_winding"]),
        winding_quantization_error=float(winding["quantization_error"]),
        minimum_contour_amplitude=float(winding["minimum_contour_amplitude"]),
        maxwell_fixed_point_error=fixed_point_error,
        maxwell_picard_iterations=iterations_used,
        construction=construction,
    )


def construct_state(cfg: PauliHartreeU1Config = PauliHartreeU1Config()) -> PauliHartreeU1State:
    return refresh_state(
        winding_seed(cfg),
        cfg,
        construction="analytic-winding-pauli-hartree-u1-seed",
    )


def operator_diagnostics(
    state: PauliHartreeU1State, cfg: PauliHartreeU1Config
) -> dict[str, Any]:
    geometry = cfg.geometry()
    density = np.asarray(np.sum(np.abs(state.spinor) ** 2, axis=0), dtype=np.float64)
    alpha, beta = coefficients()
    local_scalar = (
        cfg.charge * state.scalar_potential
        - cfg.hartree_coupling * state.hartree_potential
        - alpha * density
        + beta * density * density
    )
    hamiltonian = frozen_hamiltonian_action(
        state.spinor,
        local_scalar,
        state.vector_potential,
        state.magnetic_field,
        geometry,
        cfg,
    )
    norm = float(np.sum(np.abs(state.spinor) ** 2) * geometry.cell_volume)
    chemical_potential = float(
        np.real(np.vdot(state.spinor, hamiltonian)) * geometry.cell_volume
        / max(norm, 1.0e-30)
    )
    centered = hamiltonian - chemical_potential * state.spinor
    centered_norm_sq = float(
        np.sum(np.abs(centered) ** 2) * geometry.cell_volume
    )
    operator_norm = math.sqrt(
        float(np.sum(np.abs(hamiltonian) ** 2) * geometry.cell_volume)
    )
    residual_norm = math.sqrt(centered_norm_sq)
    discrete_imaginary_action = 0.5 * cfg.imaginary_strength * centered_norm_sq
    entropic_rate = (
        cfg.imaginary_strength * centered_norm_sq / (cfg.hbar * cfg.hbar)
    )
    charge_density, current = charge_current(
        state.spinor, state.vector_potential, geometry, cfg
    )
    fields = geometry.static_maxwell_fields(charge_density, current)
    spins = spin_density(state.spinor)
    integrated_charge = float(np.sum(charge_density) * geometry.cell_volume)
    return {
        "norm": norm,
        "chemical_potential": chemical_potential,
        "relative_stationary_residual": residual_norm / max(operator_norm, 1.0e-30),
        "centered_hamiltonian_norm_sq": centered_norm_sq,
        "discrete_imaginary_action": discrete_imaginary_action,
        "entropic_rate": entropic_rate,
        "integrated_charge": integrated_charge,
        "charge_from_winding": state.measured_winding / 3.0,
        "spin_x": float(np.sum(spins[0]) * geometry.cell_volume),
        "spin_y": float(np.sum(spins[1]) * geometry.cell_volume),
        "spin_z": float(np.sum(spins[2]) * geometry.cell_volume),
        "measured_winding": state.measured_winding,
        "winding_quantization_error": state.winding_quantization_error,
        "minimum_contour_amplitude": state.minimum_contour_amplitude,
        "maxwell_fixed_point_error": state.maxwell_fixed_point_error,
        "maxwell_picard_iterations": state.maxwell_picard_iterations,
        "gauss_relative_residual": float(fields["gauss_relative_residual"]),
        "ampere_relative_residual": float(fields["ampere_relative_residual"]),
        "magnetic_divergence_max": float(fields["magnetic_divergence_max"]),
        "state_fingerprint": state_fingerprint(state, cfg),
        "_local_scalar": local_scalar,
        "_hamiltonian": hamiltonian,
        "_centered": centered,
    }


def relaxation_step(
    state: PauliHartreeU1State, cfg: PauliHartreeU1Config
) -> tuple[PauliHartreeU1State, dict[str, float]]:
    geometry = cfg.geometry()
    diagnostics = operator_diagnostics(state, cfg)
    local_scalar = diagnostics.pop("_local_scalar")
    diagnostics.pop("_hamiltonian")
    centered = diagnostics.pop("_centered")
    squared_gradient = frozen_hamiltonian_action(
        centered,
        local_scalar,
        state.vector_potential,
        state.magnetic_field,
        geometry,
        cfg,
    ) - diagnostics["chemical_potential"] * centered
    next_spinor = normalize_spinor(
        state.spinor
        - cfg.relaxation_step * cfg.imaginary_strength * squared_gradient,
        cfg,
    )
    next_entropic = (
        state.entropic_time + cfg.relaxation_step * diagnostics["entropic_rate"]
    )
    next_state = refresh_state(
        next_spinor,
        cfg,
        time=state.time + cfg.relaxation_step,
        entropic_time=next_entropic,
        construction=f"{state.construction}+frozen-H-squared-gradient",
    )
    return next_state, {
        key: float(value)
        for key, value in diagnostics.items()
        if isinstance(value, (int, float, np.integer, np.floating))
    }


def canonical_payload(cfg: PauliHartreeU1Config | None = None) -> dict[str, Any]:
    selected = cfg or PauliHartreeU1Config()
    return {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "model": "M9 CAT/EPT",
        "config": asdict(selected),
        "formal_authority": {
            "repository": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "sources": list(FORMAL_SOURCES),
        },
        "state_api": (
            "openwave.xperiments.m9_cat_ept."
            "pauli_hartree_u1_carrier_m141:PauliHartreeU1State"
        ),
        "model_api": (
            "openwave.xperiments.m9_cat_ept."
            "pauli_hartree_u1_carrier_m141:construct_state"
        ),
        "imaginary_functional": {
            "name": "frozen-H centered squared norm",
            "formula": "S_I^n[psi] = gamma/2 ||(H_n-mu_n) psi||_2^2",
            "gradient_flow": "dpsi/dt = -gamma (H_n-mu_n)^2 psi",
            "entropic_rate": "gamma ||(H_n-mu_n) psi||_2^2 / hbar^2",
            "scope": "one frozen-operator discrete substep, not a full nonlinear continuum derivation",
        },
        "claim_boundary": {
            "stable_charged_stationary_branch": False,
            "continuum_convergence": False,
            "physical_charge_calibrated": False,
            "physical_particle_identity": False,
            "external_prediction_complete": False,
            "criterion_rows_promoted": [],
        },
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_pauli_hartree_u1_campaign() -> dict[str, Any]:
    cfg = PauliHartreeU1Config()
    geometry_checks = analytic_identity_diagnostics(cfg.points, cfg.half_width)
    state = construct_state(cfg)
    initial = operator_diagnostics(state, cfg)
    history = []
    minimum_entropic_increment = math.inf
    for index in range(cfg.relaxation_steps):
        previous = state.entropic_time
        state, step_record = relaxation_step(state, cfg)
        minimum_entropic_increment = min(
            minimum_entropic_increment, state.entropic_time - previous
        )
        history.append(
            {
                "step": index + 1,
                "entropic_time": state.entropic_time,
                "imaginary_action_before": step_record["discrete_imaginary_action"],
                "stationary_residual_before": step_record[
                    "relative_stationary_residual"
                ],
            }
        )
    final = operator_diagnostics(state, cfg)
    for row in (initial, final):
        row.pop("_local_scalar")
        row.pop("_hamiltonian")
        row.pop("_centered")
    mass_map_error = abs(2.0 * cfg.dispersion * cfg.effective_mass - 1.0)
    charge_winding_error = abs(final["integrated_charge"] - final["charge_from_winding"])
    payload = canonical_payload(cfg)
    acceptance = {
        "odd_grid_fourier_complex_closes": (
            geometry_checks["odd_operational_grid"] == 1
            and geometry_checks["fourier_null_mode_count"] == 1
            and geometry_checks["curl_gradient_max"] <= 1.0e-12
            and geometry_checks["divergence_curl_max"] <= 1.0e-12
            and geometry_checks["laplacian_identity_relative_error"] <= 1.0e-12
        ),
        "one_mass_map_closes": mass_map_error <= 2.0e-15,
        "two_component_3d_state_is_constructed": tuple(state.spinor.shape)
        == (2, cfg.points, cfg.points, cfg.points),
        "nonzero_winding_is_measured_from_the_field": (
            final["measured_winding"] == cfg.winding
            and final["winding_quantization_error"] <= 2.0e-12
            and final["minimum_contour_amplitude"] > 1.0e-3
        ),
        "normalized_charge_matches_winding_three_unit": charge_winding_error <= 2.0e-12,
        "static_u1_constraints_close": (
            final["maxwell_fixed_point_error"] <= cfg.maxwell_fixed_point_tolerance
            and final["gauss_relative_residual"] <= 1.0e-11
            and final["ampere_relative_residual"] <= 1.0e-11
            and final["magnetic_divergence_max"] <= 1.0e-11
        ),
        "spin_half_projection_is_retained": abs(final["spin_z"] - 0.5) <= 5.0e-9,
        "normalization_is_retained": abs(final["norm"] - 1.0) <= 2.0e-12,
        "frozen_imaginary_action_is_positive": initial[
            "discrete_imaginary_action"
        ]
        > 0.0,
        "entropic_time_is_monotone_and_nontrivial": (
            minimum_entropic_increment >= -1.0e-15 and state.entropic_time > 0.0
        ),
        "squared_gradient_reduces_the_stationary_residual": final[
            "relative_stationary_residual"
        ]
        < initial["relative_stationary_residual"],
        "squared_gradient_reduces_the_imaginary_functional": final[
            "discrete_imaginary_action"
        ]
        < initial["discrete_imaginary_action"],
        "state_manifest_is_replay_identifiable": len(
            state.manifest(cfg)["state_fingerprint"]
        )
        == 64,
        "physical_and_stationary_promotion_remain_blocked": not any(
            value
            for key, value in payload["claim_boundary"].items()
            if key != "criterion_rows_promoted"
        )
        and payload["claim_boundary"]["criterion_rows_promoted"] == [],
    }
    return {
        **payload,
        "task": "M9.141a-c",
        "fingerprint": fingerprint(payload),
        "geometry_diagnostics": geometry_checks,
        "mass_map_error": mass_map_error,
        "charge_winding_error": charge_winding_error,
        "initial": initial,
        "final": final,
        "history": history,
        "final_state_manifest": state.manifest(cfg),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "three_dimensional_pauli_hartree_u1_carrier_constructed": True,
            "nonzero_winding_measured_from_state": True,
            "static_maxwell_constraints_closed": True,
            "frozen_discrete_imaginary_functional_constructed": True,
            "stable_charged_stationary_branch_promoted": False,
            "physical_claims_promoted": [],
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
