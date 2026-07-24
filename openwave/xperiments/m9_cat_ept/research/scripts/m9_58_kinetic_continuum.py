"""Run M9.58 kinetic-continuum bridge."""
from openwave.xperiments.m9_cat_ept.kinetic_continuum_bridge import result_to_json,run_kinetic_continuum_study

def main()->int:
    result=run_kinetic_continuum_study(); print(result_to_json(result),end=""); return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
