from openwave.xperiments.m9_cat_ept.global_inference_statistics_emwave_m137 import (
    PHYSLIB_TIP,
    SOURCE_RECORDS,
    antisymmetrize,
    gaussian_score,
    harmonic_electric_component,
    run_m137_global_authority,
)


def test_m137_global_authority_passes_without_promoting_physics() -> None:
    report = run_m137_global_authority()
    assert report.passed
    assert report.physlib["tip"] == PHYSLIB_TIP
    assert {record["id"] for record in report.source_records} == {
        "cramer-rao-inference-precision",
        "pauli-exchange-exclusion",
        "harmonic-maxwell-plane-wave",
    }
    assert len(SOURCE_RECORDS) == 3
    assert report.acceptance["physical_promotion_remains_blocked"]
    assert "physical mass equals inference precision remains a bridge postulate" in report.boundaries


def test_m137_scalar_guards_and_algebra() -> None:
    try:
        gaussian_score(0.0, 0.0, 0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("nonpositive Gaussian variance must fail")

    amplitude = lambda a, b: complex(len(a), len(b))
    assert antisymmetrize(amplitude, "same", "same") == 0j

    try:
        harmonic_electric_component(1.0, 0.0, 1.0, 0.0, 0.0, 0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero wave number must fail")


def test_m137_fingerprint_is_deterministic() -> None:
    first = run_m137_global_authority()
    second = run_m137_global_authority()
    assert first.fingerprint() == second.fingerprint()
