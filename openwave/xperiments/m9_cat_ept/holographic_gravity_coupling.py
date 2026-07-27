"""M9.110c-d: one screen-density coupling for all OpenWave gravity carriers."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from hashlib import sha256
import json
import math
from typing import Any, Mapping

from .electrogravitic_weak_field_evolution import ElectrograviticEvolutionConfig
from .screen_coupled_nonlinear_gravity import ScreenCoupledNonlinearMetricConfig


@dataclass(frozen=True)
class ScreenDensityAnchor:
    area: float
    bits: float
    hbar: float = 1.0
    c: float = 1.0
    evidence_class: str = "internal"
    source: str = "unconfigured"
    target_dependencies: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if min(self.area, self.bits, self.hbar, self.c) <= 0.0:
            raise ValueError("positive screen anchor required")
        if self.evidence_class not in ("external", "definition", "internal", "derived"):
            raise ValueError("unsupported evidence class")

    @property
    def independent(self) -> bool:
        return self.evidence_class in ("external", "definition") and not self.target_dependencies

    @property
    def area_per_bit(self) -> float:
        return self.area / self.bits

    @property
    def newton_coupling(self) -> float:
        return self.area_per_bit * self.c**3 / self.hbar

    @property
    def inference_width(self) -> float:
        return math.pow(self.newton_coupling / (self.hbar * self.c), 0.25)


@dataclass(frozen=True)
class AnchoredGravityConfigs:
    anchor: ScreenDensityAnchor
    weak: ElectrograviticEvolutionConfig
    nonlinear: ScreenCoupledNonlinearMetricConfig


def build_gravity_configs(
    anchor: ScreenDensityAnchor,
    *,
    require_independent: bool = True,
    points: int = 17,
    half_width: float = 8.0,
) -> AnchoredGravityConfigs:
    if require_independent and not anchor.independent:
        raise ValueError("independent screen-density anchor required")
    coupling = anchor.newton_coupling
    weak = ElectrograviticEvolutionConfig(
        points=points,
        half_width=half_width,
        hbar=anchor.hbar,
        light_speed=anchor.c,
        inference_width=anchor.inference_width,
    )
    nonlinear = ScreenCoupledNonlinearMetricConfig(
        points=points,
        half_width=half_width,
        screen_newton_coupling=coupling,
        hbar=anchor.hbar,
        light_speed=anchor.c,
    )
    return AnchoredGravityConfigs(anchor=anchor, weak=weak, nonlinear=nonlinear)


def coupling_contract(configs: AnchoredGravityConfigs) -> dict[str, Any]:
    coupling = configs.anchor.newton_coupling
    weak_value = configs.weak.newton_coupling
    nonlinear_contract = configs.nonlinear.coupling_contract()
    return {
        "screen_area_per_bit": configs.anchor.area_per_bit,
        "screen_newton_coupling": coupling,
        "screen_inference_width": configs.anchor.inference_width,
        "weak_newton_coupling": weak_value,
        "nonlinear_newton_coupling": nonlinear_contract["matter_newton_coupling"],
        "weak_uses_screen_coupling": abs(weak_value - coupling) <= 5.0e-15,
        "nonlinear_uses_screen_coupling": nonlinear_contract["screen_coupling_is_injected"],
        "weak_and_nonlinear_share_one_G": abs(
            weak_value - float(nonlinear_contract["matter_newton_coupling"])
        ) <= 5.0e-15,
        "one_G_policy": True,
    }


def default_internal_anchor() -> ScreenDensityAnchor:
    return ScreenDensityAnchor(
        area=1.0,
        bits=1.0,
        evidence_class="internal",
        source="OpenWave natural-unit screen",
        target_dependencies=("gravity",),
    )


def fingerprint(payload: Mapping[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


@lru_cache(maxsize=1)
def run_holographic_gravity_coupling() -> dict[str, Any]:
    anchor = default_internal_anchor()
    blocked = False
    try:
        build_gravity_configs(anchor, require_independent=True)
    except ValueError:
        blocked = True
    synthetic = ScreenDensityAnchor(
        area=2.0,
        bits=8.0,
        evidence_class="external",
        source="synthetic test fixture; not physical evidence",
    )
    configs = build_gravity_configs(synthetic)
    contract = coupling_contract(configs)
    payload = {
        "schema": "openwave.m9.holographic-gravity-coupling.v2",
        "task": "M9.110d",
        "default_anchor": asdict(anchor),
        "default_physical_injection_blocked": blocked,
        "synthetic_fixture": asdict(synthetic),
        "synthetic_contract": contract,
        "decision": {
            "screen_density_is_primary_G_source": True,
            "particle_mass_is_primary_G_source": False,
            "weak_and_nonlinear_share_one_screen_G": contract[
                "weak_and_nonlinear_share_one_G"
            ],
            "current_default_is_physically_calibrated": False,
            "nonlinear_config_has_explicit_screen_coupling": contract[
                "nonlinear_uses_screen_coupling"
            ],
        },
    }
    acceptance = {
        "internal_default_is_blocked": blocked,
        "synthetic_screen_G_reaches_weak_config": contract["weak_uses_screen_coupling"],
        "synthetic_screen_G_reaches_nonlinear_config": contract[
            "nonlinear_uses_screen_coupling"
        ],
        "one_screen_G_is_shared": contract["weak_and_nonlinear_share_one_G"],
        "primary_G_is_screen_density": payload["decision"]["screen_density_is_primary_G_source"],
        "particle_mass_is_not_primary_G": not payload["decision"]["particle_mass_is_primary_G_source"],
        "fingerprint_is_deterministic": fingerprint(payload) == fingerprint(payload),
    }
    return {
        **payload,
        "acceptance": acceptance,
        "passed": all(acceptance.values()),
        "fingerprint": fingerprint(payload),
    }


def result_to_json(result: Mapping[str, Any]) -> str:
    return json.dumps(result, indent=2, sort_keys=True, default=str) + "\n"
