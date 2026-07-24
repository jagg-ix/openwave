"""Finite-grid SU(3) color and quark-ledger controls.

This module follows the reusable carriers identified through the
`entropic-physlib-linear-full` ZIL and Lean surfaces:

- `StandardModel.GaugeGroupI.toSU3`;
- `CKMMatrix` as a unitary 3x3 matrix;
- phase-shift equivalence of quark mixing matrices.

The implementation qualifies finite-dimensional color covariance, singlet
invariance, Wilson-loop gauge invariance, fractional-charge ledgers, and a
phase-invariant CKM control. It does not implement QCD dynamics.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import expm

ComplexMatrix = NDArray[np.complex128]
ComplexVector = NDArray[np.complex128]


@dataclass(frozen=True)
class QuarkColorConfig:
    gauge_scale: float = 0.23
    ckm_theta12: float = 0.227
    ckm_theta23: float = 0.041
    ckm_theta13: float = 0.0037
    ckm_delta: float = 1.20

    def __post_init__(self) -> None:
        if self.gauge_scale <= 0.0:
            raise ValueError("positive gauge scale required")
        if any(
            value < 0.0
            for value in (
                self.ckm_theta12,
                self.ckm_theta23,
                self.ckm_theta13,
            )
        ):
            raise ValueError("nonnegative mixing angles required")


def gell_mann_generators() -> tuple[ComplexMatrix, ...]:
    zero = np.zeros((3, 3), dtype=np.complex128)
    matrices = []
    entries = (
        ((0, 1, 1.0), (1, 0, 1.0)),
        ((0, 1, -1j), (1, 0, 1j)),
        ((0, 0, 1.0), (1, 1, -1.0)),
        ((0, 2, 1.0), (2, 0, 1.0)),
        ((0, 2, -1j), (2, 0, 1j)),
        ((1, 2, 1.0), (2, 1, 1.0)),
        ((1, 2, -1j), (2, 1, 1j)),
    )
    for specification in entries:
        matrix = zero.copy()
        for row, column, value in specification:
            matrix[row, column] = value
        matrices.append(0.5 * matrix)
    matrices.append(
        np.diag([1.0, 1.0, -2.0]).astype(np.complex128)
        / (2.0 * math.sqrt(3.0))
    )
    return tuple(matrices)


def generator_diagnostics() -> dict[str, float]:
    generators = gell_mann_generators()
    hermitian = max(
        float(np.max(np.abs(matrix - matrix.conj().T)))
        for matrix in generators
    )
    trace = max(abs(complex(np.trace(matrix))) for matrix in generators)
    gram = np.asarray(
        [
            [float(np.trace(left @ right).real) for right in generators]
            for left in generators
        ]
    )
    orthogonality = float(np.max(np.abs(gram - 0.5 * np.eye(8))))

    closure = 0.0
    for left in generators:
        for right in generators:
            commutator = left @ right - right @ left
            coefficients = np.asarray(
                [2.0 * np.trace(generator @ commutator) for generator in generators],
                dtype=np.complex128,
            )
            reconstructed = sum(
                coefficient * generator
                for coefficient, generator in zip(coefficients, generators)
            )
            closure = max(
                closure,
                float(np.max(np.abs(commutator - reconstructed))),
            )
    return {
        "maximum_hermitian_error": hermitian,
        "maximum_trace_error": float(trace),
        "orthogonality_error": orthogonality,
        "commutator_closure_error": closure,
    }


def su3_element(coefficients: NDArray[np.float64]) -> ComplexMatrix:
    coefficients = np.asarray(coefficients, dtype=np.float64)
    if coefficients.shape != (8,):
        raise ValueError("eight SU(3) coefficients required")
    hermitian = sum(
        coefficient * generator
        for coefficient, generator in zip(coefficients, gell_mann_generators())
    )
    return expm(1j * hermitian)


def deterministic_su3(seed: int, scale: float = 0.23) -> ComplexMatrix:
    rng = np.random.default_rng(seed)
    return su3_element(scale * rng.normal(size=8))


def su3_diagnostics(matrix: ComplexMatrix) -> dict[str, float]:
    matrix = np.asarray(matrix, dtype=np.complex128)
    if matrix.shape != (3, 3):
        raise ValueError("3x3 matrix required")
    return {
        "unitarity_error": float(
            np.max(np.abs(matrix.conj().T @ matrix - np.eye(3)))
        ),
        "determinant_error": abs(complex(np.linalg.det(matrix)) - 1.0),
    }


def meson_singlet() -> ComplexMatrix:
    return np.eye(3, dtype=np.complex128) / math.sqrt(3.0)


def transform_meson(state: ComplexMatrix, gauge: ComplexMatrix) -> ComplexMatrix:
    return gauge @ state @ gauge.conj().T


def baryon_singlet() -> NDArray[np.complex128]:
    tensor = np.zeros((3, 3, 3), dtype=np.complex128)
    permutations = (
        ((0, 1, 2), 1.0),
        ((1, 2, 0), 1.0),
        ((2, 0, 1), 1.0),
        ((0, 2, 1), -1.0),
        ((2, 1, 0), -1.0),
        ((1, 0, 2), -1.0),
    )
    for indices, sign in permutations:
        tensor[indices] = sign / math.sqrt(6.0)
    return tensor


def transform_baryon(
    state: NDArray[np.complex128],
    gauge: ComplexMatrix,
) -> NDArray[np.complex128]:
    return np.einsum("ia,jb,kc,abc->ijk", gauge, gauge, gauge, state)


def plaquette(
    links: tuple[ComplexMatrix, ComplexMatrix, ComplexMatrix, ComplexMatrix],
) -> ComplexMatrix:
    bottom, right, top, left = links
    return bottom @ right @ top.conj().T @ left.conj().T


def transform_plaquette_links(
    links: tuple[ComplexMatrix, ComplexMatrix, ComplexMatrix, ComplexMatrix],
    gauges: tuple[ComplexMatrix, ComplexMatrix, ComplexMatrix, ComplexMatrix],
) -> tuple[ComplexMatrix, ComplexMatrix, ComplexMatrix, ComplexMatrix]:
    bottom, right, top, left = links
    g00, g10, g11, g01 = gauges
    return (
        g00 @ bottom @ g10.conj().T,
        g10 @ right @ g11.conj().T,
        g01 @ top @ g11.conj().T,
        g00 @ left @ g01.conj().T,
    )


def wilson_trace(
    links: tuple[ComplexMatrix, ComplexMatrix, ComplexMatrix, ComplexMatrix],
) -> complex:
    return complex(np.trace(plaquette(links)) / 3.0)


QUARK_CHARGES = {
    "u": 2.0 / 3.0,
    "d": -1.0 / 3.0,
    "anti_u": -2.0 / 3.0,
    "anti_d": 1.0 / 3.0,
}


def composite_charge(constituents: tuple[str, ...]) -> float:
    if any(name not in QUARK_CHARGES for name in constituents):
        raise ValueError("unknown quark type")
    return float(sum(QUARK_CHARGES[name] for name in constituents))


def ckm_matrix(cfg: QuarkColorConfig = QuarkColorConfig()) -> ComplexMatrix:
    s12, s23, s13 = (
        math.sin(cfg.ckm_theta12),
        math.sin(cfg.ckm_theta23),
        math.sin(cfg.ckm_theta13),
    )
    c12, c23, c13 = (
        math.cos(cfg.ckm_theta12),
        math.cos(cfg.ckm_theta23),
        math.cos(cfg.ckm_theta13),
    )
    phase = np.exp(1j * cfg.ckm_delta)
    phase_conj = phase.conjugate()
    return np.asarray(
        [
            [c12 * c13, s12 * c13, s13 * phase_conj],
            [
                -s12 * c23 - c12 * s23 * s13 * phase,
                c12 * c23 - s12 * s23 * s13 * phase,
                s23 * c13,
            ],
            [
                s12 * s23 - c12 * c23 * s13 * phase,
                -c12 * s23 - s12 * c23 * s13 * phase,
                c23 * c13,
            ],
        ],
        dtype=np.complex128,
    )


def phase_shift_matrix(phases: tuple[float, float, float]) -> ComplexMatrix:
    return np.diag([np.exp(1j * phase) for phase in phases]).astype(np.complex128)


def ckm_phase_shift(
    matrix: ComplexMatrix,
    left: tuple[float, float, float],
    right: tuple[float, float, float],
) -> ComplexMatrix:
    return phase_shift_matrix(left) @ matrix @ phase_shift_matrix(right)


def jarlskog_invariant(matrix: ComplexMatrix) -> float:
    return float(
        np.imag(
            matrix[0, 0]
            * matrix[1, 1]
            * np.conjugate(matrix[0, 1])
            * np.conjugate(matrix[1, 0])
        )
    )


@lru_cache(maxsize=1)
def run_quark_color_study() -> dict[str, Any]:
    cfg = QuarkColorConfig()
    generators = generator_diagnostics()
    gauge = deterministic_su3(11, cfg.gauge_scale)
    gauge_diag = su3_diagnostics(gauge)

    meson = meson_singlet()
    baryon = baryon_singlet()
    meson_error = float(np.max(np.abs(transform_meson(meson, gauge) - meson)))
    baryon_error = float(np.max(np.abs(transform_baryon(baryon, gauge) - baryon)))

    links = tuple(deterministic_su3(seed, 0.17) for seed in (21, 22, 23, 24))
    gauges = tuple(deterministic_su3(seed, 0.19) for seed in (31, 32, 33, 34))
    transformed_links = transform_plaquette_links(links, gauges)
    wilson_error = abs(wilson_trace(transformed_links) - wilson_trace(links))

    ckm = ckm_matrix(cfg)
    shifted = ckm_phase_shift(ckm, (0.2, -0.4, 0.7), (-0.3, 0.5, -0.1))
    ckm_unitarity = float(np.max(np.abs(ckm.conj().T @ ckm - np.eye(3))))
    modulus_error = float(np.max(np.abs(np.abs(shifted) - np.abs(ckm))))
    jarlskog_error = abs(jarlskog_invariant(shifted) - jarlskog_invariant(ckm))

    charges = {
        "proton_uud": composite_charge(("u", "u", "d")),
        "neutron_udd": composite_charge(("u", "d", "d")),
        "pion_plus_u_antid": composite_charge(("u", "anti_d")),
        "pion_zero_u_antiu": composite_charge(("u", "anti_u")),
    }

    acceptance = {
        "su3_generators_are_hermitian_traceless_orthogonal": (
            generators["maximum_hermitian_error"] <= 2e-15
            and generators["maximum_trace_error"] <= 2e-15
            and generators["orthogonality_error"] <= 2e-15
        ),
        "su3_commutators_close": generators["commutator_closure_error"] <= 3e-15,
        "finite_gauge_element_is_special_unitary": (
            gauge_diag["unitarity_error"] <= 3e-15
            and gauge_diag["determinant_error"] <= 3e-15
        ),
        "meson_and_baryon_singlets_are_invariant": (
            meson_error <= 3e-15 and baryon_error <= 4e-15
        ),
        "wilson_loop_is_gauge_invariant": wilson_error <= 5e-15,
        "fractional_charge_ledgers_close": (
            abs(charges["proton_uud"] - 1.0) <= 1e-15
            and abs(charges["neutron_udd"]) <= 1e-15
            and abs(charges["pion_plus_u_antid"] - 1.0) <= 1e-15
            and abs(charges["pion_zero_u_antiu"]) <= 1e-15
        ),
        "ckm_is_unitary": ckm_unitarity <= 3e-15,
        "ckm_phase_equivalence_preserves_observables": (
            modulus_error <= 3e-15 and jarlskog_error <= 3e-15
        ),
    }

    return {
        "schema": "openwave.m9.quark-color-result.v1",
        "task": "M9.46",
        "config": asdict(cfg),
        "physlib_reuse": {
            "branch": "entropic-physlib-linear-full",
            "gauge_carrier": "StandardModel.GaugeGroupI.toSU3",
            "flavor_carrier": "CKMMatrix",
            "phase_equivalence": "PhaseShiftRelation",
            "zil_graphs": [
                "formalization/zil/liouville-second-quantization.zc",
                "formalization/zil/lindblad-driven-leads.zc",
            ],
        },
        "generator_diagnostics": generators,
        "gauge_element": gauge_diag,
        "meson_singlet_error": meson_error,
        "baryon_singlet_error": baryon_error,
        "wilson_loop_error": wilson_error,
        "charges": charges,
        "ckm": {
            "unitarity_error": ckm_unitarity,
            "phase_modulus_error": modulus_error,
            "jarlskog": jarlskog_invariant(ckm),
            "phase_jarlskog_error": jarlskog_error,
        },
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "classification": {
            "establishes": [
                "finite-dimensional SU(3) color carrier",
                "meson and baryon singlet invariance",
                "lattice Wilson-loop gauge covariance",
                "fractional quark-charge ledgers",
                "unitary CKM and phase-equivalence controls",
            ],
            "does_not_establish": [
                "dynamical QCD or gluon fields",
                "quarks emerging from the CAT/EPT PDE",
                "asymptotic freedom or running coupling",
                "physical hadron spectra or scattering",
            ],
        },
    }


def result_to_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
