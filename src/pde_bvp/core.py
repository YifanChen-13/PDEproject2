"""Interior five-point rows with Dirichlet values eliminated."""

import numpy as np
from scipy.sparse import lil_matrix

from .grid import Grid
from .problem import Problem, dirichlet_data, source


def assemble_core(problem: Problem, grid: Grid):
    """Return mutable LIL A and b; open-right-edge rows remain zero."""
    if problem.N != grid.N:
        raise ValueError("problem and grid must use the same N.")
    N = problem.N
    inv_h2 = 1.0 / problem.h**2
    A = lil_matrix((grid.n_unknowns, grid.n_unknowns), dtype=float)
    b = np.zeros(grid.n_unknowns)

    for j in range(1, N):
        for i in range(1, N):
            k = grid.index_map[j, i]
            A[k, k] = 4.0 * inv_h2
            b[k] = source(grid.x[i], grid.y[j])
            for ni, nj in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
                neighbour = grid.index_map[nj, ni]
                if neighbour >= 0:
                    A[k, neighbour] = -inv_h2
                else:
                    b[k] += inv_h2 * dirichlet_data(grid.x[ni], grid.y[nj])

    return A, b
