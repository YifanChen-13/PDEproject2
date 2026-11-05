# Technical audit of the current repository

This record documents AI-assisted code and numerical review of the current implementation. It is evidence for the team's course audit. Student participation and signatures require actual independent work.

## Model and stencil

`problem.py` implements the specified payoff, parameters and two volatility models. `discretization.py` assembles the monotone upwind operator and eliminates both boundary values. Foundation tests check the exact solution, hand-calculated matrix rows, off-diagonal signs, diagonal dominance and polynomial consistency. The numerical implementation uses the same assembly for both solvers.

## Policy and complementarity

`solver.py` replaces rows according to the obstacle policy and measures the actual componentwise minimum residual. Repeated policies are identified as a floating-point floor when the requested tolerance is not reached. Small-grid exhaustive active-set checks compare feasible policies with the banded policy solver. These checks share the assembled matrix and are complemented by the independent hand-row tests.

## Reproduction and independent calculations

The current checkout collects 64 A/B/D tests. Following directory integration, a complete Stage 2 rerun reproduced all 11 saved solution arrays within `rtol=1e-10, atol=1e-11`, and 50 saved-array checks passed. Stage 1 compares four grids against the analytic value and threshold.

`independent_audit.py` solves the Stage 2 free-boundary ODE by adaptive collocation with the boundary as an unknown parameter and compares with the existing independent shooting method on domains 300, 400 and 600. On the same LCP it also compares projected SOR and policy iteration at a common absolute residual target of `1e-8`. The saved CSV includes timing, iterations, residuals and differences. The timings reflect Python PSOR sweeps versus compiled banded linear solves.

## Interpretation and outstanding human work

The finest Stage 2 references terminate at the explicitly reported floating-point floor. Fine-reference sensitivity and the finite-domain bias limit precision claims. Neither a small backward residual nor a shared model transcription is an independent guarantee of the unbounded-domain price.

The five-gate course worksheet requires real student transcription checks, discussion, independent reproduction, interrogation and sign-off. The course precomputation protocol and individual contribution statements likewise require actual participants and truthful records. No such student actions are asserted by this technical audit.
