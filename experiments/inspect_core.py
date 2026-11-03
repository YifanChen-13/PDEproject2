"""Inspect A's assembly without solving an incomplete boundary system."""

import argparse
import json

import numpy as np

from pde_bvp import Problem, assemble_core, build_grid
from pde_bvp.problem import exact_solution


def inspect_core(N):
    problem = Problem(N=N)
    grid = build_grid(problem)
    A, b = assemble_core(problem, grid)
    A = A.tocsr()
    sampled = exact_solution(grid.X, grid.Y)[1:N, 1:N + 1].ravel()
    defect = (A @ sampled - b)[grid.interior_rows]
    result = {
        "N": N,
        "h": problem.h,
        "unknowns": grid.n_unknowns,
        "interior_rows": len(grid.interior_rows),
        "reserved_right_rows": len(grid.right_rows),
        "nnz": A.nnz,
        "right_rows_are_zero": bool(A[grid.right_rows].nnz == 0),
        "right_rhs_is_zero": bool(np.all(b[grid.right_rows] == 0.0)),
        "interior_exact_defect_linf": float(np.max(np.abs(defect))),
        "status": "assembly only; boundary closure and solve are pending",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, default=8, help="number of grid intervals")
    inspect_core(parser.parse_args().N)
