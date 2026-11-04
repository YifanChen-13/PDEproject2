# A: predictions before validation

Recorded on 2026-11-04 before running the new foundation tests. These are
AI-assisted predictions for model and assembly checks, not a student's sign-off.
No LCP solve is included in A's validation run.

1. Stage 1 has lambda = -2.5 and S* = 500/7. Value matching and the right
   derivative -1 hold at S*. The continuation formula satisfies L V = 0.
2. Stage 2 uses q = 0.02 and sigma(K) = 0.20. The volatility has the right limit
   0.13 at S = 0; evaluating that endpoint should not require log(0).
3. At S = 100, h = 1, Stage 1's (-L_h) row is
   (-200, 405.05, -205); Stage 2's row is (-200, 403.05, -203).
4. For both stages the off-diagonals are nonpositive and the complete stencil
   has diagonal-dominance margin r = 0.05. Eliminating boundary values preserves
   or increases the margin of the unknown-only matrix.
5. The first RHS contribution is -lo[0] * K. Only Stage 1 with
   exact_boundary=True uses the analytic right endpoint. Stage 2 uses zero.
6. The operator on a constant is r times that constant. On c + m*S it is
   r*c + q*m*S. This independently checks the drift sign.
7. For V = S**2 and positive drift, the forward-drift defect at a fixed node is
   -(r-q)*S*h, hence first order in h. This is a consistency check, not a
   computed option-price error or a solver residual.
8. Splitting data and assembly out of the existing solver should preserve its
   two-stage assembly arrays for the documented floating-point inputs.

Reconciliation and actual commands belong in [handoff_A.md](handoff_A.md).
The official course worksheets have not been supplied; this file does not
replace them.
