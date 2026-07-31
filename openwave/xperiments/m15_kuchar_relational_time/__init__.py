"""M15 CAT/EPT Kuchař relational-time consistency lineage."""
from .kuchar_relational_time_m151 import (
    KucharRelationalTimeConfig,
    run_kuchar_relational_time_study,
)
from .kuchar_bcj_pointwise_coverage_m152 import (
    KucharBCJPointwiseConfig,
    run_kuchar_bcj_pointwise_coverage_study,
)
run_m15_model_study = run_kuchar_bcj_pointwise_coverage_study
__all__ = [
    "KucharRelationalTimeConfig", "KucharBCJPointwiseConfig",
    "run_kuchar_relational_time_study", "run_kuchar_bcj_pointwise_coverage_study",
    "run_m15_model_study",
]
