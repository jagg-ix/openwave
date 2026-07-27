import numpy as np

from openwave.xperiments.m9_cat_ept.gauge_sector_spectrum import (
    block_gauge_matrix,
    covariant_operator_matrix,
    higgs_local_hessian,
    run_gauge_sector_spectrum,
)
from openwave.xperiments.m9_cat_ept.non_abelian_lattice_gauge import (
    NonAbelianGaugeConfig,
    gauge_transform,
    initialize_links,
    initialize_matter,
    local_gauge_transformation,
)
from openwave.xperiments.m9_cat_ept.electroweak_higgs_lattice import (
    ElectroweakHiggsConfig,
)


def test_local_su3_transform_is_block_unitary_similarity() -> None:
    cfg = NonAbelianGaugeConfig(points=5, steps=1)
    matter = initialize_matter(cfg)
    links = initialize_links(cfg)
    gauge = local_gauge_transformation(cfg)
    _, transformed_links = gauge_transform(matter, links, gauge)

    operator = covariant_operator_matrix(links)
    transformed_operator = covariant_operator_matrix(transformed_links)
    block = block_gauge_matrix(gauge)
    expected = block @ operator @ block.conjugate().T

    assert np.linalg.norm(transformed_operator - expected) / np.linalg.norm(expected) <= 3.0e-12
    assert np.max(
        np.abs(np.linalg.eigvalsh(operator) - np.linalg.eigvalsh(transformed_operator))
    ) <= 3.0e-11


def test_quartic_higgs_hessian_has_three_tangents_and_one_radial_mode() -> None:
    cfg = ElectroweakHiggsConfig()
    values = np.linalg.eigvalsh(higgs_local_hessian(cfg))

    assert np.allclose(values[:3], 0.0, atol=1.0e-14)
    assert np.isclose(values[3], 4.0 * cfg.mu_squared, atol=1.0e-14)


def test_gauge_sector_spectrum_campaign_passes_without_mass_promotion() -> None:
    result = run_gauge_sector_spectrum()

    assert result["passed"]
    assert all(result["acceptance"].values())
    assert result["decision"]["gauge_invariant_finite_spectra_constructed"]
    assert not result["decision"]["physical_particle_spectrum_predicted"]
    assert not result["decision"]["physical_mass_calibration_complete"]
    assert not any(result["claim_boundary"].values())
