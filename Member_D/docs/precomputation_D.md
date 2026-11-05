# D: predictions before the Stage 2 experiments

Recorded 2026-11-05 before running stage2_studies.py. Source baseline:
YifanChen-13/PDEproject2, main commit 489f549136502ff37e57a71cf2c73292f007ace3.

1. With q=0.02 and the prescribed local volatility, the obstacle solution
   should lie between payoff and K, decrease, remain convex, and have one
   contiguous contact interval. Small floating-point violations are possible.
2. At Smax=600, h=0.5,0.25,0.125,0.0625 should approach the same truncated-domain
   solution. The drift discretisation suggests approximately first-order value
   convergence, but measured reference-based orders may be biased by the finite
   reference mesh. The contact-node threshold is quantised, so its observed
   orders need not be smooth or first order.
3. References h=1/128 and 1/256 should differ less than the four-level study
   errors. Their difference estimates reference sensitivity; it is not a
   rigorous bound. First-order Richardson correction can be a diagnostic only.
4. At fixed h=0.0625, enlarging Smax=300,400,600 should raise values on [0,300]
   and weakly lower the last contact node. Report [0,200] as an additional
   interior comparison because S=300 is the artificial endpoint in one case.
   The Smax=600 solution is a comparison baseline, not a certified infinite-
   domain solution.
5. Finer meshes should require more iterations and more work. A strict absolute
   residual tolerance can reach the floating-point cancellation floor; record
   that status explicitly rather than silently relaxing the tolerance.
6. Tightening the requested tolerance on the h=0.0625 study grid and on the
   finest reference should change values much less than mesh/reference changes.
   A scaled backward residual is distinct from value error.

Each call also appends its settings and predictions to a new run's JSONL log
before solving, followed by a separate outcome record. No old protocol record
is edited. This is an AI-assisted preparation and execution record, not the
official course worksheet, independent C/E review, or human audit sign-off.
