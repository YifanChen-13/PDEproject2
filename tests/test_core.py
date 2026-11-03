import numpy as np
import pytest
from scipy.sparse import isspmatrix_lil

from pde_bvp import Problem, assemble_core, build_grid
from pde_bvp.problem import exact_solution


def test_hand_calculated_two_interval_system():
    problem = Problem(2)
    A, b = assemble_core(problem, build_grid(problem))
    # Unknowns: (1/2,1/2), (1,1/2). The other three neighbours are known.
    np.testing.assert_array_equal(A.toarray(), [[16.0, -4.0], [0.0, 0.0]])
    expected = -2 * np.e + 4 * (2 * np.exp(0.5) + np.exp(1.5))
    np.testing.assert_allclose(b, [expected, 0.0])


def test_unscaled_interior_row_has_the_five_expected_entries():
    A, b = assemble_core(Problem(4), build_grid(Problem(4)))
    row = A.getrow(5).toarray().ravel()  # node (i,j)=(2,2)
    np.testing.assert_array_equal(np.flatnonzero(row), [1, 4, 5, 6, 9])
    np.testing.assert_array_equal(row[[1, 4, 5, 6, 9]], [-16, -16, 64, -16, -16])
    assert b[5] == pytest.approx(-2 * np.e)


def test_right_neighbour_is_retained_and_top_data_moves_to_rhs():
    A, b = assemble_core(Problem(4), build_grid(Problem(4)))
    # Node (3/4,3/4) couples to the open right edge, not to a known exact value.
    row = A.getrow(10).toarray().ravel()
    np.testing.assert_array_equal(np.flatnonzero(row), [6, 9, 10, 11])
    np.testing.assert_array_equal(row[[6, 9, 10, 11]], [-16, -16, 64, -16])
    assert b[10] == pytest.approx(-2 * np.exp(1.5) + 16 * np.exp(1.75))


@pytest.mark.parametrize("N", [2, 3, 8, 32])
@pytest.mark.parametrize("bc_type", ["neumann", "robin"])
def test_core_reserves_every_right_row_and_has_correct_signs(N, bc_type):
    problem = Problem(N, bc_type)
    grid = build_grid(problem)
    A, b = assemble_core(problem, grid)
    assert isspmatrix_lil(A)
    assert A.shape == (N * (N - 1),) * 2
    csr = A.tocsr()
    assert csr[grid.right_rows].nnz == 0
    np.testing.assert_array_equal(b[grid.right_rows], 0.0)
    np.testing.assert_array_equal(csr.diagonal()[grid.interior_rows], 4 * N**2)
    coo = csr.tocoo()
    assert np.all(coo.data[coo.row != coo.col] == -N**2)


def test_core_is_identical_before_either_boundary_variant():
    neumann = Problem(8, "neumann")
    robin = Problem(8, "robin")
    A_n, b_n = assemble_core(neumann, build_grid(neumann))
    A_r, b_r = assemble_core(robin, build_grid(robin))
    assert (A_n.tocsr() != A_r.tocsr()).nnz == 0
    np.testing.assert_array_equal(b_n, b_r)


def test_exact_samples_match_independent_stencil_defect_and_second_order():
    errors = []
    for N in [8, 16, 32]:
        problem = Problem(N)
        grid = build_grid(problem)
        A, b = assemble_core(problem, grid)
        sampled = exact_solution(grid.X, grid.Y)[1:N, 1:N + 1].ravel()
        defect = (A.tocsr() @ sampled - b)[grid.interior_rows]
        exact_interior = np.exp(grid.X[1:N, 1:N] + grid.Y[1:N, 1:N]).ravel()
        # -Delta_h exp(x+y) = -8 exp(x+y) sinh(h/2)^2 / h^2.
        factor = 2 - 8 * (np.sinh(problem.h / 2) / problem.h)**2
        np.testing.assert_allclose(defect, factor * exact_interior, rtol=1e-7, atol=1e-11)
        errors.append(np.max(np.abs(defect / exact_interior)))
    orders = np.log2(np.array(errors[:-1]) / errors[1:])
    np.testing.assert_allclose(orders, 2.0, atol=0.01)


def test_inconsistent_grid_is_rejected():
    with pytest.raises(ValueError):
        assemble_core(Problem(4), build_grid(Problem(8)))
