"""M9.110d: nonlinear conformal-ADM configuration driven by one screen G."""
from __future__ import annotations

from dataclasses import dataclass
import math

from .electrogravitic_weak_field_evolution import ElectrograviticEvolutionConfig
from .nonlinear_constraint_gravity import NonlinearMetricConfig


@dataclass(frozen=True)
class ScreenCoupledNonlinearMetricConfig(NonlinearMetricConfig):
    """Nonlinear metric config whose matter layer uses an explicit screen coupling.

    The historical carrier parameterizes G through ``G = hbar*c*sigma0^4``.
    This adapter inverts that map only after a screen anchor has supplied G.
    """

    screen_newton_coupling: float = 1.0
    hbar: float = 1.0
    light_speed: float = 1.0

    def __post_init__(self) -> None:
        super().__post_init__()
        if min(self.screen_newton_coupling, self.hbar, self.light_speed) <= 0.0:
            raise ValueError("positive screen coupling and unit controls required")

    @property
    def screen_inference_width(self) -> float:
        return math.pow(
            self.screen_newton_coupling / (self.hbar * self.light_speed), 0.25
        )

    def matter_config(self) -> ElectrograviticEvolutionConfig:
        return ElectrograviticEvolutionConfig(
            points=self.points,
            half_width=self.half_width,
            hbar=self.hbar,
            light_speed=self.light_speed,
            inference_width=self.screen_inference_width,
            time_step=min(self.time_step, 2.0e-5),
            steps=20,
            sample_stride=10,
        )

    def coupling_contract(self) -> dict[str, float | bool]:
        realized = self.matter_config().newton_coupling
        relative_error = abs(realized - self.screen_newton_coupling) / max(
            abs(self.screen_newton_coupling), 1.0e-300
        )
        return {
            "screen_newton_coupling": self.screen_newton_coupling,
            "derived_inference_width": self.screen_inference_width,
            "matter_newton_coupling": realized,
            "relative_error": relative_error,
            "screen_coupling_is_injected": relative_error <= 5.0e-15,
        }
