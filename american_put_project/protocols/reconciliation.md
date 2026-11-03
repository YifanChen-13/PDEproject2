# Prediction / observation reconciliation

1. Expected first-order upwind price convergence: confirmed by Stage 1 exact
   errors and Stage 2 independent ODE errors. Fine-grid-reference pairwise rates
   exceed one slightly because the reference retains its own first-order bias.
2. Expected grid-quantised threshold error: confirmed. Stage 1 boundary error
   increases on the first refinement before falling; no monotone boundary-error
   claim is made. Repeated threshold nodes are not a convergence certificate.
3. Expected monotone, convex, bounded values with one contact interval: automated
   checks pass within 1e-6 absolute finite-difference tolerance. Raw defects remain
   in all_diagnostics.csv. This absolute tolerance is not a bound on gamma error.
4. Expected larger-domain higher prices and lower thresholds: confirmed. The
   domain sensitivity exceeds the finest study mesh error, so truncation is not
   negligible at Smax=600. Independent ODE domain extension strengthens this finding.
5. Expected a possible roundoff residual floor: observed at the tightest requested
   tolerance. The repeated-policy stop is explicitly flagged; actual residuals and
   met_requested_tol are reported. No unachieved tolerance is labelled achieved.
6. Expected tolerance-insensitive prices: confirmed by identical recorded vectors
   in the representative stopping-tolerance sweep. Combined with independent ODE
   agreement, this separates algebraic from discretisation error on study grids.
7. Expected agreement with independent fixed-domain ODE solution: confirmed under
   mesh refinement. ODE shooting is an independent method, not an exact reference
   or a rigorous bound on infinite-domain truncation error.
