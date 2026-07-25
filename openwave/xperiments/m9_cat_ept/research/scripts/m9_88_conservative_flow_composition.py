from openwave.xperiments.m9_cat_ept.conservative_flow_composition import result_to_json, run_conservative_flow_composition


if __name__ == "__main__":
    print(result_to_json(run_conservative_flow_composition()), end="")
