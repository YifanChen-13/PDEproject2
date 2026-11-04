# B: predictions before numerical checks

Recorded 2026-11-04 before running B's tests or solves.

- Both closures replace only the open right-edge rows. Neumann has coefficients
  (-N, N); Robin has (-N, N+2), with positive q or r on the RHS.
- N=2 has boundary row [-2, 2] or [-2, 4]. N=4 rows 3,7,11 couple
  only to columns (2,3), (6,7), (10,11), respectively.
- For exact exponential samples, both variants have the identical defect
  exp(1+y) * ((1-exp(-h))/h - 1), negative and asymptotically -h*exp(1+y)/2.
  At fixed y=1/2 its magnitude should approximately halve on refinement.
- A linear function in x satisfies the backward derivative exactly; this
  gives a separate sign/scaling check without truncation error.
- Small integration solves should retain exact Dirichlet corners and show
  decreasing global and open-right-edge errors, plausibly approaching order 1.
  Componentwise backward residual should be near floating point precision.
- These are predictions, not measured results. Formal four-case convergence
  experiments belong to D/E. Course audit and C's independent review remain pending.
