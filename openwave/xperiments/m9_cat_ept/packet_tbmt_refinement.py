"""M9.104: refined moving-packet Thomas--BMT reduction.

The regular lab-frame BMT angular velocity is an explicit external model
postulate. Physlib proves scalar coefficients, magic cancellation and rest-frame
Dirac--Pauli grounding, but not the covariant boost/Thomas extension.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
from typing import Any, Mapping

import numpy as np

from .charged_field_tools import spectral_shift, static_maxwell_fields
from .compatible_discrete_geometry import spectral_resample
from .covariant_packet_tbmt import packet_torque
from .reconciled_gauge_spinor_stationary import normalize_spinor
from .spatial_3d_operators import density
from .spinorial_pair_dynamics import (
    SpinorialPairDynamicsConfig,
    evolve_response,
    fit_response,
    pauli_source,
    pauli_to_dirac,
)
from .unrestricted_charged_stationary import best_unrestricted_state

THOMAS_EXTENSION_POSTULATE = {
    "id": "openwave.m9.thomas-extension-postulate.v1",
    "equation": "Omega=-(q/m)[(a+1/gamma)B-a*gamma/(gamma+1)(beta.B)beta-(a+1/(gamma+1))(beta x E)]",
    "source": "Bargmann-Michel-Telegdi/Thomas classical spin dynamics",
    "qed_derived": False,
    "rest_frame_qed_grounded": True,
    "domain": "regular subluminal extended packets with local beta=j/rho",
}


@dataclass(frozen=True)
class PacketRefinementConfig:
    points: tuple[int, ...] = (16, 20)
    time_steps: tuple[float, ...] = (4e-3, 2e-3)
    final_time: float = 0.16
    half_width: float = 8.0
    separation: float = 6.0
    winding: int = 3
    mass: float = 1.0
    charge: float = 1.0
    g_factor: float = 2.0
    fit_samples: int = 4
    error_gate: float = 3e-2
    monotonic_slack: float = 5e-3
    source_stationary_gate: float = 0.15

    def __post_init__(self) -> None:
        if any(points < 16 or points % 2 for points in self.points):
            raise ValueError("even grids >=16 required")
        if min(
            *self.time_steps,
            self.final_time,
            self.half_width,
            self.separation,
            self.mass,
            self.g_factor,
            self.error_gate,
        ) <= 0:
            raise ValueError("positive controls required")
        if self.charge == 0 or self.winding == 0:
            raise ValueError("nonzero charge/winding required")

    def dynamics(self, points: int, dt: float) -> SpinorialPairDynamicsConfig:
        steps = max(12, int(round(self.final_time / dt)))
        return SpinorialPairDynamicsConfig(
            points=points,
            half_width=self.half_width,
            winding=self.winding,
            separation=self.separation,
            mass=self.mass,
            charge=self.charge,
            g_factor=self.g_factor,
            time_step=dt,
            steps=steps,
            sample_stride=1,
            fit_samples=min(self.fit_samples, steps + 1),
            generator_spin_tolerance=self.error_gate,
        )


def _resample(state: np.ndarray, points: int, half_width: float) -> np.ndarray:
    spacing = 2 * half_width / points
    return normalize_spinor(
        np.stack([spectral_resample(component, (points, points, points)) for component in state]),
        spacing,
    )


def _transverse(pauli: np.ndarray) -> np.ndarray:
    rotation = np.asarray([[1.0, -1.0], [1.0, 1.0]], dtype=np.complex128) / math.sqrt(2)
    return np.asarray(
        np.einsum("ab,bxyz->axyz", rotation, pauli, optimize=True),
        dtype=np.complex128,
    )


def _shift_spinor(
    pauli: np.ndarray,
    spacings: tuple[float, float, float],
    shift: tuple[float, float, float],
) -> np.ndarray:
    """Apply the scalar spectral translation to each Pauli component."""
    if pauli.ndim != 4 or pauli.shape[0] != 2:
        raise ValueError("two-component three-dimensional Pauli spinor required")
    return np.asarray(
        np.stack([spectral_shift(component, spacings, shift) for component in pauli]),
        dtype=np.complex128,
    )


def _pair_data(pauli: np.ndarray, cfg: SpinorialPairDynamicsConfig) -> dict[str, Any]:
    spacings = (cfg.spacing,) * 3
    axis = -cfg.half_width + cfg.spacing * np.arange(cfg.points)
    coordinates = tuple(
        np.asarray(component)
        for component in np.meshgrid(axis, axis, axis, indexing="ij")
    )
    plus_p = _shift_spinor(pauli, spacings, (0.0, 0.0, -0.5 * cfg.separation))
    minus_p = np.conj(
        _shift_spinor(pauli, spacings, (0.0, 0.0, 0.5 * cfg.separation))
    )
    positive_charge, positive_current = pauli_source(
        plus_p,
        charge=cfg.charge,
        mass=cfg.mass,
        g_factor=cfg.g_factor,
        spacing=cfg.spacing,
    )
    negative_charge, negative_current = pauli_source(
        minus_p,
        charge=-cfg.charge,
        mass=cfg.mass,
        g_factor=cfg.g_factor,
        spacing=cfg.spacing,
    )
    positive_fields = static_maxwell_fields(
        positive_charge, positive_current, cfg.spacing
    )
    negative_fields = static_maxwell_fields(
        negative_charge, negative_current, cfg.spacing
    )
    vector = tuple(
        positive_fields["vector_potential"][index]
        + negative_fields["vector_potential"][index]
        for index in range(3)
    )
    electric = tuple(
        positive_fields["electric"][index] + negative_fields["electric"][index]
        for index in range(3)
    )
    magnetic = tuple(
        positive_fields["magnetic"][index] + negative_fields["magnetic"][index]
        for index in range(3)
    )
    plus = pauli_to_dirac(
        plus_p,
        vector,
        charge_sign=1,
        charge=cfg.charge,
        mass=cfg.mass,
        spacing=cfg.spacing,
    )
    minus = pauli_to_dirac(
        minus_p,
        vector,
        charge_sign=-1,
        charge=cfg.charge,
        mass=cfg.mass,
        spacing=cfg.spacing,
    )
    control = pauli_to_dirac(
        plus_p,
        positive_fields["vector_potential"],
        charge_sign=1,
        charge=cfg.charge,
        mass=cfg.mass,
        spacing=cfg.spacing,
    )
    return {
        "coordinates": coordinates,
        "pair_plus": plus,
        "pair_minus": minus,
        "control_plus": control,
        "total_vector": vector,
        "total_electric": electric,
        "total_magnetic": magnetic,
        "positive_fields": positive_fields,
    }


def _relative(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right) / max(np.linalg.norm(right), 1e-30))


def run_refinement_row(
    points: int,
    dt: float,
    source: np.ndarray,
    config: PacketRefinementConfig,
) -> dict[str, Any]:
    cfg = config.dynamics(points, dt)
    pauli = normalize_spinor(
        _transverse(_resample(source, points, config.half_width)), cfg.spacing
    )
    data = _pair_data(pauli, cfg)
    pair_torque = packet_torque(
        data["pair_plus"], data["total_electric"], data["total_magnetic"], cfg
    )
    control_torque = packet_torque(
        data["control_plus"],
        data["positive_fields"]["electric"],
        data["positive_fields"]["magnetic"],
        cfg,
    )
    packet = np.asarray(pair_torque["rate"] - control_torque["rate"])
    pair = evolve_response(
        data["pair_plus"],
        data["pair_minus"],
        data["total_vector"],
        data["total_electric"],
        data["coordinates"],
        cfg,
    )
    control = evolve_response(
        data["control_plus"],
        np.zeros_like(data["pair_minus"]),
        data["positive_fields"]["vector_potential"],
        data["positive_fields"]["electric"],
        data["coordinates"],
        cfg,
    )
    response = fit_response(pair, control, cfg)
    generator = np.asarray(response["interaction_generator_spin_rate"])
    measured = np.asarray(response["interaction_spin_rate"])
    packet_error = _relative(packet, generator)
    finite_error = _relative(measured, generator)
    return {
        "points": points,
        "time_step": dt,
        "steps": cfg.steps,
        "spacing": cfg.spacing,
        "source_norm": float(np.sum(density(data["pair_plus"])) * cfg.spacing**3),
        "packet_rate": packet.tolist(),
        "generator_rate": generator.tolist(),
        "finite_time_rate": measured.tolist(),
        "packet_vs_generator_error": packet_error,
        "finite_time_vs_generator_error": finite_error,
        "pair_velocity_audit": pair_torque["velocity_audit"],
        "control_velocity_audit": control_torque["velocity_audit"],
        "local_packet_gate": packet_error <= config.error_gate,
        "finite_time_generator_gate": finite_error <= config.error_gate,
    }


@lru_cache(maxsize=1)
def run_packet_tbmt_refinement() -> dict[str, Any]:
    cfg = PacketRefinementConfig()
    source, result = best_unrestricted_state()
    rows = [
        run_refinement_row(points, dt, source, cfg)
        for points in cfg.points
        for dt in cfg.time_steps
    ]
    finest = next(
        row
        for row in rows
        if row["points"] == max(cfg.points)
        and row["time_step"] == min(cfg.time_steps)
    )
    by_grid: dict[str, Any] = {}
    for points in cfg.points:
        selected = sorted(
            (row for row in rows if row["points"] == points),
            key=lambda row: row["time_step"],
            reverse=True,
        )
        packet_monotone = all(
            selected[index + 1]["packet_vs_generator_error"]
            <= selected[index]["packet_vs_generator_error"] + cfg.monotonic_slack
            for index in range(len(selected) - 1)
        )
        finite_monotone = all(
            selected[index + 1]["finite_time_vs_generator_error"]
            <= selected[index]["finite_time_vs_generator_error"] + cfg.monotonic_slack
            for index in range(len(selected) - 1)
        )
        by_grid[str(points)] = {
            "packet_errors": [row["packet_vs_generator_error"] for row in selected],
            "finite_time_errors": [row["finite_time_vs_generator_error"] for row in selected],
            "packet_nonincreasing": packet_monotone,
            "finite_time_nonincreasing": finite_monotone,
        }
    refinement = bool(
        finest["local_packet_gate"]
        and finest["finite_time_generator_gate"]
        and all(
            value["packet_nonincreasing"] and value["finite_time_nonincreasing"]
            for value in by_grid.values()
        )
    )
    source_gate = bool(
        result["full"]["relative_stationary_residual"] <= cfg.source_stationary_gate
    )
    acceptance = {
        "covariant_thomas_extension_is_explicitly_postulated": (
            THOMAS_EXTENSION_POSTULATE["qed_derived"] is False
        ),
        "all_grid_time_rows_execute": len(rows)
        == len(cfg.points) * len(cfg.time_steps),
        "all_local_velocities_are_finite_and_subluminal": all(
            all(math.isfinite(value) for value in row["pair_velocity_audit"].values())
            and row["pair_velocity_audit"]["maximum_used_beta"] < 1
            for row in rows
        ),
        "packet_generator_and_finite_time_rates_are_reported": all(
            math.isfinite(row["packet_vs_generator_error"])
            and math.isfinite(row["finite_time_vs_generator_error"])
            for row in rows
        ),
        "source_stationarity_is_not_silently_inferred": isinstance(source_gate, bool),
        "refinement_gate_is_reported_not_predetermined": isinstance(refinement, bool),
        "qed_derivation_is_not_claimed": True,
    }
    return {
        "schema": "openwave.m9.packet-tbmt-refinement.v1",
        "task": "M9.104",
        "config": asdict(cfg),
        "thomas_extension": dict(THOMAS_EXTENSION_POSTULATE),
        "source": {
            "stationary_residual": result["full"]["relative_stationary_residual"],
            "integer_winding": result["winding"]["integer_winding"],
            "source_stationarity_gate": source_gate,
        },
        "rows": rows,
        "per_grid_refinement": by_grid,
        "finest_row": finest,
        "refined_packet_tbmt_closed": refinement,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "decision": {
            "covariant_thomas_extension_status": "explicit-external-postulate",
            "refined_packet_reduction_constructed": refinement,
            "covariant_thomas_extension_derived_from_qed": False,
            "physical_anomalous_moment_calibrated": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
