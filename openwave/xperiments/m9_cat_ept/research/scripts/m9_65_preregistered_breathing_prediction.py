from openwave.xperiments.m9_cat_ept.preregistered_breathing_prediction import result_to_json, run_preregistered_breathing_prediction

if __name__ == "__main__":
    print(result_to_json(run_preregistered_breathing_prediction()), end="")
