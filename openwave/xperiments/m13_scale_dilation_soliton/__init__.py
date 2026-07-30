"""M13 CAT/EPT scale-dilation and holographic-amplitude model lineage."""

from .model_registration import (
    ScaleDilationSolitonConfig,
    run_scale_dilation_soliton_study,
)
from .holographic_bcj_twistor_wilson_m132 import (
    HolographicAmplitudeConfig,
    run_holographic_amplitude_study,
)

run_m13_model_study = run_holographic_amplitude_study

__all__ = [
    "ScaleDilationSolitonConfig",
    "HolographicAmplitudeConfig",
    "run_scale_dilation_soliton_study",
    "run_holographic_amplitude_study",
    "run_m13_model_study",
]
