import numpy as np
import pytest

from pde_bvp import Problem, build_grid
from pde_bvp.problem import (
    dirichlet_data,
    exact_solution,
    neumann_data,
    robin_data,
    source,
)


@pytest.mark.parametrize("N", [True, 1, 0, -2, 2.5])
def test_invalid_interval_count(N):
    with pytest.raises(ValueError):
        Problem(N)


def test_invalid_boundary_type():
    with pytest.raises(ValueError):
        Problem(4, "dirichlet")


def test_manufactured_data_and_outward_normal():
    x, y = 0.25, np.array([0.0, 0.5, 1.0])
    np.testing.assert_allclose(exact_solution(x, y), np.exp(x + y))
    np.testing.assert_allclose(source(x, y), -2 * np.exp(x + y))
    np.testing.assert_allclose(dirichlet_data(x, y), np.exp(x + y))
    np.testing.assert_allclose(neumann_data(y), np.exp(1 + y))
    assert np.all(neumann_data(y) > 0)
    np.testing.assert_allclose(
        robin_data(y), neumann_data(y) + Problem(4, "robin").beta * np.exp(1 + y)
    )


@pytest.mark.parametrize("N", [2, 3, 8, 32])
def test_grid_coordinates_indexing_and_corner_ownership(N):
    grid = build_grid(Problem(N))
    assert grid.X.shape == grid.Y.shape == (N + 1, N + 1)
    np.testing.assert_allclose(grid.X[0, :], np.linspace(0, 1, N + 1))
    np.testing.assert_allclose(grid.Y[:, 0], np.linspace(0, 1, N + 1))
    assert grid.n_unknowns == N * (N - 1)
    assert len(grid.interior_rows) == (N - 1)**2
    assert len(grid.right_rows) == N - 1
    assert grid.index_map[1, 1] == 0
    assert grid.index_map[1, N] == N - 1
    assert grid.index_map[N - 1, N] == N * (N - 1) - 1
    assert np.all(grid.index_map[:, 0] == -1)
    assert np.all(grid.index_map[0, :] == -1)
    assert np.all(grid.index_map[N, :] == -1)
    np.testing.assert_array_equal(grid.right_rows, np.arange(N - 1, N * (N - 1), N))
    all_rows = np.concatenate((grid.interior_rows, grid.right_rows))
    np.testing.assert_array_equal(np.sort(all_rows), np.arange(grid.n_unknowns))


def test_to_nodal_preserves_vector_and_dirichlet_edges():
    grid = build_grid(Problem(4))
    values = np.arange(grid.n_unknowns, dtype=float) - 100
    U = grid.to_nodal(values)
    np.testing.assert_array_equal(U[1:4, 1:5].ravel(), values)
    np.testing.assert_allclose(U[:, 0], np.exp(grid.y))
    np.testing.assert_allclose(U[0, :], np.exp(grid.x))
    np.testing.assert_allclose(U[4, :], np.exp(grid.x + 1))


def test_to_nodal_rejects_wrong_vector_shape():
    grid = build_grid(Problem(4))
    with pytest.raises(ValueError):
        grid.to_nodal(np.zeros((3, 4)))
