"""Canonical M15 registration."""
from .entropic_clock_synthesis_m157 import (
    EntropicClockSynthesisConfig,
    run_entropic_clock_synthesis_study,
)
run_model_study = run_entropic_clock_synthesis_study
__all__ = [
    "EntropicClockSynthesisConfig",
    "run_entropic_clock_synthesis_study",
    "run_model_study",
]
