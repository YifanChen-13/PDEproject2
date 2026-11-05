# B: LCP policy iteration and exercise threshold

For A's unchanged unknown-only operator A=-L_h, solve
`min(a,gap)=0`, where `a=A*v-rhs`, `gap=v-psi`. Both quantities must be
nonnegative and at least one must vanish at each interior node.

Start at `v=psi`. Choose exercise if `gap<a`, otherwise continuation, including
exact ties. Exercise replaces the corresponding row by `v_i=psi_i`;
continuation keeps A's row and rhs. At the initial zero tail, continuation ties
avoid propagating continuation only one node per iteration. This is policy
iteration, with no SOR relaxation parameter.

The banded storage is `ab[1,i]=diagonal_i`, `ab[0,i+1]=upper_i`,
`ab[2,i-1]=lower_i`. Zero off-diagonal entries according to the **row** policy,
not the column policy; use A's endpoint-eliminated rhs unchanged. Reconstruct
the full vector as `[K, v, right]`.

After every solve recompute the absolute complementarity residual
`max(abs(min(A*v-rhs,v-psi)))`. Only residual<=tol sets met_requested_tol=true.
Repeat policies can expose round-off: allow termination only if the defect is
below `100*eps*max(1,max(|diag*v|+|rhs|+neighbor products),max(|v|))`.
Record termination_reason=floating_point_floor and met_requested_tol=false.
This scale-dependent heuristic replaces the prototype's fixed 2e-5 allowance;
it is neither a guaranteed forward-error bound nor successful requested-tolerance
convergence. A repeated larger defect or exhausted maxiter raises RuntimeError.
Non-finite solutions and invalid numerical controls are explicitly rejected.

The reported scaled_backward_residual uses the final policy matrix row norm
times ||v||inf plus |policy rhs| (denominator clipped below at 1). It measures
linear policy-system backward error, separately from the unscaled LCP residual,
discretisation error and conditioning. Nonnegativity minima are also reported.

Classify contact with `abs(V-psi)<=contact_tol`, S<K, excluding the artificial
far endpoint. Starting from zero, return the last node in the contiguous contact
prefix. Report star=S[k], star_upper=S[k+1], contact_tol and contiguous; no
interpolation is used. The bracket locates the discrete transition only, and
does not certify enclosure of the continuous threshold. An isolated later
contact node flags contiguous=false. Large contact tolerances bias the threshold.
The smooth-fit probe is the first continuation forward slope plus one; if two
continuation nodes are unavailable its diagnostic is NaN rather than indexing
beyond the vector.

Independent checks enumerate every policy on one-, three- and seven-unknown
grids using dense matrices and numpy.linalg.solve, then retain only solutions
satisfying both inequalities and complementarity. This oracle shares A's
assembly but not policy iteration or banded storage. A's hand-row tests remain
the independent check on assembly. Both stages and both Stage 1 endpoint choices
are covered. Formal four-mesh price/threshold experiments belong to C/D;
independent review of B belongs to E and matrix integration review to A.
