from openwave.xperiments.m9_cat_ept.cubic_quintic_continuum import result_to_json, run_cubic_quintic_continuum_study

if __name__ == "__main__":
    print(result_to_json(run_cubic_quintic_continuum_study()), end="")
