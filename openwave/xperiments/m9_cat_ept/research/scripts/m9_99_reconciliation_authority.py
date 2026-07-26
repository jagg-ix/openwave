from openwave.xperiments.m9_cat_ept.formal_numerical_reconciliation_authority import (
    result_to_json,
    run_formal_numerical_reconciliation_authority,
)


if __name__ == "__main__":
    print(result_to_json(run_formal_numerical_reconciliation_authority()), end="")
