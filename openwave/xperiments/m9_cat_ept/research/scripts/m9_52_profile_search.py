"""Execute the M9.52 profile-family localization study."""
from openwave.xperiments.m9_cat_ept.non_gaussian_self_binding import result_to_json, run_profile_self_binding_search

def main() -> int:
    result = run_profile_self_binding_search()
    print(result_to_json(result), end="")
    return 0 if result["passed"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
