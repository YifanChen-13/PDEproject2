# B predictions (2026-11-05, before B solver checks)

The source is Problem Pack 5.3 (perpetual American put), not yesterday's mixed
boundary problem. A's operator is used unchanged.

1. Exhaustively enumerating contact/continuation policies on tiny grids should
   produce the same unique LCP value as policy iteration in both stages.
2. At payoff initialisation exact ties choose continuation; zero far-field values
   must not be classified as exercise. No SOR relaxation parameter is used.
3. Boundary reconstruction should exactly restore K and the selected right data.
4. Requested absolute residual tolerance must be reported independently of policy
   repetition. Very tight tolerance may terminate at a floating-point floor with
   met_requested_tol=false, or raise rather than silently claiming success.
5. Synthetic non-finite solves, repeated large defects and exhausted iterations
   must fail explicitly. Invalid tolerances and iteration budgets must be rejected.
6. Contact classification uses absolute payoff gap <= contact_tol, S<K and the
   contiguous prefix starting at zero; isolated contact nodes must be flagged.
   The adjacent-node bracket is a discrete transition bracket, not a rigorous
   enclosure of the continuous free boundary.
7. Representative h=1 solves should have small complementarity residuals and
   contiguous exercise prefixes. Formal four-level studies belong to C/D.

Append measured outcomes in handoff_B.md; do not rewrite these predictions.
