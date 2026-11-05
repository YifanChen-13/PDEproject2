"""Guard D's error measurements against mismatched grids and norm weights."""
import numpy as np
import pytest
from stage2_studies import nested_sample, norms


def test_nested_comparison_is_exact_without_interpolation():
    fine = np.arange(0., 4.125, .125)
    coarse = np.arange(0., 3.5, .5)
    np.testing.assert_array_equal(nested_sample(coarse, fine, fine**2), coarse**2)


@pytest.mark.parametrize('grid', [np.array([0., .3, .6]),
                                 np.array([0., .5, 1.5])])
def test_noncoincident_or_out_of_domain_nodes_are_rejected(grid):
    fine = np.arange(0., 1.125, .125)
    with pytest.raises(ValueError, match='nested'):
        nested_sample(grid, fine, fine**2)


def test_l2_is_integral_norm_not_rms_and_endpoints_have_half_weight():
    s = np.array([0., 1., 2.])
    assert norms(s, np.ones(3))['L2'] == pytest.approx(np.sqrt(2))
    assert norms(s, np.array([1., 0., 1.]))['L2'] == pytest.approx(1.)
    assert norms(s, np.array([1., -2., 1.]))['Linf'] == 2.
