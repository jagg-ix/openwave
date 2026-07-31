"""Canonical M15 registration."""
from .kuchar_full_ads_double_copy_m154 import (
    KucharFullAdSDoubleCopyConfig,
    run_kuchar_full_ads_double_copy_study,
)
run_model_study = run_kuchar_full_ads_double_copy_study
__all__ = [
    "KucharFullAdSDoubleCopyConfig",
    "run_kuchar_full_ads_double_copy_study",
    "run_model_study",
]
