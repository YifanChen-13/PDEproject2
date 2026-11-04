"""Fixed model data from Problem Pack, open direction 5.3."""

import numpy as np

K, R, SIGMA = 100.0, 0.05, 0.20
EXACT_LAMBDA = -2.5
EXACT_STAR = K * EXACT_LAMBDA / (EXACT_LAMBDA - 1)


def _prices(s):
    s = np.asarray(s, dtype=float)
    if np.any(~np.isfinite(s)) or np.any(s < 0):
        raise ValueError("Asset prices must be finite and nonnegative")
    return s


def dividend(stage):
    if stage not in (1, 2):
        raise ValueError("stage must be 1 or 2")
    return 0.0 if stage == 1 else 0.02


def payoff(s):
    return np.maximum(K - _prices(s), 0.0)


def exact(s):
    """Stage 1 infinite-domain value; accepts scalars and arrays."""
    s = _prices(s)
    tail = (K - EXACT_STAR) * (np.maximum(s, EXACT_STAR) / EXACT_STAR)**EXACT_LAMBDA
    return np.where(s <= EXACT_STAR, K - s, tail)


def volatility(s, stage):
    """At S=0, Stage 2 uses the right limit 0.13."""
    dividend(stage)
    s = _prices(s)
    if stage == 1:
        return np.full_like(s, SIGMA)
    log_ratio = np.full_like(s, -np.inf)
    np.log(s / K, out=log_ratio, where=s > 0)
    return SIGMA * (1 + 0.35 * np.tanh(log_ratio / 0.40))
