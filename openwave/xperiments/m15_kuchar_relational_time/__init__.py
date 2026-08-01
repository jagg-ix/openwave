"""M15 CAT/EPT Kuchař relational-time consistency lineage."""
from .kuchar_relational_time_m151 import (
    KucharRelationalTimeConfig,
    run_kuchar_relational_time_study,
)
from .kuchar_bcj_pointwise_coverage_m152 import (
    KucharBCJPointwiseConfig,
    run_kuchar_bcj_pointwise_coverage_study,
)
from .kuchar_continuum_bcj_causal_m153 import (
    KucharContinuumBCJConfig,
    run_kuchar_continuum_bcj_causal_study,
)
from .kuchar_full_ads_double_copy_m154 import (
    KucharFullAdSDoubleCopyConfig,
    run_kuchar_full_ads_double_copy_study,
)
from .conditioned_four_clock_dynamics_m155 import (
    ConditionedFourClockConfig,
    run_conditioned_four_clock_study,
)
from .functorial_conditioning_m156 import (
    FunctorialConditioningConfig,
    run_functorial_conditioning_study,
)
from .entropic_clock_synthesis_m157 import (
    EntropicClockSynthesisConfig,
    run_entropic_clock_synthesis_study,
)
run_m15_model_study = run_entropic_clock_synthesis_study
__all__ = [
    "KucharRelationalTimeConfig",
    "KucharBCJPointwiseConfig",
    "KucharContinuumBCJConfig",
    "KucharFullAdSDoubleCopyConfig",
    "ConditionedFourClockConfig",
    "FunctorialConditioningConfig",
    "EntropicClockSynthesisConfig",
    "run_kuchar_relational_time_study",
    "run_kuchar_bcj_pointwise_coverage_study",
    "run_kuchar_continuum_bcj_causal_study",
    "run_kuchar_full_ads_double_copy_study",
    "run_conditioned_four_clock_study",
    "run_functorial_conditioning_study",
    "run_entropic_clock_synthesis_study",
    "run_m15_model_study",
]
