"""Monotone upwind assembly of -L; unknowns are the interior asset nodes."""

import numpy as np

from problem import K, R, dividend, exact, volatility


def assemble(smax, h, stage, exact_boundary=False):
    """Return (S, lo, diag, up, rhs, right_value).

    lo[0] and up[-1] retain the eliminated boundary coefficients.
    The LCP is min(A*v - rhs, v - payoff(S[1:-1])) = 0.
    """
    q = dividend(stage)
    if not np.isfinite(smax) or smax <= K:
        raise ValueError("smax must be finite and greater than K")
    if not np.isfinite(h) or h <= 0 or h > smax / 2:
        raise ValueError("h must be positive and give at least two intervals")
    n = round(smax / h)
    if not np.isclose(n * h, smax, rtol=1e-12, atol=1e-12):
        raise ValueError("smax / h must be an integer")
    if exact_boundary and stage != 1:
        raise ValueError("The analytic right boundary is only available in Stage 1")

    s = np.linspace(0.0, smax, n + 1)
    x = s[1:-1]
    diffusion = 0.5 * volatility(x, stage)**2 * x * x
    drift = (R - q) * x
    lo = -diffusion / h**2 - np.maximum(-drift, 0) / h
    up = -diffusion / h**2 - np.maximum(drift, 0) / h
    diag = 2 * diffusion / h**2 + np.abs(drift) / h + R

    right = float(exact(smax)) if exact_boundary else 0.0
    rhs = np.zeros(n - 1)
    rhs[0] -= lo[0] * K
    rhs[-1] -= up[-1] * right
    return s, lo, diag, up, rhs, right


def action(lo, diag, up, v):
    """Apply the unknown-only tridiagonal matrix without boundary terms."""
    result = diag * v
    result[1:] += lo[1:] * v[:-1]
    result[:-1] += up[:-1] * v[1:]
    return result
