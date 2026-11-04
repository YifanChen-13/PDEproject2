"""Member B: first-order Neumann and Robin boundary rows."""

from .problem import neumann_data, robin_data


def apply_first_order(A, b, problem, grid):
    """Fill grid.right_rows in place and return (A, b); see docs/interfaces.md."""
    if problem.N != grid.N:
        raise ValueError("problem and grid must use the same N.")
    inv_h = 1.0 / problem.h
    beta = problem.beta if problem.bc_type == "robin" else 0.0
    data = robin_data if problem.bc_type == "robin" else neumann_data
    for j in range(1, problem.N):
        k = grid.index_map[j, problem.N]
        west = grid.index_map[j, problem.N - 1]
        # Replace the whole row: reapplication must not accumulate data or
        # leave PDE/ghost couplings behind. Corners are never visited.
        A.rows[k] = [int(west), int(k)]
        A.data[k] = [-inv_h, inv_h + beta]
        b[k] = data(grid.y[j])
    return A, b
