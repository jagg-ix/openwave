from openwave.xperiments.m9_cat_ept.coefficient_self_consistency import result_to_json, run_coefficient_self_consistency

if __name__ == "__main__":
    print(result_to_json(run_coefficient_self_consistency()), end="")
