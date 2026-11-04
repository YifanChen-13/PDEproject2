# Predictions written before the first solver run

The supplied problem pack requires predictions before each new solve. The run driver
records a timestamped prediction immediately before every solve, using these rules.

1. Stage 1: S*=500/7=71.4285714286. Upwind drift is first order, so global value
   convergence is expected to approach order one. No second-order claim is made.
2. The exercise boundary is recorded as the last contiguous contact node, without
   interpolation. Quantisation and discretisation both affect its error; pairwise
   boundary-error rates may oscillate and need not be one at each refinement.
3. Stage 2: the value should decrease with S and be convex, lie between payoff
   and K, and have one contact interval. These are hypotheses to test.
4. Enlarging the zero-Dirichlet upper boundary should increase the value in the
   common domain and lower the exercise threshold. A fixed-h domain study measures
   sensitivity, not a proof of negligible infinite-domain truncation error.
5. The LCP has nonpositive off-diagonal matrix entries and strict row dominance
   margin r. Nonlinear complementarity residuals should be small, while large
   fine-grid coefficients may impose a floating-point residual floor.
6. Tighter tolerance should eventually stop changing prices and the contact node.
7. An independent ODE shooting reference should agree with the FDM limit on the
   same truncated domain. It is separate from the required fine-grid reference.

Protocol limitation: the exact course precomputation and five-gate worksheet files
were not provided. The included audit is a documented substitute, not a claim that
the official worksheets or student sign-off have been completed.
