"""Independent model, hand-row and polynomial checks for A's foundation."""

import numpy as np
import pytest

from discretization import action, assemble
from problem import EXACT_LAMBDA, EXACT_STAR, K, R, dividend, exact, payoff, volatility


def full_stencil(lo, diag, up, full):
    result = action(lo, diag, up, full[1:-1])
    result[0] += lo[0] * full[0]
    result[-1] += up[-1] * full[-1]
    return result


def test_payoff_and_exact_support_scalars_and_integer_arrays():
    np.testing.assert_array_equal(payoff([0, 60, 100, 150]), [100, 40, 0, 0])
    assert float(exact(0)) == 100
    assert float(exact(50)) == 50
    expected_at_100 = (200 / 7) * (7 / 5)**(-2.5)
    assert float(exact(100)) == pytest.approx(expected_at_100)
    assert EXACT_STAR == pytest.approx(500 / 7)


def test_stage1_value_matching_smooth_fit_and_continuation_equation():
    assert float(exact(EXACT_STAR)) == pytest.approx(K - EXACT_STAR)
    derivative = (K - EXACT_STAR) * EXACT_LAMBDA / EXACT_STAR
    assert derivative == pytest.approx(-1)
    x = np.array([80.0, 100.0, 200.0, 400.0])
    value = exact(x)
    first = EXACT_LAMBDA * value / x
    second = EXACT_LAMBDA * (EXACT_LAMBDA - 1) * value / x**2
    residual = 0.5 * 0.20**2 * x**2 * second + 0.05 * x * first - 0.05 * value
    np.testing.assert_allclose(residual, 0, atol=2e-14)


def test_volatility_endpoint_and_integer_input():
    with np.errstate(divide="raise", invalid="raise"):
        np.testing.assert_allclose(volatility([0, 100, 200], 1), 0.20)
        sigma = volatility(np.array([0, 100, 200]), 2)
    assert sigma[0] == pytest.approx(0.13)
    assert sigma[1] == pytest.approx(0.20)
    assert 0.20 < sigma[2] < 0.27
    assert dividend(1) == 0 and dividend(2) == 0.02


@pytest.mark.parametrize("function", [payoff, exact, lambda s: volatility(s, 2)])
@pytest.mark.parametrize("bad", [-1, np.nan, np.inf])
def test_model_rejects_invalid_asset_prices(function, bad):
    with pytest.raises(ValueError):
        function(bad)


@pytest.mark.parametrize("stage,expected", [
    (1, [-200, 405.05, -205]),
    (2, [-200, 403.05, -203]),
])
def test_independently_derived_row_at_strike(stage, expected):
    s, lo, diag, up, _, _ = assemble(200.0, 1.0, stage)
    k = int(np.flatnonzero(s[1:-1] == 100)[0])
    np.testing.assert_allclose([lo[k], diag[k], up[k]], expected, atol=1e-11)


def test_three_unknown_matrix_and_boundary_elimination_by_hand():
    s, lo, diag, up, rhs, right = assemble(200.0, 50.0, 1, True)
    np.testing.assert_array_equal(s, [0, 50, 100, 150, 200])
    expected = np.array([[0.14, -0.07, 0], [-0.08, 0.31, -0.18], [0, -0.18, 0.56]])
    for basis in np.eye(3):
        np.testing.assert_allclose(action(lo, diag, up, basis), expected @ basis)
    right_by_formula = (200 / 7) * (200 / (500 / 7))**(-2.5)
    assert right == pytest.approx(right_by_formula)
    np.testing.assert_allclose(rhs, [2, 0, 0.33 * right_by_formula])


def test_two_boundary_contributions_accumulate_in_one_unknown_row():
    _, lo, diag, up, rhs, right = assemble(200.0, 100.0, 1, True)
    np.testing.assert_allclose([lo[0], diag[0], up[0]], [-0.02, 0.14, -0.07])
    assert rhs[0] == pytest.approx(2 + 0.07 * right)


@pytest.mark.parametrize("stage", [1, 2])
@pytest.mark.parametrize("h", [2.0, 1.0, 0.5])
def test_stencil_is_monotone_and_unknown_matrix_strictly_dominant(stage, h):
    _, lo, diag, up, rhs, right = assemble(400.0, h, stage)
    assert np.all(lo <= 0) and np.all(up <= 0)
    np.testing.assert_allclose(diag + lo + up, R, atol=3e-11)
    margin = diag.copy()
    margin[1:] -= np.abs(lo[1:])
    margin[:-1] -= np.abs(up[:-1])
    assert margin.min() >= R - 3e-11
    assert right == 0 and rhs[0] == pytest.approx(-lo[0] * K)
    assert np.count_nonzero(rhs[1:]) == 0


@pytest.mark.parametrize("stage", [1, 2])
def test_constant_and_affine_operator_identities_check_drift_sign(stage):
    s, lo, diag, up, _, _ = assemble(200.0, 5.0, stage)
    np.testing.assert_allclose(full_stencil(lo, diag, up, np.full_like(s, 7)), 0.35, atol=2e-12)
    c, slope = 12.0, -0.3
    expected = R * c + dividend(stage) * slope * s[1:-1]
    np.testing.assert_allclose(full_stencil(lo, diag, up, c + slope * s), expected, atol=2e-12)


@pytest.mark.parametrize("stage", [1, 2])
def test_quadratic_consistency_defect_is_first_order_at_a_fixed_node(stage):
    defects = []
    for h in [1.0, 0.5, 0.25]:
        s, lo, diag, up, _, _ = assemble(200.0, h, stage)
        x = s[1:-1]
        # Scale the quadratic to keep cancellation in the stencil terms small.
        continuous = (2 * dividend(stage) - R - volatility(x, stage)**2) * (x / 100)**2
        defect = full_stencil(lo, diag, up, (s / 100)**2) - continuous
        k = int(np.flatnonzero(x == 100)[0])
        assert defect[k] == pytest.approx(-(R - dividend(stage)) * 100 * h / 10000, abs=1e-11)
        defects.append(abs(defect[k]))
    np.testing.assert_allclose(np.array(defects[:-1]) / defects[1:], 2, rtol=1e-7)


@pytest.mark.parametrize("smax,h,stage,exact_boundary", [
    (100, 1, 1, False), (400, 0, 1, False), (400, -1, 1, False),
    (400, 300, 1, False), (400, 3, 1, False), (400, 1, 3, False),
    (400, 1, 2, True), (np.inf, 1, 1, False), (400, np.nan, 1, False),
])
def test_assembly_rejects_invalid_grids_or_boundary_modes(smax, h, stage, exact_boundary):
    with pytest.raises(ValueError):
        assemble(smax, h, stage, exact_boundary)
