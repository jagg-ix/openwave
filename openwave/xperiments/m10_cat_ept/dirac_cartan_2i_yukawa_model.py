"""M10 CAT/EPT Dirac--Cartan--binary-icosahedral particle carrier.

This module constructs one four-spinor state carrying the complete 120-element
binary icosahedral action, a Yukawa-generated complex mass, its Compton clock,
algebraically eliminated axial Cartan torsion, measured winding, and
self-consistent periodic U(1) fields.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import itertools
import json
import math
from typing import Any, Mapping

import numpy as np

from openwave.xperiments.m9_cat_ept.charged_field_tools import periodic_contour_winding
from openwave.xperiments.m9_cat_ept.compatible_discrete_geometry import PeriodicFourierGeometry

MILESTONE = "M10.1"
SCHEMA = "openwave.m10.dirac-cartan-2i-yukawa.v1"
FORMAL_REPOSITORY = "jagg-ix/entropic-physlib-private"
FORMAL_BRANCH = "agent/dirac-cartan-2i-compton-yukawa"

Quaternion = tuple[float, float, float, float]
Vector = tuple[np.ndarray, np.ndarray, np.ndarray]

_SIGMA_X = np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
_SIGMA_Y = np.asarray([[0.0, -1.0j], [1.0j, 0.0]], dtype=np.complex128)
_SIGMA_Z = np.asarray([[1.0, 0.0], [0.0, -1.0]], dtype=np.complex128)
_ZERO_2 = np.zeros((2, 2), dtype=np.complex128)
_ID_2 = np.eye(2, dtype=np.complex128)

ALPHAS = tuple(
    np.block([[_ZERO_2, sigma], [sigma, _ZERO_2]])
    for sigma in (_SIGMA_X, _SIGMA_Y, _SIGMA_Z)
)
BETA = np.block([[_ID_2, _ZERO_2], [_ZERO_2, -_ID_2]])
GAMMAS = (BETA, *(BETA @ alpha for alpha in ALPHAS))
GAMMA5 = 1.0j * GAMMAS[0] @ GAMMAS[1] @ GAMMAS[2] @ GAMMAS[3]
AXIAL_MATRICES = (GAMMA5, *(alpha @ GAMMA5 for alpha in ALPHAS))


def _permutation_parity(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return inversions % 2


def _quaternion_key(value: Quaternion) -> Quaternion:
    return tuple(round(float(component), 12) for component in value)  # type: ignore[return-value]


@lru_cache(maxsize=1)
def binary_icosahedral_quaternions() -> tuple[Quaternion, ...]:
    """Return the exact coordinate pattern of the 120 binary-icosahedral units."""
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    phi_inverse = 1.0 / phi
    values: set[Quaternion] = set()

    def add(value: list[float] | tuple[float, ...]) -> None:
        values.add(_quaternion_key(tuple(value)))

    for axis in range(4):
        for sign in (-1.0, 1.0):
            value = [0.0, 0.0, 0.0, 0.0]
            value[axis] = sign
            add(value)

    for signs in itertools.product((-1.0, 1.0), repeat=4):
        add(tuple(0.5 * sign for sign in signs))

    even_permutations = tuple(
        permutation
        for permutation in itertools.permutations(range(4))
        if _permutation_parity(permutation) == 0
    )
    for permutation in even_permutations:
        for signs in itertools.product((-1.0, 1.0), repeat=3):
            base = (
                0.0,
                signs[0] * 0.5,
                signs[1] * phi / 2.0,
                signs[2] * phi_inverse / 2.0,
            )
            add(tuple(base[permutation[index]] for index in range(4)))

    result = tuple(sorted(values))
    if len(result) != 120:
        raise RuntimeError(f"expected 120 binary-icosahedral elements, got {len(result)}")
    return result


def quaternion_multiply(left: Quaternion, right: Quaternion) -> Quaternion:
    a, b, c, d = left
    e, f, g, h = right
    return (
        a * e - b * f - c * g - d * h,
        a * f + b * e + c * h - d * g,
        a * g - b * h + c * e + d * f,
        a * h + b * g - c * f + d * e,
    )


def quaternion_to_su2(value: Quaternion) -> np.ndarray:
    a, b, c, d = value
    return np.asarray(
        [[a + 1.0j * b, c + 1.0j * d], [-c + 1.0j * d, a - 1.0j * b]],
        dtype=np.complex128,
    )


def dirac_2i_matrix(value: Quaternion) -> np.ndarray:
    unitary = quaternion_to_su2(value)
    return np.block([[unitary, _ZERO_2], [_ZERO_2, unitary]])


def apply_binary_icosahedral(spinor: np.ndarray, value: Quaternion) -> np.ndarray:
    if spinor.ndim != 4 or spinor.shape[0] != 4:
        raise ValueError("a component-by-space four-spinor is required")
    return np.asarray(
        np.einsum("ab,bxyz->axyz", dirac_2i_matrix(value), spinor, optimize=True),
        dtype=np.complex128,
    )


@lru_cache(maxsize=1)
def binary_icosahedral_diagnostics() -> dict[str, float | int | bool]:
    values = binary_icosahedral_quaternions()
    keys = set(values)
    maximum_norm_error = max(abs(sum(component * component for component in q) - 1.0) for q in values)
    maximum_unitarity_error = max(
        float(np.max(np.abs(dirac_2i_matrix(q).conj().T @ dirac_2i_matrix(q) - np.eye(4))))
        for q in values
    )
    closure_failures = sum(
        _quaternion_key(quaternion_multiply(left, right)) not in keys
        for left in values
        for right in values
    )
    return {
        "cardinality": len(values),
        "maximum_norm_error": maximum_norm_error,
        "maximum_unitarity_error": maximum_unitarity_error,
        "multiplication_closure_failures": closure_failures,
        "central_sign_closed": all(_quaternion_key(tuple(-x for x in q)) in keys for q in values),
    }


@dataclass(frozen=True)
class DiracCartan2IYukawaConfig:
    points: int = 17
    half_width: float = 8.0
    winding: int = 3
    contour_radius: float = 2.4
    core_radius: float = 0.9
    envelope_width: float = 2.0
    charge: float = 1.0
    yukawa_coupling: float = 0.20
    higgs_vev: float = math.sqrt(2.0)
    c: float = 1.0
    hbar: float = 1.0
    cartan_coupling: float = 0.025

    def __post_init__(self) -> None:
        if self.points < 9 or self.points % 2 == 0:
            raise ValueError("an odd three-dimensional grid with at least nine points is required")
        if min(
            self.half_width,
            self.contour_radius,
            self.core_radius,
            self.envelope_width,
            self.higgs_vev,
            self.c,
            self.hbar,
            self.cartan_coupling,
        ) <= 0.0:
            raise ValueError("positive M10 controls required")
        if self.winding == 0 or self.charge == 0.0 or self.yukawa_coupling == 0.0:
            raise ValueError("nonzero winding, charge, and Yukawa coupling required")
        if self.contour_radius >= self.half_width:
            raise ValueError("the winding contour must lie inside the periodic half box")

    @property
    def spacing(self) -> float:
        return 2.0 * self.half_width / self.points

    @property
    def yukawa_mass(self) -> float:
        return self.yukawa_coupling * self.higgs_vev / math.sqrt(2.0)

    @property
    def compton_frequency(self) -> float:
        return self.yukawa_mass * self.c * self.c / self.hbar

    @property
    def yukawa_decoherence_width(self) -> float:
        return self.yukawa_coupling * self.compton_frequency / self.hbar

    @property
    def entropy_rate(self) -> float:
        return 0.5 * self.yukawa_decoherence_width

    @property
    def imaginary_mass(self) -> float:
        return self.entropy_rate / (self.c * self.c)

    def geometry(self) -> PeriodicFourierGeometry:
        return PeriodicFourierGeometry(
            (self.points, self.points, self.points),
            (self.spacing, self.spacing, self.spacing),
        )


@dataclass(frozen=True)
class DiracCartan2IYukawaState:
    spinor: np.ndarray
    scalar_potential: np.ndarray
    vector_potential: Vector
    electric_field: Vector
    magnetic_field: Vector
    axial_current: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    contorsion: tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
    cartan_contact_density: np.ndarray
    time: float
    entropic_time: float
    measured_winding: int
    winding_quantization_error: float
    minimum_contour_amplitude: float
    construction: str

    def __post_init__(self) -> None:
        if self.spinor.ndim != 4 or self.spinor.shape[0] != 4:
            raise ValueError("a four-component three-dimensional Dirac spinor is required")
        shape = tuple(self.spinor.shape[1:])
        fields = (
            self.scalar_potential,
            *self.vector_potential,
            *self.electric_field,
            *self.magnetic_field,
            *self.axial_current,
            *self.contorsion,
            self.cartan_contact_density,
        )
        if any(tuple(field.shape) != shape for field in fields):
            raise ValueError("all M10 fields must share one spatial grid")
        if self.time < 0.0 or self.entropic_time < 0.0 or not self.construction:
            raise ValueError("nonnegative times and construction metadata required")

    def manifest(self, cfg: DiracCartan2IYukawaConfig) -> dict[str, Any]:
        return {
            "schema": "openwave.m10.dirac-cartan-2i-yukawa-state.v1",
            "shape": list(self.spinor.shape),
            "spacing": cfg.spacing,
            "yukawa_mass": cfg.yukawa_mass,
            "compton_frequency": cfg.compton_frequency,
            "entropy_rate": cfg.entropy_rate,
            "measured_winding": self.measured_winding,
            "winding_quantization_error": self.winding_quantization_error,
            "time": self.time,
            "entropic_time": self.entropic_time,
            "construction": self.construction,
            "state_fingerprint": state_fingerprint(self, cfg),
        }


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def state_fingerprint(state: DiracCartan2IYukawaState, cfg: DiracCartan2IYukawaConfig) -> str:
    digest = sha256(_canonical_json(asdict(cfg)).encode())
    for array in (
        state.spinor,
        state.scalar_potential,
        *state.vector_potential,
        *state.electric_field,
        *state.magnetic_field,
        *state.axial_current,
        *state.contorsion,
        state.cartan_contact_density,
    ):
        contiguous = np.ascontiguousarray(array)
        digest.update(str(contiguous.shape).encode())
        digest.update(contiguous.view(np.uint8).tobytes())
    digest.update(
        _canonical_json(
            {
                "time": state.time,
                "entropic_time": state.entropic_time,
                "winding": state.measured_winding,
                "construction": state.construction,
            }
        ).encode()
    )
    return digest.hexdigest()


def normalize_spinor(spinor: np.ndarray, cfg: DiracCartan2IYukawaConfig) -> np.ndarray:
    norm = float(np.sum(np.abs(spinor) ** 2) * cfg.geometry().cell_volume)
    if norm <= 0.0 or not math.isfinite(norm):
        raise ValueError("positive finite spinor norm required")
    return np.asarray(spinor / math.sqrt(norm), dtype=np.complex128)


def winding_seed(cfg: DiracCartan2IYukawaConfig) -> np.ndarray:
    axis = (np.arange(cfg.points, dtype=np.float64) - cfg.points / 2.0) * cfg.spacing
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    radial = np.hypot(x, y)
    angle = np.arctan2(y, x)
    core = np.tanh(radial / cfg.core_radius) ** abs(cfg.winding)
    envelope = np.exp(-(x * x + y * y + z * z) / (2.0 * cfg.envelope_width**2))
    scalar = core * envelope * np.exp(1.0j * cfg.winding * angle)
    spinor = np.zeros((4, cfg.points, cfg.points, cfg.points), dtype=np.complex128)
    spinor[0] = scalar
    return normalize_spinor(spinor, cfg)


def _matrix_bilinear(spinor: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    operated = np.einsum("ab,bxyz->axyz", matrix, spinor, optimize=True)
    return np.asarray(np.real(np.sum(np.conj(spinor) * operated, axis=0)), dtype=np.float64)


def dirac_charge_current(spinor: np.ndarray, cfg: DiracCartan2IYukawaConfig) -> tuple[np.ndarray, Vector]:
    density = np.asarray(np.sum(np.abs(spinor) ** 2, axis=0), dtype=np.float64)
    current = tuple(cfg.charge * _matrix_bilinear(spinor, alpha) for alpha in ALPHAS)
    return np.asarray(cfg.charge * density, dtype=np.float64), current  # type: ignore[return-value]


def axial_current(spinor: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    return tuple(_matrix_bilinear(spinor, matrix) for matrix in AXIAL_MATRICES)  # type: ignore[return-value]


def cartan_fields(
    spinor: np.ndarray, cfg: DiracCartan2IYukawaConfig
) -> tuple[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], np.ndarray]:
    current = axial_current(spinor)
    contorsion = tuple(cfg.cartan_coupling * component for component in current)
    contact = -0.5 * cfg.cartan_coupling * sum(component * component for component in current)
    return current, contorsion, np.asarray(contact, dtype=np.float64)  # type: ignore[return-value]


def refresh_state(
    spinor: np.ndarray,
    cfg: DiracCartan2IYukawaConfig,
    *,
    time: float = 0.0,
    entropic_time: float = 0.0,
    construction: str,
) -> DiracCartan2IYukawaState:
    geometry = cfg.geometry()
    charge_density, current = dirac_charge_current(spinor, cfg)
    fields = geometry.static_maxwell_fields(charge_density, current)
    axial, contorsion, contact = cartan_fields(spinor, cfg)
    winding = periodic_contour_winding(
        np.asarray(spinor[0], dtype=np.complex128), cfg.spacing, radius=cfg.contour_radius
    )
    return DiracCartan2IYukawaState(
        spinor=np.asarray(spinor, dtype=np.complex128),
        scalar_potential=np.asarray(fields["potential"], dtype=np.float64),
        vector_potential=tuple(np.asarray(value, dtype=np.float64) for value in fields["vector_potential"]),
        electric_field=tuple(np.asarray(value, dtype=np.float64) for value in fields["electric"]),
        magnetic_field=tuple(np.asarray(value, dtype=np.float64) for value in fields["magnetic"]),
        axial_current=axial,
        contorsion=contorsion,
        cartan_contact_density=contact,
        time=time,
        entropic_time=entropic_time,
        measured_winding=int(winding["integer_winding"]),
        winding_quantization_error=float(winding["quantization_error"]),
        minimum_contour_amplitude=float(winding["minimum_contour_amplitude"]),
        construction=construction,
    )


def construct_state(
    cfg: DiracCartan2IYukawaConfig = DiracCartan2IYukawaConfig(),
) -> DiracCartan2IYukawaState:
    return refresh_state(winding_seed(cfg), cfg, construction="four-spinor-winding-yukawa-cartan-seed")


def dirac_hamiltonian_action(
    spinor: np.ndarray,
    state: DiracCartan2IYukawaState,
    cfg: DiracCartan2IYukawaConfig,
) -> np.ndarray:
    geometry = cfg.geometry()
    result = np.zeros_like(spinor, dtype=np.complex128)
    for axis, alpha in enumerate(ALPHAS):
        covariant = geometry.derivative(spinor, axis)
        covariant -= 1.0j * cfg.charge * state.vector_potential[axis][None, ...] * spinor
        result += -1.0j * np.einsum("ab,bxyz->axyz", alpha, covariant, optimize=True)

    complex_mass = cfg.yukawa_mass + 1.0j * cfg.imaginary_mass
    result += complex_mass * np.einsum("ab,bxyz->axyz", BETA, spinor, optimize=True)
    result += cfg.charge * state.scalar_potential[None, ...] * spinor

    for component, matrix in zip(state.axial_current, AXIAL_MATRICES, strict=True):
        operated = np.einsum("ab,bxyz->axyz", matrix, spinor, optimize=True)
        result -= cfg.cartan_coupling * component[None, ...] * operated
    return np.asarray(result, dtype=np.complex128)


def dirac_mass_shell_residual(cfg: DiracCartan2IYukawaConfig, momentum: tuple[float, float, float]) -> float:
    hamiltonian = sum(momentum[index] * ALPHAS[index] for index in range(3)) + cfg.yukawa_mass * BETA
    expected = (sum(value * value for value in momentum) + cfg.yukawa_mass**2) * np.eye(4)
    return float(np.max(np.abs(hamiltonian @ hamiltonian - expected)))


def canonical_payload(cfg: DiracCartan2IYukawaConfig | None = None) -> dict[str, Any]:
    selected = cfg or DiracCartan2IYukawaConfig()
    return {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "model_id": "M10",
        "model": "CAT/EPT Dirac-Cartan-2I-Compton-Yukawa",
        "config": asdict(selected),
        "formal_authority": {
            "repository": FORMAL_REPOSITORY,
            "branch": FORMAL_BRANCH,
            "sources": [
                "Physlib/QuantumMechanics/ComplexAction/BinaryIcosahedralDiracSpinor.lean",
                "Physlib/QuantumMechanics/ComplexAction/EinsteinCartanAxialTorsion.lean",
                "Physlib/QuantumMechanics/ComplexAction/DiracCartanComptonYukawaBridge.lean",
            ],
        },
        "state_api": "openwave.xperiments.m10_cat_ept.dirac_cartan_2i_yukawa_model:DiracCartan2IYukawaState",
        "construction_api": "openwave.xperiments.m10_cat_ept.dirac_cartan_2i_yukawa_model:construct_state",
        "establishes": [
            "complete 120-element binary-icosahedral quaternion set",
            "unitary four-spinor lift and central-pair bilinear descent",
            "four-spinor U1 carrier with measured winding",
            "Yukawa mass and Compton clock identity",
            "complex Yukawa mass entropy rate",
            "algebraic axial Cartan contorsion and contact density",
            "Dirac mass-shell matrix identity",
        ],
    }


def fingerprint(payload: Mapping[str, Any] | None = None) -> str:
    selected = canonical_payload() if payload is None else dict(payload)
    return sha256(_canonical_json(selected).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_m10_core_study() -> dict[str, Any]:
    cfg = DiracCartan2IYukawaConfig()
    geometry = cfg.geometry()
    state = construct_state(cfg)
    group = binary_icosahedral_diagnostics()

    transformed = apply_binary_icosahedral(state.spinor, binary_icosahedral_quaternions()[17])
    central = apply_binary_icosahedral(
        state.spinor, tuple(-value for value in binary_icosahedral_quaternions()[17])  # type: ignore[arg-type]
    )
    density = np.sum(np.abs(transformed) ** 2, axis=0)
    central_density = np.sum(np.abs(central) ** 2, axis=0)
    central_density_error = float(np.max(np.abs(density - central_density)))

    charge_density, current = dirac_charge_current(state.spinor, cfg)
    maxwell = geometry.static_maxwell_fields(charge_density, current)
    norm = float(np.sum(np.abs(state.spinor) ** 2) * geometry.cell_volume)
    integrated_charge = float(np.sum(charge_density) * geometry.cell_volume)
    cartan_residual = max(
        float(np.max(np.abs(state.contorsion[index] - cfg.cartan_coupling * state.axial_current[index])))
        for index in range(4)
    )
    mass_clock_error = abs(cfg.hbar * cfg.compton_frequency - cfg.yukawa_mass * cfg.c * cfg.c)
    entropy_rate_error = abs(
        cfg.entropy_rate - cfg.yukawa_coupling * cfg.compton_frequency / (2.0 * cfg.hbar)
    )
    mass_shell_error = dirac_mass_shell_residual(cfg, (0.31, -0.17, 0.09))

    acceptance = {
        "binary_icosahedral_group_has_120_elements": group["cardinality"] == 120,
        "binary_icosahedral_coordinates_are_unit": group["maximum_norm_error"] <= 2.0e-12,
        "binary_icosahedral_multiplication_closes": group["multiplication_closure_failures"] == 0,
        "four_spinor_lift_is_unitary": group["maximum_unitarity_error"] <= 2.0e-12,
        "central_pair_descends_on_density": central_density_error <= 2.0e-12,
        "four_component_3d_state_is_constructed": tuple(state.spinor.shape) == (4, cfg.points, cfg.points, cfg.points),
        "winding_three_is_measured_from_the_field": (
            state.measured_winding == cfg.winding
            and state.winding_quantization_error <= 2.0e-12
            and state.minimum_contour_amplitude > 1.0e-3
        ),
        "normalization_and_charge_close": abs(norm - 1.0) <= 2.0e-12 and abs(integrated_charge - cfg.charge) <= 2.0e-12,
        "static_u1_constraints_close": (
            maxwell["gauss_relative_residual"] <= 1.0e-11
            and maxwell["ampere_relative_residual"] <= 1.0e-11
            and maxwell["magnetic_divergence_max"] <= 1.0e-11
        ),
        "cartan_spin_source_equation_closes": cartan_residual <= 2.0e-15,
        "yukawa_compton_clock_identity_closes": mass_clock_error <= 2.0e-15,
        "complex_mass_entropy_rate_closes": entropy_rate_error <= 2.0e-15,
        "dirac_mass_shell_closes": mass_shell_error <= 2.0e-14,
        "state_manifest_is_replay_identifiable": len(state.manifest(cfg)["state_fingerprint"]) == 64,
    }
    payload = canonical_payload(cfg)
    return {
        **payload,
        "task": "M10.1a-f",
        "fingerprint": fingerprint(payload),
        "group_diagnostics": group,
        "central_density_error": central_density_error,
        "norm": norm,
        "integrated_charge": integrated_charge,
        "measured_winding": state.measured_winding,
        "cartan_residual": cartan_residual,
        "mass_clock_error": mass_clock_error,
        "entropy_rate_error": entropy_rate_error,
        "dirac_mass_shell_error": mass_shell_error,
        "maxwell": {
            key: float(maxwell[key])
            for key in ("gauss_relative_residual", "ampere_relative_residual", "magnetic_divergence_max")
        },
        "final_state_manifest": state.manifest(cfg),
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "dirac_cartan_2i_yukawa_carrier_constructed": True,
            "complete_binary_icosahedral_action_executed": True,
            "yukawa_compton_complex_mass_assembled": True,
            "cartan_axial_contact_assembled": True,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
