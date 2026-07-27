from openwave.xperiments.m9_cat_ept.platform_integration_contract import (
    result_to_json,
    run_platform_integration_contract,
)

print(result_to_json(run_platform_integration_contract()), end="")
