"""Shared grid and assembly for the mixed-boundary Poisson project."""

from .core import assemble_core
from .grid import Grid, build_grid
from .problem import Problem

__all__ = ["Problem", "Grid", "build_grid", "assemble_core"]
