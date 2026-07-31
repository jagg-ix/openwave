"""M14.6 continuum-kernel BCJ registration."""
from .continuum_kernel_double_copy_m146 import ContinuumKernelDoubleCopyConfig, run_continuum_kernel_double_copy_study
run_model_study = run_continuum_kernel_double_copy_study
__all__ = ["ContinuumKernelDoubleCopyConfig", "run_continuum_kernel_double_copy_study", "run_model_study"]
