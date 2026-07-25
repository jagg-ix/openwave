from openwave.xperiments.m9_cat_ept.zil_runtime_upgrade import result_to_json
from openwave.xperiments.m9_cat_ept.zil_runtime_upgrade_current import (
    run_zil_runtime_upgrade,
)


if __name__ == "__main__":
    print(result_to_json(run_zil_runtime_upgrade()), end="")
