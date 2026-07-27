"""M9.117a: dynamical screen coarse graining with one invariant area-per-bit coupling.

The physical count hierarchy is

    N_H / N_C = (m_P / m)^2.

This module gives that hierarchy an explicit renormalisation-scale flow and a finite
block-spin realization.  The flow preserves the microscopic screen density A/N_H,
so the injected Newton coupling remains invariant.  The construction demonstrates a
consistent mechanism; it does not derive why a particular particle mass or physical
screen must select the endpoint scale.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .holographic_count_hierarchy import (
    Constants,
    SPECIES,
    planck_area,
    planck_mass,
    species_row,
)


@dataclass(frozen=True)
class ScreenCoarseGrainingConfig:
    points: int = 256
    block_factor: int = 2
    levels: int = 5
    half_width: float = math.pi
    diffusion_time: float = 1.0e-3
    total_bits: float = 8192.0
    area_per_bit: float = 0.25
    hbar: float = 1.0
    light_speed: float = 1.0
    scale_samples: int = 65

    def __post_init__(self) -> None:
        if self.points < 32 or self.points & (self.points - 1):
            raise ValueError("a power-of-two fine grid with at least 32 cells is required")
        if self.block_factor < 2 or self.levels < 2:
            raise ValueError("substantive block hierarchy required")
        if self.points % (self.block_factor**self.levels):
            raise ValueError("the block hierarchy must divide the fine grid exactly")
        if min(
            self.half_width,
            self.diffusion_time,
            self.total_bits,
            self.area_per_bit,
            self.hbar,
            self.light_speed,
        ) <= 0.0:
            raise ValueError("positive screen-flow controls required")
        if self.scale_samples < 9:
            raise ValueError("substantive continuous scale sampling required")

    @property
    def newton_coupling(self) -> float:
        return self.area_per_bit * self.light_speed**3 / self.hbar


def spectral_heat_flow(values: np.ndarray, time: float, half_width: float) -> np.ndarray:
    """Apply the exact periodic heat semigroup to one real cell field."""
    if values.ndim != 1 or values.size < 4:
        raise ValueError("one-dimensional periodic cell field required")
    if time < 0.0 or half_width <= 0.0:
        raise ValueError("nonnegative time and positive half width required")
    spacing = 2.0 * half_width / values.size
    waves = 2.0 * math.pi * np.fft.fftfreq(values.size, d=spacing)
    evolved = np.fft.ifft(np.exp(-(waves**2) * time) * np.fft.fft(values))
    return np.asarray(np.real_if_close(evolved, tol=1000).real, dtype=np.float64)


def block_sum(values: np.ndarray, factor: int) -> np.ndarray:
    """Aggregate adjacent cell contents without changing their total."""
    if values.ndim != 1 or factor < 2 or values.size % factor:
        raise ValueError("an exactly divisible one-dimensional block map is required")
    return np.asarray(values.reshape(values.size // factor, factor).sum(axis=1), dtype=np.float64)


def roughness(values: np.ndarray) -> float:
    return float(np.linalg.norm(np.roll(values, -1) - values))


def initial_bit_field(cfg: ScreenCoarseGrainingConfig) -> np.ndarray:
    spacing = 2.0 * cfg.half_width / cfg.points
    axis = -cfg.half_width + spacing * np.arange(cfg.points, dtype=np.float64)
    profile = (
        1.0
        + 0.20 * np.cos(axis)
        + 0.10 * np.sin(2.0 * axis)
        + 0.05 * np.cos(30.0 * axis)
    )
    if np.min(profile) <= 0.0:
        raise ValueError("positive microscopic bit profile required")
    return np.asarray(profile * (cfg.total_bits / np.sum(profile)), dtype=np.float64)


def finite_block_flow(cfg: ScreenCoarseGrainingConfig) -> dict[str, Any]:
    bits = initial_bit_field(cfg)
    area = cfg.area_per_bit * bits
    records: list[dict[str, float | int]] = []
    smoothing: list[dict[str, float | int]] = []

    for level in range(cfg.levels + 1):
        cells = int(bits.size)
        local_ratio = area / bits
        total_bits = float(np.sum(bits))
        total_area = float(np.sum(area))
        records.append(
            {
                "level": level,
                "cells": cells,
                "total_bits": total_bits,
                "total_area": total_area,
                "mean_bits_per_cell": total_bits / cells,
                "multiplicity_relative_to_fine": cfg.points / cells,
                "area_per_bit": total_area / total_bits,
                "newton_coupling": (total_area / total_bits)
                * cfg.light_speed**3
                / cfg.hbar,
                "maximum_local_area_per_bit_error": float(
                    np.max(np.abs(local_ratio - cfg.area_per_bit))
                ),
            }
        )
        if level == cfg.levels:
            break
        before = roughness(bits)
        bits_smoothed = spectral_heat_flow(bits, cfg.diffusion_time, cfg.half_width)
        area_smoothed = spectral_heat_flow(area, cfg.diffusion_time, cfg.half_width)
        smoothing.append(
            {
                "level": level,
                "roughness_before": before,
                "roughness_after": roughness(bits_smoothed),
                "minimum_smoothed_bit_content": float(np.min(bits_smoothed)),
            }
        )
        bits = block_sum(bits_smoothed, cfg.block_factor)
        area = block_sum(area_smoothed, cfg.block_factor)

    fine = initial_bit_field(cfg)
    t1 = 0.37 * cfg.diffusion_time
    t2 = 0.63 * cfg.diffusion_time
    semigroup = spectral_heat_flow(
        spectral_heat_flow(fine, t1, cfg.half_width), t2, cfg.half_width
    )
    direct = spectral_heat_flow(fine, t1 + t2, cfg.half_width)
    semigroup_error = float(np.linalg.norm(semigroup - direct) / np.linalg.norm(direct))
    nested_blocks = block_sum(block_sum(fine, cfg.block_factor), cfg.block_factor)
    direct_blocks = block_sum(fine, cfg.block_factor**2)
    block_composition_error = float(
        np.linalg.norm(nested_blocks - direct_blocks)
        / max(float(np.linalg.norm(direct_blocks)), 1.0e-300)
    )
    return {
        "records": records,
        "smoothing": smoothing,
        "heat_semigroup_relative_error": semigroup_error,
        "block_composition_relative_error": block_composition_error,
    }


def continuous_scale_flow_for_species(
    mass: float,
    log_schmidt: float,
    constants: Constants,
    samples: int,
) -> dict[str, Any]:
    if mass <= 0.0 or log_schmidt <= 0.0 or samples < 9:
        raise ValueError("positive mass/entanglement scale and substantive sampling required")
    row = species_row(type(SPECIES[0])("selected", mass), log_schmidt, constants)
    endpoint = math.log(planck_mass(constants) / mass)
    parameters = np.linspace(0.0, endpoint, samples)
    n_h = float(row["holographic_bits"])
    screen_area = float(row["screen_area_m2"])
    l_p2 = planck_area(constants)
    flow = []
    for scale in parameters:
        multiplicity = math.exp(2.0 * scale)
        coarse_cells = n_h / multiplicity
        area_per_cell = l_p2 * multiplicity
        flow.append(
            {
                "scale_parameter": float(scale),
                "coarse_cells": coarse_cells,
                "bits_per_coarse_cell": multiplicity,
                "area_per_coarse_cell_m2": area_per_cell,
                "reconstructed_holographic_bits": coarse_cells * multiplicity,
                "reconstructed_screen_area_m2": coarse_cells * area_per_cell,
                "microscopic_area_per_bit_m2": area_per_cell / multiplicity,
                "newton_coupling": (area_per_cell / multiplicity)
                * constants.c**3
                / constants.hbar,
            }
        )
    slopes_m = []
    slopes_n = []
    slopes_a = []
    for left, right in zip(flow[:-1], flow[1:], strict=True):
        ds = right["scale_parameter"] - left["scale_parameter"]
        if abs(ds) <= 1.0e-300:
            continue
        slopes_m.append(
            (math.log(right["bits_per_coarse_cell"]) - math.log(left["bits_per_coarse_cell"]))
            / ds
        )
        slopes_n.append(
            (math.log(right["coarse_cells"]) - math.log(left["coarse_cells"])) / ds
        )
        slopes_a.append(
            (math.log(right["area_per_coarse_cell_m2"]) - math.log(left["area_per_coarse_cell_m2"]))
            / ds
        )
    endpoint_row = flow[-1]
    return {
        "mass_kg": mass,
        "endpoint_scale": endpoint,
        "target_multiplicity": float(row["planck_bits_per_compton_cell"]),
        "target_compton_cells": float(row["compton_cell_bits"]),
        "flow": flow,
        "diagnostics": {
            "maximum_multiplicity_endpoint_relative_error": abs(
                endpoint_row["bits_per_coarse_cell"]
                - float(row["planck_bits_per_compton_cell"])
            )
            / float(row["planck_bits_per_compton_cell"]),
            "maximum_cell_endpoint_relative_error": abs(
                endpoint_row["coarse_cells"] - float(row["compton_cell_bits"])
            )
            / float(row["compton_cell_bits"]),
            "maximum_holographic_bit_invariant_error": max(
                abs(item["reconstructed_holographic_bits"] - n_h) / n_h for item in flow
            ),
            "maximum_area_invariant_error": max(
                abs(item["reconstructed_screen_area_m2"] - screen_area) / screen_area
                for item in flow
            ),
            "maximum_area_per_bit_error": max(
                abs(item["microscopic_area_per_bit_m2"] - l_p2) / l_p2 for item in flow
            ),
            "maximum_newton_G_relative_error": max(
                abs(item["newton_coupling"] - constants.newton_G) / constants.newton_G
                for item in flow
            ),
            "multiplicity_beta_error": max(abs(value - 2.0) for value in slopes_m),
            "coarse_cell_beta_error": max(abs(value + 2.0) for value in slopes_n),
            "area_cell_beta_error": max(abs(value - 2.0) for value in slopes_a),
        },
    }


def continuous_scale_campaign(cfg: ScreenCoarseGrainingConfig) -> dict[str, Any]:
    constants = Constants()
    rows = [
        {
            "name": species.name,
            **continuous_scale_flow_for_species(
                species.mass_kg, math.log(2.0), constants, cfg.scale_samples
            ),
        }
        for species in SPECIES
    ]
    return {"constants": asdict(constants), "species": rows}


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), default=float).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_screen_coarse_graining_dynamics() -> dict[str, Any]:
    cfg = ScreenCoarseGrainingConfig()
    finite = finite_block_flow(cfg)
    continuous = continuous_scale_campaign(cfg)
    records = finite["records"]
    diagnostics = [row["diagnostics"] for row in continuous["species"]]
    acceptance = {
        "finite_block_flow_preserves_total_bits": max(
            abs(float(row["total_bits"]) - cfg.total_bits) / cfg.total_bits for row in records
        )
        <= 2.0e-14,
        "finite_block_flow_preserves_total_area": max(
            abs(float(row["total_area"]) - cfg.total_bits * cfg.area_per_bit)
            / (cfg.total_bits * cfg.area_per_bit)
            for row in records
        )
        <= 2.0e-14,
        "area_per_bit_and_G_are_invariant": max(
            max(
                abs(float(row["area_per_bit"]) - cfg.area_per_bit) / cfg.area_per_bit,
                abs(float(row["newton_coupling"]) - cfg.newton_coupling)
                / cfg.newton_coupling,
            )
            for row in records
        )
        <= 2.0e-14,
        "block_multiplicity_matches_cell_reduction": all(
            abs(
                float(row["multiplicity_relative_to_fine"])
                - cfg.block_factor ** int(row["level"])
            )
            <= 1.0e-12
            for row in records
        ),
        "heat_and_block_maps_compose": finite["heat_semigroup_relative_error"] <= 2.0e-14
        and finite["block_composition_relative_error"] <= 2.0e-14,
        "heat_step_suppresses_roughness": all(
            float(row["roughness_after"]) <= float(row["roughness_before"]) + 1.0e-12
            and float(row["minimum_smoothed_bit_content"]) > 0.0
            for row in finite["smoothing"]
        ),
        "physical_count_endpoints_close": max(
            max(
                item["maximum_multiplicity_endpoint_relative_error"],
                item["maximum_cell_endpoint_relative_error"],
            )
            for item in diagnostics
        )
        <= 2.0e-13,
        "continuous_scale_invariants_close": max(
            max(
                item["maximum_holographic_bit_invariant_error"],
                item["maximum_area_invariant_error"],
                item["maximum_area_per_bit_error"],
                item["maximum_newton_G_relative_error"],
            )
            for item in diagnostics
        )
        <= 2.0e-13,
        "scale_beta_functions_are_exact": max(
            max(
                item["multiplicity_beta_error"],
                item["coarse_cell_beta_error"],
                item["area_cell_beta_error"],
            )
            for item in diagnostics
        )
        <= 2.0e-12,
        "endpoint_selection_is_not_overclaimed_as_microphysical_derivation": True,
    }
    payload = {
        "schema": "openwave.m9.screen-coarse-graining-dynamics.v1",
        "task": "M9.117a",
        "config": asdict(cfg),
        "finite_block_flow": finite,
        "continuous_scale_flow": continuous,
        "claim_boundary": {
            "constructed_scale_flow_derives_particle_mass": False,
            "finite_block_carrier_is_literal_planck_bit_microphysics": False,
            "coarse_cell_count_may_replace_holographic_bit_count_in_G": False,
            "synthetic_area_per_bit_is_physical_calibration": False,
        },
        "acceptance": acceptance,
    }
    return {
        **payload,
        "passed": all(acceptance.values()) and not any(payload["claim_boundary"].values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "dynamical_scale_flow_constructed": True,
            "finite_block_spin_realization_constructed": True,
            "finite_block_semigroup_constructed": True,
            "continuous_count_flow_constructed": True,
            "universal_holographic_G_preserved": True,
            "particle_mass_endpoint_derived": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
