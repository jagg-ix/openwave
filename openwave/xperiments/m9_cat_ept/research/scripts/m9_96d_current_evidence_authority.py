from openwave.xperiments.m9_cat_ept.current_evidence_authority import (
    result_to_json,
    run_current_evidence_authority,
)


if __name__ == "__main__":
    print(result_to_json(run_current_evidence_authority()), end="")
