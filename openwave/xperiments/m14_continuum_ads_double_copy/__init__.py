"""M14 CAT/EPT continuum AdS double-copy lineage."""
from .causal_green_hadamard_m141 import CausalGreenHadamardConfig, run_causal_green_hadamard_study
from .infinite_bcj_direct_limit_m142 import InfiniteBCJDirectLimitConfig, run_infinite_bcj_direct_limit_study
run_m14_model_study=run_infinite_bcj_direct_limit_study
__all__=["CausalGreenHadamardConfig","InfiniteBCJDirectLimitConfig","run_causal_green_hadamard_study","run_infinite_bcj_direct_limit_study","run_m14_model_study"]
