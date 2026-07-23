"""Run M9.29 spin and magnetic observables."""
from openwave.xperiments.m9_cat_ept.spin_magnetic_observables import result_to_json, run_spin_magnetic_study

def main()->int:
    result=run_spin_magnetic_study(); print(result_to_json(result),end=""); return 0 if result["passed"] else 1
if __name__=="__main__": raise SystemExit(main())
