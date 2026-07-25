from openwave.xperiments.m9_cat_ept.identified_standing_wave_orbit import result_to_json, run_identified_standing_wave_orbit


if __name__ == "__main__":
    print(result_to_json(run_identified_standing_wave_orbit()), end="")
