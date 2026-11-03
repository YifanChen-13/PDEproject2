"""Manufactured data from Direction 2 of the course problem pack."""

from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass(frozen=True)
class Problem:
    N: int
    bc_type: Literal["neumann", "robin"] = "neumann"

    def __post_init__(self):
        if isinstance(self.N, bool) or not isinstance(self.N, int) or self.N < 2:
            raise ValueError("N must be an integer >= 2 (number of intervals).")
        if self.bc_type not in ("neumann", "robin"):
            raise ValueError("bc_type must be 'neumann' or 'robin'.")

    @property
    def h(self):
        return 1.0 / self.N

    @property
    def beta(self):
        return 2.0


def exact_solution(x, y):
    return np.exp(x + y)


def source(x, y):
    return -2.0 * np.exp(x + y)


def dirichlet_data(x, y):
    return np.exp(x + y)


def neumann_data(y):
    return np.exp(1.0 + y)


def robin_data(y):
    return 3.0 * np.exp(1.0 + y)
