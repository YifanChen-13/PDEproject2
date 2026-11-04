"""Inspect A's data and matrix rows without solving an LCP."""

import json

import numpy as np

from discretization import assemble
from problem import EXACT_STAR, K, volatility


def inspect(stage):
    s, lo, diag, up, rhs, right = assemble(400.0, 1.0, stage, stage == 1)
    row = int(np.flatnonzero(s[1:-1] == K)[0])
    return {
        "stage": stage,
        "intervals": len(s) - 1,
        "unknowns": len(diag),
        "row_at_S_100": [float(lo[row]), float(diag[row]), float(up[row])],
        "minimum_stencil_margin": float(np.min(diag + lo + up)),
        "nonpositive_offdiagonals": bool(np.all(lo <= 0) and np.all(up <= 0)),
        "left_rhs_contribution": float(rhs[0]),
        "right_value": right,
        "sigma_at_zero": float(volatility(0.0, stage)),
    }


if __name__ == "__main__":
    print(json.dumps({"stage1_exact_threshold": EXACT_STAR,
                      "assembly_checks": [inspect(1), inspect(2)],
                      "lcp_solve_performed": False}, indent=2))
