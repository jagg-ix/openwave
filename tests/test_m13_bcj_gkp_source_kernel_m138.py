from openwave.xperiments.m13_scale_dilation_soliton.bcj_gkp_source_kernel_m138 import run_bcj_gkp_source_kernel_study
def test_m138():
    result=run_bcj_gkp_source_kernel_study(); assert result["passed"]; assert result["decision"]["ads_double_copy_theorem_not_claimed"]
