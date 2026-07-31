"""M15 CAT/EPT Kuchař relational-time consistency lineage."""
from .kuchar_relational_time_m151 import (
    KucharRelationalTimeConfig,
    run_kuchar_relational_time_study,
)
run_m15_model_study = run_kuchar_relational_time_study
__all__ = [
    "KucharRelationalTimeConfig",
    "run_kuchar_relational_time_study",
    "run_m15_model_study",
]
