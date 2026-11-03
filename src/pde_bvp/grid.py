"""Nodal arrays use [j, i]; unknown vectors use x as the fast index."""

from dataclasses import dataclass

import numpy as np

from .problem import Problem, dirichlet_data


@dataclass(frozen=True)
class Grid:
    N: int
    x: np.ndarray
    y: np.ndarray
    X: np.ndarray
    Y: np.ndarray
    index_map: np.ndarray

    @property
    def h(self):
        return 1.0 / self.N

    @property
    def n_unknowns(self):
        return self.N * (self.N - 1)

    @property
    def dirichlet_mask(self):
        return self.index_map < 0

    @property
    def interior_rows(self):
        return self.index_map[1:self.N, 1:self.N].ravel()

    @property
    def right_rows(self):
        return self.index_map[1:self.N, self.N].copy()

    def to_nodal(self, unknown_values):
        """Restore a full U[j, i] array, including known Dirichlet values."""
        values = np.asarray(unknown_values)
        if values.shape != (self.n_unknowns,):
            raise ValueError(f"Expected a vector of length {self.n_unknowns}.")
        U = np.zeros_like(self.X)
        mask = self.dirichlet_mask
        U[mask] = dirichlet_data(self.X[mask], self.Y[mask])
        U[1:self.N, 1:self.N + 1] = values.reshape(self.N - 1, self.N)
        return U


def build_grid(problem: Problem) -> Grid:
    N = problem.N
    x = np.linspace(0.0, 1.0, N + 1)
    y = np.linspace(0.0, 1.0, N + 1)
    X, Y = np.meshgrid(x, y, indexing="xy")
    index_map = np.full((N + 1, N + 1), -1, dtype=int)
    index_map[1:N, 1:N + 1] = np.arange(N * (N - 1)).reshape(N - 1, N)
    return Grid(N, x, y, X, Y, index_map)
