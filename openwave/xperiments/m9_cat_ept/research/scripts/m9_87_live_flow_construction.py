from openwave.xperiments.m9_cat_ept.live_flow_construction import result_to_json, run_live_flow_construction


if __name__ == "__main__":
    print(result_to_json(run_live_flow_construction()), end="")
