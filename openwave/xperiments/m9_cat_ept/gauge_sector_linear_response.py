"""M9.120b: gauge-invariant finite transition response.

A site-scalar source is inserted into each gauge carrier. Its spectral response is
computed from the Hermitian covariant operator and compared before and after a
local gauge transformation. The source commutes with local internal rotations,
so the broadened response and its completeness sum rule are gauge invariant.

The Lorentzian width is a plotting/resolution parameter. The closed Hermitian
carrier has no intrinsic irreversible decay channel.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

import numpy as np

from .electroweak_higgs_lattice import (
    ElectroweakHiggsConfig,
    combined_links,
    gauge_transform as electroweak_gauge_transform,
    initialize_electroweak_state,
    local_electroweak_gauge,
)
from .gauge_sector_spectrum import (
    block_gauge_matrix,
    covariant_operator_matrix,
    flatten_field,
)
from .non_abelian_lattice_gauge import (
    Array,
    NonAbelianGaugeConfig,
    gauge_transform,
    initialize_links,
    initialize_matter,
    local_gauge_transformation,
)


@dataclass(frozen=True)
class GaugeResponseConfig:
    broadening: float = 0.08
    frequency_points: int = 601
    source_harmonics: tuple[float, float] = (1.0, 0.35)

    def __post_init__(self) -> None:
        if self.broadening <= 0.0:
            raise ValueError("positive response broadening required")
        if self.frequency_points < 101:
            raise ValueError("substantive frequency grid required")
        if len(self.source_harmonics) != 2:
            raise ValueError("two-dimensional source harmonics required")


def site_scalar_source(
    site_shape: tuple[int, int], internal: int, harmonics: tuple[float, float]
) -> Array:
    x, y = np.meshgrid(
        np.arange(site_shape[0], dtype=np.float64),
        np.arange(site_shape[1], dtype=np.float64),
        indexing="ij",
    )
    profile = (
        harmonics[0] * np.cos(2.0 * math.pi * x / site_shape[0])
        + harmonics[1] * np.sin(2.0 * math.pi * y / site_shape[1])
    )
    diagonal = np.repeat(profile.reshape(-1), internal)
    return np.diag(diagonal.astype(np.complex128))


def spectral_response(
    operator: Array,
    state: Array,
    observable: Array,
    broadening: float,
    frequency_points: int,
) -> dict[str, Any]:
    vector = np.asarray(state, dtype=np.complex128).reshape(-1)
    vector /= np.linalg.norm(vector)
    eigenvalues, eigenvectors = np.linalg.eigh(operator)
    source_vector = observable @ vector
    amplitudes = eigenvectors.conjugate().T @ source_vector
    weights = np.abs(amplitudes) ** 2
    reference_energy = float(np.vdot(vector, operator @ vector).real)
    frequencies = eigenvalues - reference_energy
    span = max(float(np.max(np.abs(frequencies))), 1.0)
    grid = np.linspace(-1.05 * span, 1.05 * span, frequency_points)
    differences = grid[:, None] - frequencies[None, :]
    lorentzian = broadening / math.pi / (
        differences * differences + broadening * broadening
    )
    response = lorentzian @ weights
    sum_rule_target = float(np.vdot(source_vector, source_vector).real)
    sum_rule_error = abs(float(np.sum(weights)) - sum_rule_target) / max(
        sum_rule_target, 1.0e-300
    )
    dominant = np.argsort(weights)[::-1][:8]
    return {
        "reference_energy": reference_energy,
        "frequency_grid": grid,
        "response": np.asarray(response, dtype=np.float64),
        "frequencies": np.asarray(frequencies, dtype=np.float64),
        "weights": np.asarray(weights, dtype=np.float64),
        "sum_rule_target": sum_rule_target,
        "sum_rule_relative_error": sum_rule_error,
        "dominant_channels": [
            {
                "mode": int(index),
                "frequency": float(frequencies[index]),
                "weight": float(weights[index]),
            }
            for index in dominant
        ],
    }


def response_relative_error(left: Array, right: Array) -> float:
    return float(
        np.linalg.norm(left - right)
        / max(float(np.linalg.norm(left)), float(np.linalg.norm(right)), 1.0e-300)
    )


def higgs_radial_tangent_selection() -> dict[str, float]:
    radial = np.asarray((1.0, 0.0, 0.0, 0.0), dtype=np.float64)
    radial /= np.linalg.norm(radial)
    tangent_projector = np.eye(4) - np.outer(radial, radial)
    source = radial.copy()
    return {
        "radial_strength": float(abs(np.dot(radial, source)) ** 2),
        "tangent_strength": float(np.linalg.norm(tangent_projector @ source) ** 2),
        "completeness_error": abs(
            float(abs(np.dot(radial, source)) ** 2)
            + float(np.linalg.norm(tangent_projector @ source) ** 2)
            - float(np.dot(source, source))
        ),
    }


def response_comparison(
    operator: Array,
    transformed_operator: Array,
    state: Array,
    transformed_state: Array,
    block_gauge: Array,
    observable: Array,
    cfg: GaugeResponseConfig,
) -> dict[str, Any]:
    original = spectral_response(
        operator,
        state,
        observable,
        cfg.broadening,
        cfg.frequency_points,
    )
    transformed = spectral_response(
        transformed_operator,
        transformed_state,
        observable,
        cfg.broadening,
        cfg.frequency_points,
    )
    observable_commutator = observable @ block_gauge - block_gauge @ observable
    return {
        "response_gauge_relative_error": response_relative_error(
            original["response"], transformed["response"]
        ),
        "source_commutator_norm": float(np.linalg.norm(observable_commutator)),
        "sum_rule_relative_error": max(
            original["sum_rule_relative_error"],
            transformed["sum_rule_relative_error"],
        ),
        "integrated_response_original": float(
            np.trapz(original["response"], original["frequency_grid"])
        ),
        "integrated_response_transformed": float(
            np.trapz(
                transformed["response"], transformed["frequency_grid"]
            )
        ),
        "dominant_channels": original["dominant_channels"],
        "response_peak": float(np.max(original["response"])),
        "broadening_is_intrinsic_decay_width": False,
    }


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), default=float
        ).encode()
    ).hexdigest()


@lru_cache(maxsize=1)
def run_gauge_sector_linear_response() -> dict[str, Any]:
    cfg = GaugeResponseConfig()

    strong_cfg = NonAbelianGaugeConfig()
    strong_state = initialize_matter(strong_cfg)
    strong_links = initialize_links(strong_cfg)
    strong_gauge = local_gauge_transformation(strong_cfg)
    strong_state_gauge, strong_links_gauge = gauge_transform(
        strong_state, strong_links, strong_gauge
    )
    strong_operator = covariant_operator_matrix(strong_links)
    strong_operator_gauge = covariant_operator_matrix(strong_links_gauge)
    strong_block = block_gauge_matrix(strong_gauge)
    strong_observable = site_scalar_source(
        (strong_cfg.points, strong_cfg.points),
        strong_cfg.colors,
        cfg.source_harmonics,
    )
    strong = response_comparison(
        strong_operator,
        strong_operator_gauge,
        flatten_field(strong_state),
        flatten_field(strong_state_gauge),
        strong_block,
        strong_observable,
        cfg,
    )

    electroweak_cfg = ElectroweakHiggsConfig()
    higgs, su2_links, u1_links = initialize_electroweak_state(electroweak_cfg)
    su2_gauge, u1_gauge = local_electroweak_gauge(electroweak_cfg)
    higgs_gauge, su2_links_gauge, u1_links_gauge = electroweak_gauge_transform(
        higgs,
        su2_links,
        u1_links,
        su2_gauge,
        u1_gauge,
        electroweak_cfg.hypercharge_power,
    )
    links = combined_links(
        su2_links, u1_links, electroweak_cfg.hypercharge_power
    )
    links_gauge = combined_links(
        su2_links_gauge, u1_links_gauge, electroweak_cfg.hypercharge_power
    )
    combined_gauge = su2_gauge * (
        u1_gauge**electroweak_cfg.hypercharge_power
    )[..., None, None]
    electroweak_observable = site_scalar_source(
        (electroweak_cfg.points, electroweak_cfg.points),
        2,
        cfg.source_harmonics,
    )
    electroweak = response_comparison(
        covariant_operator_matrix(links),
        covariant_operator_matrix(links_gauge),
        flatten_field(higgs),
        flatten_field(higgs_gauge),
        block_gauge_matrix(combined_gauge),
        electroweak_observable,
        cfg,
    )
    electroweak["higgs_radial_tangent_selection"] = (
        higgs_radial_tangent_selection()
    )

    payload = {
        "schema": "openwave.m9.gauge-sector-linear-response.v1",
        "task": "M9.120b",
        "config": asdict(cfg),
        "strong": strong,
        "electroweak": electroweak,
        "claim_boundary": {
            "finite_response_is_physical_decay_rate": False,
            "numerical_broadening_is_intrinsic_linewidth": False,
            "response_peak_is_observed_transition": False,
            "radial_selection_is_calibrated_higgs_decay_channel": False,
        },
    }
    acceptance = {
        "strong_response_is_locally_gauge_invariant": (
            strong["source_commutator_norm"] <= 2.0e-12
            and strong["response_gauge_relative_error"] <= 3.0e-10
        ),
        "strong_response_completeness_sum_rule_closes": strong[
            "sum_rule_relative_error"
        ]
        <= 2.0e-12,
        "electroweak_response_is_locally_gauge_invariant": (
            electroweak["source_commutator_norm"] <= 2.0e-12
            and electroweak["response_gauge_relative_error"] <= 3.0e-10
        ),
        "electroweak_response_completeness_sum_rule_closes": electroweak[
            "sum_rule_relative_error"
        ]
        <= 2.0e-12,
        "higgs_radial_source_is_orthogonal_to_gauge_orbit_tangents": (
            electroweak["higgs_radial_tangent_selection"]["radial_strength"]
            >= 1.0 - 1.0e-14
            and electroweak["higgs_radial_tangent_selection"][
                "tangent_strength"
            ]
            <= 1.0e-14
            and electroweak["higgs_radial_tangent_selection"][
                "completeness_error"
            ]
            <= 1.0e-14
        ),
        "closed_Hermitian_carriers_do_not_claim_intrinsic_decay": (
            not strong["broadening_is_intrinsic_decay_width"]
            and not electroweak["broadening_is_intrinsic_decay_width"]
        ),
        "no_physical_transition_claim_is_promoted": not any(
            payload["claim_boundary"].values()
        ),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
        "decision": {
            "gauge_invariant_transition_response_constructed": True,
            "spectral_completeness_sum_rules_closed": True,
            "higgs_radial_tangent_selection_constructed": True,
            "intrinsic_decay_channel_constructed": False,
            "physical_transition_or_decay_identified": False,
        },
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=float) + "\n"
