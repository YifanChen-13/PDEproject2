"""Independent free-boundary collocation and matched LCP solver comparison."""
from pathlib import Path
import argparse
import csv
import json
import time

import numpy as np
from scipy.integrate import solve_bvp

from discretization import action, assemble
from solver import solve

ROOT = Path(__file__).resolve().parent


def collocation(smax):
    """Solve on a transformed continuation interval with an unknown boundary."""
    def equation(t, y, p):
        boundary = p[0]
        s = boundary + (smax - boundary) * t
        sigma = 0.20 * (1 + 0.35 * np.tanh(np.log(s / 100) / 0.40))
        return (smax - boundary) * np.vstack((y[1], (0.05 * y[0] - 0.03 * s * y[1]) / (0.5 * sigma**2 * s**2)))

    def boundary_conditions(left, right, p):
        return np.array([left[0] - (100 - p[0]), left[1] + 1, right[0]])

    t = np.linspace(0, 1, 100)
    guess = np.vstack((30 * (1 - t), -0.05 * np.ones_like(t)))
    result = solve_bvp(equation, boundary_conditions, t, guess, p=[69.0], tol=1e-9, max_nodes=20000)
    if not result.success:
        raise RuntimeError(result.message)
    boundary = float(result.p[0])
    price = float(result.sol((100 - boundary) / (smax - boundary))[0])
    return boundary, price


def projected_sor(smax, h, tol=1e-8, omega=1.2, max_iterations=200000):
    """Projected SOR using the same assembled LCP and payoff initial value."""
    start = time.perf_counter()
    s, lower, diagonal, upper, rhs, right = assemble(smax, h, 2)
    payoff = np.maximum(100 - s[1:-1], 0)
    value = payoff.copy()
    for iteration in range(1, max_iterations + 1):
        for i in range(len(value)):
            left = lower[i] * value[i - 1] if i > 0 else 0.0
            next_value = upper[i] * value[i + 1] if i + 1 < len(value) else 0.0
            update = (rhs[i] - left - next_value) / diagonal[i]
            value[i] = max(payoff[i], value[i] + omega * (update - value[i]))
        residual = float(np.max(np.abs(np.minimum(action(lower, diagonal, upper, value) - rhs, value - payoff))))
        if residual <= tol:
            return np.r_[100.0, value, right], iteration, time.perf_counter() - start, residual
    raise RuntimeError(f'PSOR did not meet residual tolerance {tol:g}; residual={residual:g}')


def main():
    from solver import continuous_reference

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'results' / 'independent_audit')
    out = parser.parse_args().output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    references = []
    for smax in (300, 400, 600):
        boundary, price = collocation(smax)
        shooting_boundary, shooting_value = continuous_reference(smax, 2)
        shooting_price = float(shooting_value(np.array([100.0]))[0])
        assert abs(boundary - shooting_boundary) < 1e-6
        assert abs(price - shooting_price) < 1e-6
        references.append(dict(smax=smax, boundary=boundary, value_100=price,
                               shooting_boundary=shooting_boundary, shooting_value_100=shooting_price))
    comparisons = []
    _, reference_value = continuous_reference(600, 2)
    for h in (5.0, 2.5):
        grid, policy, stats = solve(smax=600, h=h, stage=2, tol=1e-8)
        psor, iterations, seconds, residual = projected_sor(600, h)
        difference = float(np.max(np.abs(policy - psor)))
        assert stats['met_requested_tol'] and difference < 1e-5
        error_vs_ode = float(np.max(np.abs(policy - reference_value(grid))))
        comparisons.append(dict(h=h, unknowns=len(policy)-2, tolerance=1e-8, omega=1.2,
                                value_error_vs_ode=error_vs_ode,
                                policy_iterations=stats['iterations'], policy_seconds=stats['seconds'],
                                policy_residual=stats['lcp_residual'], psor_iterations=iterations,
                                psor_seconds=seconds, psor_residual=residual, max_difference=difference))
    (out / 'collocation.json').write_text(json.dumps(references, indent=2) + '\n')
    with (out / 'solver_comparison.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(comparisons[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(comparisons)
    print(json.dumps(dict(collocation=references, solver_comparison=comparisons), indent=2))


if __name__ == '__main__':
    main()
