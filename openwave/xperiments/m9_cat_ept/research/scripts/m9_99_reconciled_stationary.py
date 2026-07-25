from openwave.xperiments.m9_cat_ept.reconciled_gauge_spinor_stationary_current import (
    result_to_json,
    run_reconciled_gauge_spinor_campaign,
)


if __name__ == "__main__":
    print(result_to_json(run_reconciled_gauge_spinor_campaign()), end="")
